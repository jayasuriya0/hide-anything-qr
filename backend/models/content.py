import gridfs
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class Content:
    _indexes_created = False
    
    def __init__(self, db):
        self.collection = db.shared_content
        self.fs = gridfs.GridFS(db)
        if not Content._indexes_created:
            self.create_indexes()
            Content._indexes_created = True
    
    def create_indexes(self):
        try:
            indexes = [
                IndexModel([('sender_id', ASCENDING)]),
                IndexModel([('receiver_id', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
                IndexModel([('expires_at', ASCENDING)], expireAfterSeconds=0),
            ]
            self.collection.create_indexes(indexes)
        except Exception as e:
            print(f"[WARNING] Failed to create Content indexes: {e}")
    
    def share_content(self, sender_id, receiver_id, encrypted_data, metadata, 
                     encrypted_key, expires_in=None):
        content = {
            'sender_id': ObjectId(sender_id),
            'receiver_id': ObjectId(receiver_id),
            'encrypted_data': encrypted_data,  # For text, this is the encrypted text
            'encrypted_key': encrypted_key,
            'metadata': metadata,
            'viewed': False,
            'view_count': 0,
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
            'expires_at': None
        }
        
        if expires_in:
            from datetime import timedelta
            content['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        
        # If it's a file, store in GridFS
        if metadata.get('type') == 'file':
            # Ensure encrypted_data is bytes for GridFS
            if isinstance(encrypted_data, str):
                encrypted_data_bytes = encrypted_data.encode('utf-8')
            else:
                encrypted_data_bytes = encrypted_data
                
            file_id = self.fs.put(
                encrypted_data_bytes,
                filename=metadata['filename'],
                content_type=metadata['content_type'],
                metadata={
                    'sender_id': str(sender_id),
                    'receiver_id': str(receiver_id) if receiver_id else None
                }
            )
            content['file_id'] = file_id
            content['encrypted_data'] = str(file_id)  # Store file ID instead of data
        
        result = self.collection.insert_one(content)
        return str(result.inserted_id), content
    
    def get_content_for_user(self, user_id, content_type=None):
        query = {'receiver_id': ObjectId(user_id)}
        if content_type:
            query['metadata.type'] = content_type
        
        contents = self.collection.find(query).sort('created_at', -1).limit(50)
        
        result = []
        for content in contents:
            result.append({
                'content_id': str(content['_id']),
                'sender_id': str(content['sender_id']),
                'encrypted_data': content['encrypted_data'],
                'encrypted_key': content['encrypted_key'],
                'metadata': content['metadata'],
                'viewed': content['viewed'],
                'created_at': content['created_at'],
                'has_file': 'file_id' in content
            })
        
        return result
    
    def mark_as_viewed(self, content_id):
        self.collection.update_one(
            {'_id': ObjectId(content_id)},
            {
                '$set': {'viewed': True}, 
                '$inc': {
                    'view_count': 1,
                    'metadata.views': 1  # Increment views in metadata for view limit tracking
                }
            }
        )
    
    def get_file(self, file_id):
        try:
            return self.fs.get(ObjectId(file_id))
        except:
            return None
    
    def get_shared_by_user(self, user_id):
        """Get all content shared by a user"""
        query = {'sender_id': ObjectId(user_id)}
        contents = self.collection.find(query).sort('created_at', -1)
        
        result = []
        for content in contents:
            result.append({
                'content_id': str(content['_id']),
                'receiver_id': str(content['receiver_id']) if content.get('receiver_id') else None,
                'metadata': content['metadata'],
                'viewed': content.get('viewed', False),
                'view_count': content.get('view_count', 0),
                'is_active': content.get('is_active', True),
                'created_at': content['created_at'],
                'expires_at': content.get('expires_at'),
                'has_file': 'file_id' in content
            })
        
        return result
    
    def deactivate_content(self, content_id, user_id):
        """Deactivate a shared content"""
        result = self.collection.update_one(
            {'_id': ObjectId(content_id), 'sender_id': ObjectId(user_id)},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0
    
    def activate_content(self, content_id, user_id):
        """Activate a shared content"""
        result = self.collection.update_one(
            {'_id': ObjectId(content_id), 'sender_id': ObjectId(user_id)},
            {'$set': {'is_active': True}}
        )
        return result.modified_count > 0
    
    def get_by_id(self, content_id):
        """Get content by ID"""
        try:
            content = self.collection.find_one({'_id': ObjectId(content_id)})
            return content
        except Exception as e:
            print(f"Error getting content by ID: {e}")
            return None
    
    def delete_content(self, content_id):
        """Delete content permanently"""
        try:
            # Get content first to check if it has a file
            content = self.collection.find_one({'_id': ObjectId(content_id)})
            
            if not content:
                return False
            
            # If it has a file in GridFS, delete it
            if 'file_id' in content:
                try:
                    self.fs.delete(content['file_id'])
                except Exception as e:
                    print(f"Error deleting file from GridFS: {e}")
            
            # Delete the content document
            result = self.collection.delete_one({'_id': ObjectId(content_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting content: {e}")
            return False
import gridfs
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING
import hashlib
from enum import Enum

class FileErrorCode(Enum):
    """File operation error codes"""
    CHUNK_MISSING = 'CHUNK_MISSING'
    CORRUPTION_DETECTED = 'CORRUPTION_DETECTED'
    EMPTY_FILE = 'EMPTY_FILE'
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'
    READ_FAILED = 'READ_FAILED'
    WRITE_FAILED = 'WRITE_FAILED'
    UPLOAD_TIMEOUT = 'UPLOAD_TIMEOUT'
    INVALID_HASH = 'INVALID_HASH'

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
            db = self.collection.database
            indexes = [
                IndexModel([('sender_id', ASCENDING)]),
                IndexModel([('receiver_id', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
                IndexModel([('expires_at', ASCENDING)], expireAfterSeconds=0),
            ]
            self.collection.create_indexes(indexes)
            
            # Create upload sessions collection indexes
            upload_sessions = db.upload_sessions
            upload_sessions.create_indexes([
                IndexModel([('expires_at', ASCENDING)], expireAfterSeconds=0),
                IndexModel([('user_id', ASCENDING)]),
                IndexModel([('status', ASCENDING)]),
            ])
        except Exception as e:
            print(f"[WARNING] Failed to create Content indexes: {e}")
    
    def share_content(self, sender_id, receiver_id, encrypted_data, metadata, 
                     encrypted_key, expires_in=None, file_hash=None, upload_session_id=None):
        """Share content with hash verification and error handling"""
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
            'expires_at': None,
            'upload_verified': False
        }
        
        if expires_in:
            content['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        
        # If it's a file, store in GridFS with error handling
        if metadata.get('type') == 'file':
            # Ensure encrypted_data is bytes for GridFS
            if isinstance(encrypted_data, str):
                encrypted_data_bytes = encrypted_data.encode('utf-8')
            else:
                encrypted_data_bytes = encrypted_data
            
            try:
                # Store file in GridFS
                file_id = self.fs.put(
                    encrypted_data_bytes,
                    filename=metadata['filename'],
                    content_type=metadata['content_type'],
                    metadata={
                        'sender_id': str(sender_id),
                        'receiver_id': str(receiver_id) if receiver_id else None,
                        'upload_session_id': upload_session_id,
                        'file_hash': file_hash,
                        'uploaded_at': datetime.now(timezone.utc).isoformat()
                    }
                )
                
                # Verify stored file integrity
                if file_hash:
                    verification = self._verify_file_integrity(file_id, file_hash)
                    if not verification['valid']:
                        # Cleanup corrupted file
                        try:
                            self.fs.delete(file_id)
                        except:
                            pass
                        return None, {
                            'status': 'error',
                            'code': FileErrorCode.CORRUPTION_DETECTED.value,
                            'message': f"File corruption detected: {verification['message']}"
                        }
                    content['upload_verified'] = True
                
                content['file_id'] = file_id
                content['encrypted_data'] = str(file_id)  # Store file ID instead of data
                
            except Exception as e:
                print(f"[ERROR] GridFS upload failed: {e}")
                return None, {
                    'status': 'error',
                    'code': FileErrorCode.WRITE_FAILED.value,
                    'message': f'Failed to store file: {str(e)}'
                }
        
        try:
            result = self.collection.insert_one(content)
            return str(result.inserted_id), {'status': 'success', 'content': content}
        except Exception as e:
            print(f"[ERROR] Failed to insert content document: {e}")
            # Cleanup file if document insert fails
            if metadata.get('type') == 'file' and 'file_id' in content:
                try:
                    self.fs.delete(content['file_id'])
                except:
                    pass
            return None, {
                'status': 'error',
                'code': FileErrorCode.WRITE_FAILED.value,
                'message': f'Failed to save content: {str(e)}'
            }
    
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
        """Get file with proper error handling"""
        try:
            grid_file = self.fs.get(ObjectId(file_id))
            if grid_file is None:
                return None, {
                    'status': 'error',
                    'code': FileErrorCode.FILE_NOT_FOUND.value,
                    'message': 'File does not exist'
                }
            return grid_file, None
        except Exception as e:
            print(f"[ERROR] Failed to retrieve file {file_id}: {e}")
            return None, {
                'status': 'error',
                'code': FileErrorCode.FILE_NOT_FOUND.value,
                'message': f'File retrieval failed: {str(e)}'
            }
    
    def read_file_with_verification(self, file_id):
        """Read file with error detection and specific error codes"""
        try:
            grid_file = self.fs.get(ObjectId(file_id))
            if grid_file is None:
                return None, {
                    'status': 'error',
                    'code': FileErrorCode.FILE_NOT_FOUND.value,
                    'message': 'File does not exist in database'
                }
            
            try:
                file_data = grid_file.read()
                
                if not file_data or len(file_data) == 0:
                    return None, {
                        'status': 'error',
                        'code': FileErrorCode.EMPTY_FILE.value,
                        'message': 'File is empty or corrupted'
                    }
                
                return file_data, None
            
            except EOFError as e:
                return None, {
                    'status': 'error',
                    'code': FileErrorCode.CHUNK_MISSING.value,
                    'message': 'File chunks incomplete - missing data mid-stream. Upload may have been interrupted.'
                }
            
            except Exception as e:
                print(f"[ERROR] Failed to read file data: {e}")
                return None, {
                    'status': 'error',
                    'code': FileErrorCode.READ_FAILED.value,
                    'message': f'Failed to read file: {str(e)}'
                }
        except Exception as e:
            print(f"[ERROR] File retrieval failed: {e}")
            return None, {
                'status': 'error',
                'code': FileErrorCode.FILE_NOT_FOUND.value,
                'message': f'Could not access file: {str(e)}'
            }
    
    def _verify_file_integrity(self, file_id, expected_hash):
        """Verify file hash matches expected value"""
        try:
            grid_file = self.fs.get(ObjectId(file_id))
            file_data = grid_file.read()
            
            # Calculate SHA-256 hash of stored file
            actual_hash = hashlib.sha256(file_data).hexdigest()
            
            if actual_hash != expected_hash:
                return {
                    'valid': False,
                    'message': f'Hash mismatch: expected {expected_hash}, got {actual_hash}'
                }
            
            return {'valid': True, 'message': 'File integrity verified'}
        
        except Exception as e:
            return {
                'valid': False,
                'message': f'Verification failed: {str(e)}'
            }
    
    def create_upload_session(self, user_id, filename, total_size, file_hash, encryption_level):
        """Create upload session for tracking"""
        db = self.collection.database
        
        session = {
            'user_id': ObjectId(user_id),
            'filename': filename,
            'total_size': total_size,
            'expected_hash': file_hash,
            'encryption_level': encryption_level,
            'uploaded_size': 0,
            'status': 'in_progress',  # in_progress, completed, failed, verified
            'created_at': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=2),  # Auto-cleanup after 2 hours
            'retry_count': 0,
            'last_error': None
        }
        
        result = db.upload_sessions.insert_one(session)
        return str(result.inserted_id)
    
    def update_upload_session(self, session_id, uploaded_size=None, status=None, error=None, retry_count=None):
        """Update upload session progress"""
        db = self.collection.database
        
        updates = {}
        if uploaded_size is not None:
            updates['uploaded_size'] = uploaded_size
        if status is not None:
            updates['status'] = status
        if error is not None:
            updates['last_error'] = error
        if retry_count is not None:
            updates['retry_count'] = retry_count
        
        if updates:
            db.upload_sessions.update_one(
                {'_id': ObjectId(session_id)},
                {'$set': updates}
            )
    
    def mark_upload_session_complete(self, session_id, file_id, verified=True):
        """Mark upload session as complete"""
        db = self.collection.database
        
        db.upload_sessions.update_one(
            {'_id': ObjectId(session_id)},
            {
                '$set': {
                    'status': 'verified' if verified else 'completed',
                    'file_id': file_id,
                    'completed_at': datetime.now(timezone.utc)
                }
            }
        )
    
    def cleanup_orphaned_chunks(self):
        """Remove chunks not referenced in files (orphaned chunks from failed uploads)"""
        db = self.collection.database
        
        try:
            # Get all file IDs that are referenced
            referenced_files = db['fs.files'].find({}, {'_id': 1})
            valid_file_ids = set(f['_id'] for f in referenced_files)
            
            # Find orphaned chunks (chunks with files_id not in valid set)
            orphaned = list(db['fs.chunks'].find({
                'files_id': {'$nin': list(valid_file_ids)}
            }))
            
            count = len(orphaned)
            
            # Delete orphaned chunks
            if count > 0:
                db['fs.chunks'].delete_many({
                    'files_id': {'$nin': list(valid_file_ids)}
                })
                print(f"[CLEANUP] Removed {count} orphaned chunks from GridFS")
            
            # Also cleanup expired upload sessions
            expired = db.upload_sessions.delete_many({
                'expires_at': {'$lt': datetime.now(timezone.utc)}
            })
            
            if expired.deleted_count > 0:
                print(f"[CLEANUP] Removed {expired.deleted_count} expired upload sessions")
            
            return {
                'orphaned_chunks_removed': count,
                'expired_sessions_removed': expired.deleted_count
            }
        
        except Exception as e:
            print(f"[ERROR] Cleanup operation failed: {e}")
            return {'error': str(e)}
    
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
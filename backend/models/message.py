from datetime import datetime, timezone
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING
import gridfs

class Message:
    _indexes_created = False
    
    def __init__(self, db):
        self.collection = db.messages
        self.fs = gridfs.GridFS(db)
        if not Message._indexes_created:
            self.create_indexes()
            Message._indexes_created = True
    
    def create_indexes(self):
        try:
            indexes = [
                IndexModel([('sender_id', ASCENDING), ('receiver_id', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
                IndexModel([('conversation_id', ASCENDING), ('created_at', ASCENDING)])
            ]
            self.collection.create_indexes(indexes)
        except Exception as e:
            print(f"[WARNING] Failed to create Message indexes: {e}")
    
    def _get_conversation_id(self, user1_id, user2_id):
        """Generate consistent conversation ID for two users"""
        ids = sorted([str(user1_id), str(user2_id)])
        return f"{ids[0]}_{ids[1]}"
    
    def send_message(self, sender_id, receiver_id, content, message_type='text', 
                    qr_code_data=None, file_data=None):
        """
        Send a message (text, QR code, or file)
        message_type: 'text', 'qr', 'file'
        """
        conversation_id = self._get_conversation_id(sender_id, receiver_id)
        
        message = {
            'conversation_id': conversation_id,
            'sender_id': ObjectId(sender_id),
            'receiver_id': ObjectId(receiver_id),
            'content': content,
            'message_type': message_type,
            'read': False,
            'created_at': datetime.now(timezone.utc)
        }
        
        # Add QR code data if present
        if message_type == 'qr' and qr_code_data:
            message['qr_data'] = qr_code_data
        
        # Add file data if present
        if message_type == 'file' and file_data:
            message['file_data'] = file_data
        
        result = self.collection.insert_one(message)
        message['_id'] = result.inserted_id
        return message
    
    def get_conversation(self, user1_id, user2_id, skip=0, limit=50):
        """Get messages between two users"""
        conversation_id = self._get_conversation_id(user1_id, user2_id)
        
        messages = list(self.collection.find({
            'conversation_id': conversation_id
        }).sort('created_at', DESCENDING).skip(skip).limit(limit))
        
        # Reverse to show oldest first
        messages.reverse()
        return messages
    
    def get_conversations_list(self, user_id):
        """Get list of all conversations for a user with last message"""
        user_oid = ObjectId(user_id)
        
        # Get all messages where user is sender or receiver
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'sender_id': user_oid},
                        {'receiver_id': user_oid}
                    ]
                }
            },
            {
                '$sort': {'created_at': -1}
            },
            {
                '$group': {
                    '_id': '$conversation_id',
                    'last_message': {'$first': '$$ROOT'},
                    'unread_count': {
                        '$sum': {
                            '$cond': [
                                {
                                    '$and': [
                                        {'$eq': ['$receiver_id', user_oid]},
                                        {'$eq': ['$read', False]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    }
                }
            },
            {
                '$sort': {'last_message.created_at': -1}
            }
        ]
        
        conversations = list(self.collection.aggregate(pipeline))
        return conversations
    
    def mark_as_read(self, conversation_id, user_id):
        """Mark all messages in a conversation as read for the user"""
        self.collection.update_many(
            {
                'conversation_id': conversation_id,
                'receiver_id': ObjectId(user_id),
                'read': False
            },
            {
                '$set': {'read': True}
            }
        )
    
    def get_unread_count(self, user_id):
        """Get total unread message count for a user"""
        count = self.collection.count_documents({
            'receiver_id': ObjectId(user_id),
            'read': False
        })
        return count
    
    def delete_message(self, message_id, user_id):
        """Delete a message (only sender can delete)"""
        result = self.collection.delete_one({
            '_id': ObjectId(message_id),
            'sender_id': ObjectId(user_id)
        })
        return result.deleted_count > 0
    
    def search_messages(self, user_id, query, conversation_id=None):
        """Search messages by content"""
        filter_query = {
            '$or': [
                {'sender_id': ObjectId(user_id)},
                {'receiver_id': ObjectId(user_id)}
            ],
            'content': {'$regex': query, '$options': 'i'}
        }
        
        if conversation_id:
            filter_query['conversation_id'] = conversation_id
        
        messages = list(self.collection.find(filter_query).sort('created_at', DESCENDING).limit(50))
        return messages

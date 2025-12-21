from datetime import datetime, timezone
from bson import ObjectId

class Friend:
    def __init__(self, db):
        self.collection = db.friendships
    
    def send_request(self, sender_id, receiver_id, message=""):
        # Check if request already exists
        existing = self.collection.find_one({
            'user1_id': ObjectId(sender_id),
            'user2_id': ObjectId(receiver_id),
            'status': 'pending'
        })
        if existing:
            return None
        
        friendship = {
            'user1_id': ObjectId(sender_id),
            'user2_id': ObjectId(receiver_id),
            'status': 'pending',
            'message': message,
            'shared_key': None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        result = self.collection.insert_one(friendship)
        return str(result.inserted_id)
    
    def accept_request(self, friendship_id, user_id, shared_key):
        friendship = self.collection.find_one({'_id': ObjectId(friendship_id)})
        if not friendship:
            return False
        
        # Verify user is the receiver
        if str(friendship['user2_id']) != user_id:
            return False
        
        self.collection.update_one(
            {'_id': ObjectId(friendship_id)},
            {
                '$set': {
                    'status': 'accepted',
                    'shared_key': shared_key,
                    'updated_at': datetime.now(timezone.utc)
                }
            }
        )
        
        # Update users' friend lists
        from app import db
        db.users.update_one(
            {'_id': friendship['user1_id']},
            {'$addToSet': {'friends': friendship['user2_id']}}
        )
        db.users.update_one(
            {'_id': friendship['user2_id']},
            {'$addToSet': {'friends': friendship['user1_id']}}
        )
        
        return True
    
    def get_friends(self, user_id):
        friendships = self.collection.find({
            '$or': [
                {'user1_id': ObjectId(user_id), 'status': 'accepted'},
                {'user2_id': ObjectId(user_id), 'status': 'accepted'}
            ]
        })
        
        friends = []
        for friendship in friendships:
            friend_id = str(friendship['user1_id']) if str(friendship['user1_id']) != user_id else str(friendship['user2_id'])
            friends.append({
                'friendship_id': str(friendship['_id']),
                'friend_id': friend_id,
                'shared_key': friendship['shared_key'],
                'created_at': friendship['created_at']
            })
        
        return friends
    
    def get_pending_requests(self, user_id):
        requests = self.collection.find({
            'user2_id': ObjectId(user_id),
            'status': 'pending'
        })
        
        result = []
        for req in requests:
            result.append({
                'request_id': str(req['_id']),
                'sender_id': str(req['user1_id']),
                'message': req['message'],
                'created_at': req['created_at']
            })
        
        return result
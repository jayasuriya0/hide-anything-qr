from datetime import datetime, timezone
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class Notification:
    _indexes_created = False
    
    def __init__(self, db):
        self.collection = db.notifications
        if not Notification._indexes_created:
            self.create_indexes()
            Notification._indexes_created = True
    
    def create_indexes(self):
        try:
            indexes = [
                IndexModel([('user_id', ASCENDING)]),
                IndexModel([('read', ASCENDING)]),
                IndexModel([('created_at', DESCENDING)]),
                IndexModel([('type', ASCENDING)]),
            ]
            self.collection.create_indexes(indexes)
        except Exception as e:
            print(f"[WARNING] Failed to create Notification indexes: {e}")
    
    def create_notification(self, user_id, notification_type, message, data=None, related_user_id=None):
        """Create a new notification"""
        notification = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'type': notification_type,
            'message': message,
            'data': data or {},
            'read': False,
            'created_at': datetime.now(timezone.utc),
            'read_at': None
        }
        
        if related_user_id:
            notification['related_user_id'] = ObjectId(related_user_id) if isinstance(related_user_id, str) else related_user_id
        
        result = self.collection.insert_one(notification)
        return str(result.inserted_id)
    
    def get_user_notifications(self, user_id, limit=20, unread_only=False, notification_type=None):
        """Get notifications for a user"""
        query = {'user_id': ObjectId(user_id)}
        
        if unread_only:
            query['read'] = False
        
        if notification_type:
            query['type'] = notification_type
        
        notifications = list(self.collection.find(query)
                           .sort('created_at', -1)
                           .limit(limit))
        
        # Convert ObjectIds to strings
        for notif in notifications:
            notif['_id'] = str(notif['_id'])
            notif['user_id'] = str(notif['user_id'])
            if 'related_user_id' in notif:
                notif['related_user_id'] = str(notif['related_user_id'])
        
        return notifications
    
    def mark_as_read(self, notification_id, user_id):
        """Mark a notification as read"""
        result = self.collection.update_one(
            {
                '_id': ObjectId(notification_id),
                'user_id': ObjectId(user_id)
            },
            {
                '$set': {
                    'read': True,
                    'read_at': datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0
    
    def mark_all_as_read(self, user_id):
        """Mark all user's notifications as read"""
        result = self.collection.update_many(
            {
                'user_id': ObjectId(user_id),
                'read': False
            },
            {
                '$set': {
                    'read': True,
                    'read_at': datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count
    
    def delete_notification(self, notification_id, user_id):
        """Delete a specific notification"""
        result = self.collection.delete_one({
            '_id': ObjectId(notification_id),
            'user_id': ObjectId(user_id)
        })
        return result.deleted_count > 0
    
    def delete_all_read(self, user_id):
        """Delete all read notifications for a user"""
        result = self.collection.delete_many({
            'user_id': ObjectId(user_id),
            'read': True
        })
        return result.deleted_count
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications"""
        return self.collection.count_documents({
            'user_id': ObjectId(user_id),
            'read': False
        })
    
    def create_friend_request_notification(self, receiver_id, sender_id, sender_username, request_id):
        """Create notification for friend request"""
        return self.create_notification(
            user_id=receiver_id,
            notification_type='friend_request',
            message=f"{sender_username} sent you a friend request",
            data={'request_id': request_id, 'sender_username': sender_username},
            related_user_id=sender_id
        )
    
    def create_friend_accepted_notification(self, receiver_id, sender_id, sender_username):
        """Create notification for friend request acceptance"""
        return self.create_notification(
            user_id=receiver_id,
            notification_type='friend_request_accepted',
            message=f"{sender_username} accepted your friend request",
            data={'sender_username': sender_username},
            related_user_id=sender_id
        )
    
    def create_content_received_notification(self, receiver_id, sender_id, sender_username, content_id, content_type):
        """Create notification for received content"""
        type_text = "a file" if content_type == "file" else "a message"
        return self.create_notification(
            user_id=receiver_id,
            notification_type='content_received',
            message=f"{sender_username} sent you {type_text}",
            data={
                'content_id': content_id,
                'content_type': content_type,
                'sender_username': sender_username
            },
            related_user_id=sender_id
        )
    
    def create_content_viewed_notification(self, receiver_id, sender_id, sender_username, content_id):
        """Create notification when content is viewed"""
        return self.create_notification(
            user_id=receiver_id,
            notification_type='content_viewed',
            message=f"{sender_username} viewed your content",
            data={
                'content_id': content_id,
                'sender_username': sender_username
            },
            related_user_id=sender_id
        )
    
    def get_notifications_by_type(self, user_id, notification_type):
        """Get notifications of a specific type"""
        return self.get_user_notifications(
            user_id=user_id,
            notification_type=notification_type,
            limit=50
        )
    
    def clear_old_notifications(self, user_id, days=30):
        """Delete notifications older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        result = self.collection.delete_many({
            'user_id': ObjectId(user_id),
            'created_at': {'$lt': cutoff_date},
            'read': True
        })
        return result.deleted_count

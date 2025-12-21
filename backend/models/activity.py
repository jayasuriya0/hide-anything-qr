from datetime import datetime, timezone
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING

class Activity:
    def __init__(self, db):
        self.collection = db.activities
        self.create_indexes()
    
    def create_indexes(self):
        indexes = [
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('created_at', DESCENDING)]),
            IndexModel([('type', ASCENDING)]),
            IndexModel([('visibility', ASCENDING)]),
        ]
        self.collection.create_indexes(indexes)
    
    def log_activity(self, user_id, activity_type, description, metadata=None, visibility='friends'):
        """
        Log user activity
        Types: share_qr, scan_qr, add_friend, accept_friend, upload_file, etc.
        Visibility: public, friends, private
        """
        activity = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'type': activity_type,
            'description': description,
            'metadata': metadata or {},
            'visibility': visibility,
            'created_at': datetime.now(timezone.utc)
        }
        
        result = self.collection.insert_one(activity)
        return str(result.inserted_id)
    
    def get_user_activity(self, user_id, limit=50):
        """Get all activities for a specific user"""
        activities = list(self.collection.find({'user_id': ObjectId(user_id)})
                         .sort('created_at', -1)
                         .limit(limit))
        
        return self._format_activities(activities)
    
    def get_feed(self, user_id, friend_ids=None, limit=30):
        """
        Get activity feed for user
        Includes their own activities and friends' activities
        """
        query_user_ids = [ObjectId(user_id)]
        
        # Add friend IDs to the query
        if friend_ids:
            query_user_ids.extend([ObjectId(fid) if isinstance(fid, str) else fid for fid in friend_ids])
        
        query = {
            'user_id': {'$in': query_user_ids},
            'visibility': {'$in': ['public', 'friends']}
        }
        
        activities = list(self.collection.find(query)
                         .sort('created_at', -1)
                         .limit(limit))
        
        return self._format_activities(activities)
    
    def get_recent_shares(self, user_id, limit=10):
        """Get recent QR code shares by user"""
        activities = list(self.collection.find({
            'user_id': ObjectId(user_id),
            'type': 'share_qr'
        }).sort('created_at', -1).limit(limit))
        
        return self._format_activities(activities)
    
    def get_recent_scans(self, user_id, limit=10):
        """Get recent QR code scans by user"""
        activities = list(self.collection.find({
            'user_id': ObjectId(user_id),
            'type': 'scan_qr'
        }).sort('created_at', -1).limit(limit))
        
        return self._format_activities(activities)
    
    def get_friend_activities(self, friend_ids, limit=20):
        """Get activities from specific friends"""
        if not friend_ids:
            return []
        
        query_friend_ids = [ObjectId(fid) if isinstance(fid, str) else fid for fid in friend_ids]
        
        activities = list(self.collection.find({
            'user_id': {'$in': query_friend_ids},
            'visibility': {'$in': ['public', 'friends']}
        }).sort('created_at', -1).limit(limit))
        
        return self._format_activities(activities)
    
    def delete_activity(self, activity_id, user_id):
        """Delete an activity (only by owner)"""
        result = self.collection.delete_one({
            '_id': ObjectId(activity_id),
            'user_id': ObjectId(user_id)
        })
        return result.deleted_count > 0
    
    def get_stats(self, user_id):
        """Get activity statistics for user"""
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$group': {
                '_id': '$type',
                'count': {'$sum': 1}
            }}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        stats = {item['_id']: item['count'] for item in results}
        
        # Get last activity timestamp
        last_activity = self.collection.find_one(
            {'user_id': ObjectId(user_id)},
            sort=[('created_at', -1)]
        )
        
        return {
            'total_shares': stats.get('share_qr', 0),
            'total_scans': stats.get('scan_qr', 0),
            'total_friends_added': stats.get('add_friend', 0),
            'total_activities': sum(stats.values()),
            'last_activity': last_activity['created_at'].isoformat() if last_activity else None
        }
    
    def _format_activities(self, activities):
        """Format activities for API response"""
        formatted = []
        for activity in activities:
            formatted.append({
                'id': str(activity['_id']),
                'user_id': str(activity['user_id']),
                'type': activity['type'],
                'description': activity['description'],
                'metadata': activity.get('metadata', {}),
                'visibility': activity.get('visibility', 'friends'),
                'created_at': activity['created_at'].isoformat()
            })
        return formatted

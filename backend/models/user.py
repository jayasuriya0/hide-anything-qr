from datetime import datetime, timezone
import bcrypt
from bson import ObjectId
from pymongo import IndexModel, ASCENDING
from utils.encryption import generate_keypair, encrypt_private_key

class User:
    def __init__(self, db):
        self.collection = db.users
        self.create_indexes()
    
    def create_indexes(self):
        # Drop existing indexes to avoid conflicts (except _id)
        try:
            existing_indexes = self.collection.list_indexes()
            for index in existing_indexes:
                if index['name'] != '_id_':
                    try:
                        self.collection.drop_index(index['name'])
                    except:
                        pass
        except:
            pass
        
        # Create new indexes
        indexes = [
            IndexModel([('email', ASCENDING)], unique=True, sparse=True, name='email_unique_idx'),
            IndexModel([('phone', ASCENDING)], unique=True, sparse=True, name='phone_unique_idx'),
            IndexModel([('username', ASCENDING)], unique=True, name='username_unique_idx'),
            IndexModel([('created_at', ASCENDING)], name='created_at_idx'),
        ]
        self.collection.create_indexes(indexes)
    
    def create_user(self, email=None, phone=None, username=None, password=None):
        # Validate that at least email or phone is provided
        if not email and not phone:
            raise ValueError('Either email or phone number is required')
        
        # Check if user exists
        if email and self.collection.find_one({'email': email}):
            raise ValueError('Email already registered')
        if phone and self.collection.find_one({'phone': phone}):
            raise ValueError('Phone number already registered')
        if username and self.collection.find_one({'username': username}):
            raise ValueError('Username already taken')
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Generate encryption keys
        private_key, public_key = generate_keypair()
        encrypted_private_key = encrypt_private_key(private_key, password)
        
        user = {
            'email': email,
            'phone': phone,
            'username': username,
            'password_hash': password_hash,
            'public_key': public_key,
            'private_key_encrypted': encrypted_private_key,
            'friends': [],
            'friend_requests': [],
            'profile_pic_url': None,
            'bio': '',
            'status': '',
            'created_at': datetime.now(timezone.utc),
            'last_login': datetime.now(timezone.utc),
            'is_active': True,
            'settings': {
                'notifications': True,
                'privacy': 'friends_only',
                'theme': 'dark',
                'show_online_status': True,
                'allow_friend_requests': True,
                'notify_friend_requests': True,
                'notify_new_content': True,
                'notify_activities': True,
                'email_notifications': False
            }
        }
        
        result = self.collection.insert_one(user)
        return str(result.inserted_id)
    
    def authenticate(self, identifier, password):
        # Try to find user by email or phone
        user = self.collection.find_one({
            '$or': [
                {'email': identifier},
                {'phone': identifier}
            ],
            'is_active': True
        })
        if not user:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            # Update last login
            self.collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.now(timezone.utc)}}
            )
            return user
        return None
    
    def get_by_id(self, user_id):
        try:
            return self.collection.find_one({'_id': ObjectId(user_id), 'is_active': True})
        except:
            return None
    
    def get_by_email(self, email):
        return self.collection.find_one({'email': email, 'is_active': True})
    
    def get_by_phone(self, phone):
        return self.collection.find_one({'phone': phone, 'is_active': True})
    
    def update_profile(self, user_id, updates):
        allowed_fields = ['username', 'bio', 'status', 'profile_pic_url', 'settings']
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        
        if filtered_updates:
            self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': filtered_updates}
            )
    
    def search_users(self, query, exclude_user_id=None):
        regex_query = {'$regex': f'.*{query}.*', '$options': 'i'}
        filter_query = {
            '$or': [
                {'username': regex_query},
                {'email': regex_query},
                {'phone': regex_query}
            ],
            'is_active': True
        }
        
        if exclude_user_id:
            filter_query['_id'] = {'$ne': ObjectId(exclude_user_id)}
        
        return list(self.collection.find(
            filter_query,
            {'password_hash': 0, 'private_key_encrypted': 0}
        ).limit(20))
    
    def update_settings(self, user_id, settings):
        """Update user settings"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'settings': settings}}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from PIL import Image
from routes.helpers import get_user_model, get_db, get_activity_model

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads/profiles'
MAX_IMAGE_SIZE = (800, 800)  # Max dimensions for profile pictures

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get activity stats
        activity_model = get_activity_model()
        stats = activity_model.get_stats(user_id)
        
        # Get content stats
        db = get_db()
        from .helpers import get_friend_model
        friend_model = get_friend_model()
        
        # Get actual friends count from friends collection
        try:
            friends = friend_model.get_friends(user_id)
            friends_count = len(friends)
        except:
            friends_count = len(user.get('friends', []))
        
        content_stats = {
            'friends_count': friends_count,
            'content_shared': db.shared_content.count_documents({'sender_id': ObjectId(user_id)}),
            'content_received': db.shared_content.count_documents({'receiver_id': ObjectId(user_id)})
        }
        content_stats.update(stats)
        
        return jsonify({
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user.get('email'),
            'phone': user.get('phone'),
            'bio': user.get('bio', ''),
            'status': user.get('status', ''),
            'profile_pic_url': user.get('profile_pic_url'),
            'public_key': user['public_key'],
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
            'last_login': user['last_login'].isoformat() if user.get('last_login') else None,
            'settings': user.get('settings', {}),
            'stats': content_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        updates = {}
        db = get_db()
        
        # Allowed fields to update
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
            # Check if username is taken by another user
            existing = db.users.find_one({
                'username': username,
                '_id': {'$ne': ObjectId(user_id)}
            })
            if existing:
                return jsonify({'error': 'Username already taken'}), 400
            
            updates['username'] = username
        
        if 'bio' in data:
            bio = data['bio'].strip()
            if len(bio) > 500:
                return jsonify({'error': 'Bio must be 500 characters or less'}), 400
            updates['bio'] = bio
        
        if 'status' in data:
            status = data['status'].strip()
            if len(status) > 100:
                return jsonify({'error': 'Status must be 100 characters or less'}), 400
            updates['status'] = status
        
        if 'settings' in data:
            # Validate settings structure
            settings = data['settings']
            if isinstance(settings, dict):
                allowed_settings = ['notifications', 'privacy', 'theme', 'show_online_status', 'allow_friend_requests']
                
                user_model = get_user_model()
                user = user_model.get_by_id(user_id)
                current_settings = user.get('settings', {})
                
                # Merge with existing settings
                merged_settings = current_settings.copy()
                
                for key, value in settings.items():
                    if key in allowed_settings:
                        # Validate privacy setting
                        if key == 'privacy':
                            if value not in ['public', 'friends_only', 'private']:
                                return jsonify({'error': 'Invalid privacy setting'}), 400
                        
                        # Validate theme setting
                        elif key == 'theme':
                            if value not in ['light', 'dark']:
                                return jsonify({'error': 'Invalid theme setting'}), 400
                        
                        # Validate boolean settings
                        elif key in ['notifications', 'show_online_status', 'allow_friend_requests']:
                            if not isinstance(value, bool):
                                return jsonify({'error': f'{key} must be true or false'}), 400
                        
                        merged_settings[key] = value
                
                updates['settings'] = merged_settings
        
        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update user
        user_model = get_user_model()
        user_model.update_profile(user_id, updates)
        
        # Log activity if significant changes
        if 'bio' in updates or 'profile_pic_url' in updates:
            activity_model = get_activity_model()
            activity_model.log_activity(
                user_id,
                'update_profile',
                'Updated profile',
                {'fields_updated': list(updates.keys())},
                visibility='private'
            )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'updates': updates
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/upload-picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, webp'}), 400
        
        # Validate file size (max 5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"user_{user_id}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save and resize image
        try:
            image = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize if larger than max dimensions
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Save optimized image
            image.save(filepath, optimize=True, quality=85)
            
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
        
        # Update user profile
        profile_pic_url = f"/static/uploads/profiles/{unique_filename}"
        user_model = get_user_model()
        user_model.update_profile(user_id, {'profile_pic_url': profile_pic_url})
        
        # Log activity
        activity_model = get_activity_model()
        activity_model.log_activity(
            user_id,
            'update_profile',
            'Updated profile picture',
            {'profile_pic_url': profile_pic_url},
            visibility='friends'
        )
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_pic_url': profile_pic_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    try:
        current_user_id = get_jwt_identity()
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check privacy settings
        privacy = user.get('settings', {}).get('privacy', 'friends_only')
        
        # Check if users are friends
        are_friends = ObjectId(current_user_id) in user.get('friends', [])
        
        # Base information visible to everyone
        profile_data = {
            'user_id': str(user['_id']),
            'username': user['username'],
            'profile_pic_url': user.get('profile_pic_url'),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None
        }
        
        # Additional info based on privacy settings
        if privacy == 'public' or (privacy == 'friends_only' and are_friends) or user_id == current_user_id:
            profile_data.update({
                'bio': user.get('bio', ''),
                'status': user.get('status', ''),
                'stats': {
                    'friends_count': len(user.get('friends', []))
                }
            })
        
        # Full info for own profile
        if user_id == current_user_id:
            db = get_db()
            activity_model = get_activity_model()
            activity_stats = activity_model.get_stats(user_id)
            
            profile_data.update({
                'email': user.get('email'),
                'phone': user.get('phone'),
                'public_key': user['public_key'],
                'settings': user.get('settings', {}),
                'stats': {
                    'friends_count': len(user.get('friends', [])),
                    'content_shared': db.shared_content.count_documents({'sender_id': ObjectId(user_id)}),
                    'content_received': db.shared_content.count_documents({'receiver_id': ObjectId(user_id)}),
                    **activity_stats
                }
            })
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password required'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        # Verify current password
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        import bcrypt
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': new_password_hash}}
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password required to delete account'}), 400
        
        # Verify password
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        import bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return jsonify({'error': 'Incorrect password'}), 401
        
        # Soft delete - mark as inactive
        db = get_db()
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': False}}
        )
        
        # Remove from friends' lists
        db.users.update_many(
            {'friends': ObjectId(user_id)},
            {'$pull': {'friends': ObjectId(user_id)}}
        )
        
        # Delete friendships
        db.friendships.delete_many({
            '$or': [
                {'user1_id': ObjectId(user_id)},
                {'user2_id': ObjectId(user_id)}
            ]
        })
        
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

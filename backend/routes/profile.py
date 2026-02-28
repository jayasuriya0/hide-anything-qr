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
        
        # Get active and deleted QR counts
        total_qr_generated = db.shared_content.count_documents({
            'sender_id': ObjectId(user_id)
        })
        active_qr_count = db.shared_content.count_documents({
            'sender_id': ObjectId(user_id),
            'is_active': True
        })
        deleted_qr_count = db.shared_content.count_documents({
            'sender_id': ObjectId(user_id),
            'is_active': False
        })
        
        content_stats = {
            'friends_count': friends_count,
            'content_shared': db.shared_content.count_documents({'sender_id': ObjectId(user_id)}),
            'content_received': db.shared_content.count_documents({'receiver_id': ObjectId(user_id)}),
            'total_qr_generated': total_qr_generated,
            'active_qr_count': active_qr_count,
            'deleted_qr_count': deleted_qr_count
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
        db = get_db()
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


@profile_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    """Search for users by username, email, or phone"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        user_model = get_user_model()
        users = user_model.search_users(query, exclude_user_id=user_id)
        
        # Format results
        results = []
        for user in users:
            results.append({
                'user_id': str(user['_id']),
                'username': user['username'],
                'bio': user.get('bio', ''),
                'profile_pic_url': user.get('profile_pic_url'),
                'profile_visibility': user.get('settings', {}).get('profile_visibility', 'public')
            })
        
        return jsonify({'users': results}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/view/<target_user_id>', methods=['GET'])
@jwt_required()
def view_user_profile(target_user_id):
    """View another user's profile with appropriate QR visibility"""
    try:
        viewer_id = get_jwt_identity()
        
        # Get target user
        user_model = get_user_model()
        target_user = user_model.get_by_id(target_user_id)
        
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check profile visibility
        profile_visibility = target_user.get('settings', {}).get('profile_visibility', 'public')
        
        # Check if viewer is a friend
        from routes.helpers import get_friend_model
        friend_model = get_friend_model()
        friends = friend_model.get_friends(target_user_id)
        friend_ids = [f['friend_id'] for f in friends]
        is_friend = viewer_id in friend_ids
        
        # If profile is private and viewer is not a friend, deny access
        if profile_visibility == 'private' and not is_friend:
            return jsonify({
                'error': 'This profile is private',
                'username': target_user['username'],
                'profile_pic_url': target_user.get('profile_pic_url'),
                'is_private': True
            }), 403
        
        # Get QR codes with visibility logic
        db = get_db()
        from routes.helpers import get_content_model
        content_model = get_content_model()
        
        # Get all active QR codes shared by this user
        all_qr_codes = content_model.get_shared_by_user(target_user_id)
        
        visible_qr_codes = []
        for qr in all_qr_codes:
            # Skip inactive QR codes
            if not qr.get('is_active', True):
                continue
            
            is_public = qr['metadata'].get('is_public', False)
            shared_with_viewer = str(qr.get('receiver_id')) == viewer_id
            
            # NEW VISIBILITY RULES based on profile privacy:
            # If profile is PUBLIC:
            #   - Public QR codes: visible to everyone
            #   - Private QR codes (receiver_id set): only visible to that specific receiver
            # If profile is PRIVATE:
            #   - Public QR codes: only visible to friends
            #   - Private QR codes (receiver_id set): only visible to that specific receiver (if they're friends)
            
            should_show = False
            
            if profile_visibility == 'public':
                # PUBLIC profile: Show public QRs to everyone, private QRs only to receiver
                if is_public:
                    should_show = True  # Anyone can view public QRs
                elif shared_with_viewer:
                    should_show = True  # Only receiver can view their private QR
            else:
                # PRIVATE profile: Show public QRs only to friends, private QRs only to receiver
                if is_public and is_friend:
                    should_show = True  # Only friends can view public QRs
                elif shared_with_viewer and is_friend:
                    should_show = True  # Only receiver (if friend) can view their private QR
            
            if should_show:
                visible_qr_codes.append({
                    'content_id': qr['content_id'],
                    'type': qr['metadata'].get('type'),
                    'created_at': qr['created_at'].isoformat() if qr.get('created_at') else None,
                    'viewed': qr.get('viewed', False),
                    'view_count': qr.get('view_count', 0),
                    'is_public': is_public,
                    'shared_with_me': shared_with_viewer,
                    'can_view': True  # Add flag to indicate viewer can view this QR
                })
        
        # Get activity stats
        activity_model = get_activity_model()
        stats = activity_model.get_stats(target_user_id)
        
        # Calculate content stats
        friends_count = len(friends)
        total_qr_shared = len(all_qr_codes)
        public_qr_count = sum(1 for qr in all_qr_codes if qr['metadata'].get('is_public', False) and qr.get('is_active', True))
        
        return jsonify({
            'user_id': str(target_user['_id']),
            'username': target_user['username'],
            'bio': target_user.get('bio', ''),
            'status': target_user.get('status', ''),
            'profile_pic_url': target_user.get('profile_pic_url'),
            'created_at': target_user['created_at'].isoformat() if target_user.get('created_at') else None,
            'is_friend': is_friend,
            'profile_visibility': profile_visibility,
            'stats': {
                'friends_count': friends_count,
                'total_qr_shared': total_qr_shared,
                'public_qr_count': public_qr_count,
                **stats
            },
            'qr_codes': visible_qr_codes
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

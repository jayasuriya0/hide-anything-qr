from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from bson import ObjectId
from routes.helpers import get_notification_model, get_user_model, get_db

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_type = request.args.get('type', None)
        
        notification_model = get_notification_model()
        notifications = notification_model.get_user_notifications(
            user_id, 
            limit=limit, 
            unread_only=unread_only,
            notification_type=notification_type
        )
        
        # Enrich with user information
        user_model = get_user_model()
        for notification in notifications:
            if 'related_user_id' in notification:
                related_user = user_model.get_by_id(notification['related_user_id'])
                if related_user:
                    notification['related_user'] = {
                        'id': str(related_user['_id']),
                        'username': related_user['username'],
                        'profile_pic_url': related_user.get('profile_pic_url')
                    }
        
        return jsonify({
            'notifications': notifications,
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    try:
        user_id = get_jwt_identity()
        
        notification_model = get_notification_model()
        success = notification_model.mark_as_read(notification_id, user_id)
        
        if not success:
            return jsonify({'error': 'Notification not found'}), 404
        
        return jsonify({'message': 'Notification marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    try:
        user_id = get_jwt_identity()
        
        notification_model = get_notification_model()
        count = notification_model.mark_all_as_read(user_id)
        
        return jsonify({
            'message': 'All notifications marked as read',
            'modified_count': count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        user_id = get_jwt_identity()
        
        notification_model = get_notification_model()
        notifications = notification_model.get_user_notifications(user_id, limit=100, unread_only=True)
        
        # Count by type
        type_counts = {}
        for notif in notifications:
            notif_type = notif.get('type', 'general')
            type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
        
        return jsonify({
            'total_unread': len(notifications),
            'by_type': type_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    try:
        user_id = get_jwt_identity()
        
        notification_model = get_notification_model()
        success = notification_model.delete_notification(notification_id, user_id)
        
        if not success:
            return jsonify({'error': 'Notification not found'}), 404
        
        return jsonify({'message': 'Notification deleted'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/clear-all', methods=['DELETE'])
@jwt_required()
def clear_all_notifications():
    try:
        user_id = get_jwt_identity()
        
        db = get_db()
        result = db.notifications.delete_many({'user_id': ObjectId(user_id)})
        
        return jsonify({
            'message': 'All notifications cleared',
            'deleted_count': result.deleted_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    try:
        user_id = get_jwt_identity()
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        settings = user.get('settings', {})
        preferences = {
            'notifications_enabled': settings.get('notifications', True),
            'friend_request_notifications': settings.get('notify_friend_requests', True),
            'content_notifications': settings.get('notify_new_content', True),
            'activity_notifications': settings.get('notify_activities', True),
            'email_notifications': settings.get('email_notifications', False)
        }
        
        return jsonify(preferences), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        current_settings = user.get('settings', {})
        
        # Update notification preferences
        if 'notifications_enabled' in data:
            current_settings['notifications'] = bool(data['notifications_enabled'])
        if 'friend_request_notifications' in data:
            current_settings['notify_friend_requests'] = bool(data['friend_request_notifications'])
        if 'content_notifications' in data:
            current_settings['notify_new_content'] = bool(data['content_notifications'])
        if 'activity_notifications' in data:
            current_settings['notify_activities'] = bool(data['activity_notifications'])
        if 'email_notifications' in data:
            current_settings['email_notifications'] = bool(data['email_notifications'])
        
        user_model.update_profile(user_id, {'settings': current_settings})
        
        return jsonify({
            'message': 'Notification preferences updated',
            'preferences': current_settings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

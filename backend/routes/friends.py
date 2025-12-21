from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from routes.helpers import get_user_model, get_friend_model, get_socketio, get_activity_model, get_notification_model

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'users': []}), 200
        
        user_model = get_user_model()
        users = user_model.search_users(query, exclude_user_id=user_id)
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
        
        return jsonify({'users': users}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/request', methods=['POST'])
@jwt_required()
def send_friend_request():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        receiver_id = data.get('receiver_id')
        message = data.get('message', '')
        
        if not receiver_id:
            return jsonify({'error': 'Receiver ID required'}), 400
        
        # Check if receiver exists
        user_model = get_user_model()
        receiver = user_model.get_by_id(receiver_id)
        if not receiver:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already friends
        friend_model = get_friend_model()
        friends = friend_model.get_friends(user_id)
        if any(f['friend_id'] == receiver_id for f in friends):
            return jsonify({'error': 'Already friends'}), 400
        
        # Send request
        request_id = friend_model.send_request(user_id, receiver_id, message)
        
        if not request_id:
            return jsonify({'error': 'Request already sent'}), 400
        
        # Get sender info
        sender = user_model.get_by_id(user_id)
        
        # Send notification via WebSocket
        socketio = get_socketio()
        socketio.emit('friend_request', {
            'from': user_id,
            'from_username': sender['username'],
            'request_id': request_id,
            'message': message
        }, room=receiver_id)
        
        # Create notification if receiver has notifications enabled
        notification_model = get_notification_model()
        receiver_settings = receiver.get('settings', {})
        if receiver_settings.get('notify_friend_requests', True):
            notification_model.create_friend_request_notification(
                receiver_id,
                user_id,
                sender['username'],
                request_id
            )
        
        # Log activity
        activity_model = get_activity_model()
        activity_model.log_activity(
            user_id,
            'add_friend',
            f"Sent friend request to {receiver['username']}",
            {
                'receiver_id': receiver_id,
                'receiver_username': receiver['username'],
                'request_id': request_id
            },
            visibility='private'
        )
        
        return jsonify({
            'message': 'Friend request sent',
            'request_id': request_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/accept', methods=['POST'])
@jwt_required()
def accept_friend_request():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        request_id = data.get('request_id')
        shared_key = data.get('shared_key')
        
        if not request_id or not shared_key:
            return jsonify({'error': 'Request ID and shared key required'}), 400
        
        friend_model = get_friend_model()
        success = friend_model.accept_request(request_id, user_id, shared_key)
        
        if not success:
            return jsonify({'error': 'Failed to accept request'}), 400
        
        # Get user info
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        # Get the friendship to notify the sender
        from routes.helpers import get_db
        db = get_db()
        friendship = db.friendships.find_one({'_id': ObjectId(request_id)})
        sender_id = str(friendship['user1_id'])
        sender = user_model.get_by_id(sender_id)
        
        # Notify sender via WebSocket
        socketio = get_socketio()
        socketio.emit('friend_request_accepted', {
            'from': user_id,
            'from_username': user['username']
        }, room=sender_id)
        
        # Create notification if sender has notifications enabled
        notification_model = get_notification_model()
        sender_settings = sender.get('settings', {})
        if sender_settings.get('notify_friend_requests', True):
            notification_model.create_friend_accepted_notification(
                sender_id,
                user_id,
                user['username']
            )
        
        # Log activity for both users
        activity_model = get_activity_model()
        activity_model.log_activity(
            user_id,
            'accept_friend',
            f"Accepted friend request from {sender['username']}",
            {'friend_id': sender_id, 'friend_username': sender['username']},
            visibility='friends'
        )
        activity_model.log_activity(
            sender_id,
            'accept_friend',
            f"{user['username']} accepted your friend request",
            {'friend_id': user_id, 'friend_username': user['username']},
            visibility='friends'
        )
        
        return jsonify({'message': 'Friend request accepted'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/reject', methods=['POST'])
@jwt_required()
def reject_friend_request():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({'error': 'Request ID required'}), 400
        
        # Verify user is the receiver and delete the request
        from routes.helpers import get_db
        db = get_db()
        result = db.friendships.delete_one({
            '_id': ObjectId(request_id),
            'user2_id': ObjectId(user_id),
            'status': 'pending'
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Request not found'}), 404
        
        return jsonify({'message': 'Friend request rejected'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/list', methods=['GET'])
@jwt_required()
def get_friends_list():
    try:
        user_id = get_jwt_identity()
        
        friend_model = get_friend_model()
        friendships = friend_model.get_friends(user_id)
        
        # Get user details for each friend
        user_model = get_user_model()
        friends_with_details = []
        
        for friendship in friendships:
            friend = user_model.get_by_id(friendship['friend_id'])
            if friend:
                friends_with_details.append({
                    'friendship_id': friendship['friendship_id'],
                    'friend_id': friendship['friend_id'],
                    'username': friend['username'],
                    'email': friend['email'],
                    'profile_pic_url': friend.get('profile_pic_url'),
                    'bio': friend.get('bio', ''),
                    'public_key': friend['public_key'],
                    'shared_key': friendship['shared_key'],
                    'created_at': friendship['created_at'].isoformat() if friendship.get('created_at') else None
                })
        
        return jsonify({'friends': friends_with_details}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    try:
        user_id = get_jwt_identity()
        
        friend_model = get_friend_model()
        requests = friend_model.get_pending_requests(user_id)
        
        # Get sender details
        user_model = get_user_model()
        requests_with_details = []
        
        for req in requests:
            sender = user_model.get_by_id(req['sender_id'])
            if sender:
                requests_with_details.append({
                    'request_id': req['request_id'],
                    'sender_id': req['sender_id'],
                    'sender_username': sender['username'],
                    'sender_email': sender['email'],
                    'sender_profile_pic': sender.get('profile_pic_url'),
                    'message': req['message'],
                    'created_at': req['created_at'].isoformat() if req.get('created_at') else None
                })
        
        return jsonify({'requests': requests_with_details}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/remove/<friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    try:
        user_id = get_jwt_identity()
        
        # Find and delete the friendship
        from routes.helpers import get_db
        db = get_db()
        result = db.friendships.delete_one({
            '$or': [
                {'user1_id': ObjectId(user_id), 'user2_id': ObjectId(friend_id)},
                {'user1_id': ObjectId(friend_id), 'user2_id': ObjectId(user_id)}
            ],
            'status': 'accepted'
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Friendship not found'}), 404
        
        # Remove from users' friend lists
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$pull': {'friends': ObjectId(friend_id)}}
        )
        db.users.update_one(
            {'_id': ObjectId(friend_id)},
            {'$pull': {'friends': ObjectId(user_id)}}
        )
        
        return jsonify({'message': 'Friend removed'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

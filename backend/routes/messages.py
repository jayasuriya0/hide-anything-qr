from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from routes.helpers import get_message_model, get_user_model, get_friend_model
from datetime import datetime, timezone

messages_bp = Blueprint('messages', __name__)

def format_datetime(dt):
    """Format datetime to ISO string with explicit UTC timezone"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Ensure it's in UTC and format with Z suffix
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get all conversations for the current user"""
    try:
        user_id = get_jwt_identity()
        message_model = get_message_model()
        user_model = get_user_model()
        
        conversations = message_model.get_conversations_list(user_id)
        
        # Enhance conversations with friend info
        result = []
        for conv in conversations:
            last_msg = conv['last_message']
            
            # Determine the other user in conversation
            other_user_id = last_msg['receiver_id'] if str(last_msg['sender_id']) == user_id else last_msg['sender_id']
            
            # Get friend details
            friend = user_model.get_by_id(str(other_user_id))
            if friend:
                result.append({
                    'conversation_id': conv['_id'],
                    'friend': {
                        'id': str(friend['_id']),
                        'username': friend['username'],
                        'display_name': friend.get('display_name', friend['username']),
                        'avatar': friend.get('profile_pic_url') or friend.get('avatar')
                    },
                    'last_message': {
                        'content': last_msg['content'],
                        'type': last_msg['message_type'],
                        'created_at': format_datetime(last_msg['created_at']),
                        'is_sender': str(last_msg['sender_id']) == user_id
                    },
                    'unread_count': conv['unread_count']
                })
        
        return jsonify({'conversations': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/conversation/<friend_id>', methods=['GET'])
@jwt_required()
def get_conversation(friend_id):
    """Get messages in a conversation with a specific friend"""
    try:
        user_id = get_jwt_identity()
        message_model = get_message_model()
        user_model = get_user_model()
        
        # Verify friend exists
        friend = user_model.get_by_id(friend_id)
        if not friend:
            return jsonify({'error': 'Friend not found'}), 404
        
        # Get pagination params
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))
        
        # Get messages
        messages = message_model.get_conversation(user_id, friend_id, skip, limit)
        
        # Mark messages as read
        conversation_id = message_model._get_conversation_id(user_id, friend_id)
        message_model.mark_as_read(conversation_id, user_id)
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                'id': str(msg['_id']),
                'content': msg['content'],
                'type': msg['message_type'],
                'is_sender': str(msg['sender_id']) == user_id,
                'created_at': format_datetime(msg['created_at']),
                'read': msg.get('read', False)
            }
            
            # Add QR data if present
            if msg['message_type'] == 'qr' and 'qr_data' in msg:
                formatted_msg['qr_data'] = msg['qr_data']
            
            # Add file data if present
            if msg['message_type'] == 'file' and 'file_data' in msg:
                formatted_msg['file_data'] = msg['file_data']
            
            formatted_messages.append(formatted_msg)
        
        return jsonify({
            'messages': formatted_messages,
            'friend': {
                'id': str(friend['_id']),
                'username': friend['username'],
                'display_name': friend.get('display_name', friend['username']),
                'avatar': friend.get('profile_pic_url') or friend.get('avatar')
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message to a friend"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        receiver_id = data.get('receiver_id')
        content = data.get('content', '')
        message_type = data.get('type', 'text')  # 'text', 'qr', 'file'
        qr_data = data.get('qr_data')
        file_data = data.get('file_data')
        
        if not receiver_id:
            return jsonify({'error': 'Receiver ID required'}), 400
        
        if not content and message_type == 'text':
            return jsonify({'error': 'Message content required'}), 400
        
        # Verify receiver exists and is a friend
        user_model = get_user_model()
        friend_model = get_friend_model()
        
        receiver = user_model.get_by_id(receiver_id)
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        # Check if they are friends
        friends = friend_model.get_friends(user_id)
        friend_ids = [f['friend_id'] for f in friends]
        if receiver_id not in friend_ids:
            return jsonify({'error': 'You can only message friends'}), 403
        
        # Send message
        message_model = get_message_model()
        message = message_model.send_message(
            sender_id=user_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            qr_code_data=qr_data,
            file_data=file_data
        )
        
        # Format response
        response = {
            'id': str(message['_id']),
            'content': message['content'],
            'type': message['message_type'],
            'is_sender': True,
            'created_at': format_datetime(message['created_at']),
            'read': False
        }
        
        if qr_data:
            response['qr_data'] = qr_data
        if file_data:
            response['file_data'] = file_data
        
        return jsonify({'message': response}), 201
        
    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get total unread message count"""
    try:
        user_id = get_jwt_identity()
        message_model = get_message_model()
        
        count = message_model.get_unread_count(user_id)
        
        return jsonify({'unread_count': count}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/<message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message"""
    try:
        user_id = get_jwt_identity()
        message_model = get_message_model()
        
        success = message_model.delete_message(message_id, user_id)
        
        if not success:
            return jsonify({'error': 'Message not found or unauthorized'}), 404
        
        return jsonify({'message': 'Message deleted'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/search', methods=['GET'])
@jwt_required()
def search_messages():
    """Search messages"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        conversation_id = request.args.get('conversation_id')
        
        if not query or len(query) < 2:
            return jsonify({'messages': []}), 200
        
        message_model = get_message_model()
        messages = message_model.search_messages(user_id, query, conversation_id)
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': str(msg['_id']),
                'content': msg['content'],
                'type': msg['message_type'],
                'conversation_id': msg['conversation_id'],
                'is_sender': str(msg['sender_id']) == user_id,
                'created_at': format_datetime(msg['created_at'])
            })
        
        return jsonify({'messages': formatted_messages}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error searching messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from .helpers import get_activity_model, get_user_model, get_friend_model

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_activity_feed():
    """Get activity feed for current user (own + friends' activities)"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 30))
        
        # Get user's friend list
        friend_model = get_friend_model()
        try:
            friends = friend_model.get_friends(user_id)
            friend_ids = [f['friend_id'] for f in friends]
        except Exception as e:
            print(f"Error getting friends: {e}")
            import traceback
            traceback.print_exc()
            friend_ids = []
        
        # Get activity feed
        activity_model = get_activity_model()
        try:
            activities = activity_model.get_feed(user_id, friend_ids, limit)
        except Exception as e:
            print(f"Error getting activity feed: {e}")
            # Return empty feed if there's an error
            return jsonify({
                'activities': [],
                'count': 0
            }), 200
        
        # Enrich activities with user info
        user_model = get_user_model()
        enriched_activities = []
        
        for activity in activities:
            try:
                user = user_model.get_by_id(activity['user_id'])
                if user:
                    activity['user'] = {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'profile_pic_url': user.get('profile_pic_url')
                    }
                    enriched_activities.append(activity)
            except Exception as e:
                print(f"Error enriching activity: {e}")
                continue
        
        return jsonify({
            'activities': enriched_activities,
            'count': len(enriched_activities)
        }), 200
        
    except Exception as e:
        print(f"Activity feed error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty feed instead of 500 error
        return jsonify({
            'activities': [],
            'count': 0,
            'error': str(e)
        }), 200

@activity_bp.route('/my-activities', methods=['GET'])
@jwt_required()
def get_my_activities():
    """Get current user's own activities"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        
        activity_model = get_activity_model()
        activities = activity_model.get_user_activity(user_id, limit)
        
        return jsonify({
            'activities': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/recent-shares', methods=['GET'])
@jwt_required()
def get_recent_shares():
    """Get recent QR code shares"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 10))
        
        activity_model = get_activity_model()
        activities = activity_model.get_recent_shares(user_id, limit)
        
        return jsonify({
            'shares': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/recent-scans', methods=['GET'])
@jwt_required()
def get_recent_scans():
    """Get recent QR code scans"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 10))
        
        activity_model = get_activity_model()
        activities = activity_model.get_recent_scans(user_id, limit)
        
        return jsonify({
            'scans': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/friend-activities', methods=['GET'])
@jwt_required()
def get_friend_activities():
    """Get activities from friends only"""
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))
        
        # Get friends
        friend_model = get_friend_model()
        friends = friend_model.get_friends(user_id)
        friend_ids = [str(f['_id']) for f in friends]
        
        # Get friend activities
        activity_model = get_activity_model()
        activities = activity_model.get_friend_activities(friend_ids, limit)
        
        # Enrich with user info
        user_model = get_user_model()
        enriched_activities = []
        
        for activity in activities:
            user = user_model.get_by_id(activity['user_id'])
            if user:
                activity['user'] = {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'profile_pic_url': user.get('profile_pic_url')
                }
                enriched_activities.append(activity)
        
        return jsonify({
            'activities': enriched_activities,
            'count': len(enriched_activities)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_activity_stats():
    """Get activity statistics for current user"""
    try:
        user_id = get_jwt_identity()
        
        activity_model = get_activity_model()
        stats = activity_model.get_stats(user_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/<activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """Delete an activity"""
    try:
        user_id = get_jwt_identity()
        
        activity_model = get_activity_model()
        success = activity_model.delete_activity(activity_id, user_id)
        
        if success:
            return jsonify({'message': 'Activity deleted'}), 200
        else:
            return jsonify({'error': 'Activity not found or unauthorized'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/log', methods=['POST'])
@jwt_required()
def log_activity():
    """Manually log an activity (for testing/admin)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        activity_type = data.get('type')
        description = data.get('description')
        metadata = data.get('metadata', {})
        visibility = data.get('visibility', 'friends')
        
        if not activity_type or not description:
            return jsonify({'error': 'Type and description required'}), 400
        
        activity_model = get_activity_model()
        activity_id = activity_model.log_activity(
            user_id, 
            activity_type, 
            description, 
            metadata, 
            visibility
        )
        
        return jsonify({
            'message': 'Activity logged',
            'activity_id': activity_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

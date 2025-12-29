from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
import re
from .helpers import get_user_model
from config.security import (
    validate_username,
    validate_email_address,
    validate_password,
    validate_phone,
    sanitize_html,
    RATE_LIMITS
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    print("=== Registration attempt started ===")
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Validate input - convert empty strings to None
        email = data.get('email', '').strip().lower() if data.get('email') and data.get('email').strip() else None
        phone = data.get('phone', '').strip() if data.get('phone') and data.get('phone').strip() else None
        username = sanitize_html(data.get('username', '').strip())
        password = data.get('password', '')
        
        print(f"Parsed: email={email}, phone={phone}, username={username}")
        
        # Must have either email or phone
        if not email and not phone:
            return jsonify({'error': 'Email or phone number is required'}), 400
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Validate username
        valid, msg = validate_username(username)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Validate email if provided
        if email:
            valid, msg = validate_email_address(email)
            if not valid:
                return jsonify({'error': f'Invalid email: {msg}'}), 400
            email = msg  # Use normalized email
        
        # Validate phone if provided
        if phone:
            valid, msg = validate_phone(phone)
            if not valid:
                return jsonify({'error': msg}), 400
        
        # Validate password strength
        valid, msg = validate_password(password)
        if not valid:
            return jsonify({'error': msg}), 400
        
        user_model = get_user_model()
        user_id = user_model.create_user(email=email, phone=phone, username=username, password=password)
        
        # Generate tokens
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValueError as e:
        print(f"Registration ValueError: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Registration Exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip() if data.get('email') else None
        phone = data.get('phone', '').strip() if data.get('phone') else None
        password = data.get('password', '')
        
        # Determine the identifier based on which field is provided
        identifier = None
        if email:
            identifier = sanitize_html(email).lower()
        elif phone:
            identifier = sanitize_html(phone)
        
        if not identifier or not password:
            return jsonify({'error': 'Email/phone and password required'}), 400
        
        user_model = get_user_model()
        user = user_model.authenticate(identifier, password)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Decrypt the user's private key with their password
        try:
            from utils.encryption import decrypt_private_key
            encrypted_private_key = user.get('private_key_encrypted')
            if encrypted_private_key:
                decrypted_private_key = decrypt_private_key(encrypted_private_key, password)
                # Store decrypted private key in the user document (in memory, not persisted)
                # Update user document to include decrypted private key for this session
                user_model.collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'private_key': decrypted_private_key}}
                )
        except Exception as e:
            print(f"Warning: Could not decrypt private key: {e}")
        
        # Generate tokens
        access_token = create_access_token(identity=str(user['_id']))
        refresh_token = create_refresh_token(identity=str(user['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user.get('email'),
            'phone': user.get('phone'),
            'public_key': user['public_key'],
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        print(f"Login Exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_access_token}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user_id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'phone': user.get('phone', ''),
            'public_key': user['public_key'],
            'profile_pic_url': user.get('profile_pic_url'),
            'bio': user.get('bio', ''),
            'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
            'settings': user.get('settings', {})
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real app, you'd add the token to a blacklist
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/update-settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update user settings (notifications, preferences)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        User = get_user_model()
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update settings in user document
        settings = data.get('settings', {})
        result = User.update_settings(user_id, settings)
        
        if result:
            return jsonify({'message': 'Settings updated successfully', 'settings': settings}), 200
        else:
            return jsonify({'error': 'Failed to update settings'}), 500
            
    except Exception as e:
        print(f"Update settings error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import base64
from io import BytesIO
from routes.helpers import get_user_model, get_db, get_socketio, get_content_model, get_encryption_manager, get_qr_generator, get_activity_model, get_notification_model
from config.security import (
    validate_file_upload,
    validate_text_content,
    validate_object_id,
    sanitize_html,
    secure_filename,
    RATE_LIMITS
)

content_bp = Blueprint('content', __name__)

@content_bp.route('/share/text', methods=['POST'])
@jwt_required()
def share_text():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        text = data.get('text')
        receiver_id = data.get('receiver_id')
        expires_in = data.get('expires_in')  # in seconds
        encryption_level = data.get('encryption_level', 'standard')  # basic, standard, high, maximum
        
        if not text:
            return jsonify({'error': 'Text content required'}), 400
        
        # Validate text content
        valid, msg = validate_text_content(text)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Validate receiver_id if provided
        if receiver_id:
            valid, msg = validate_object_id(receiver_id)
            if not valid:
                return jsonify({'error': f'Invalid receiver: {msg}'}), 400
        
        # Get encryption configuration
        encryption = get_encryption_manager()
        from utils.encryption import get_encryption_levels
        enc_levels = get_encryption_levels()
        enc_config = enc_levels.get(encryption_level, enc_levels['standard'])
        
        # Get receiver's public key
        user_model = get_user_model()
        receiver = user_model.get_by_id(receiver_id) if receiver_id else None
        
        if receiver_id and not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        # Generate AES key based on encryption level
        aes_key = encryption.generate_aes_key(enc_config['aes_key_size'])
        
        # Encrypt the text
        encrypted_text = encryption.encrypt_data(text, aes_key)
        
        # Encrypt AES key with receiver's public key (or encode for public sharing)
        if receiver:
            encrypted_aes_key = encryption.encrypt_aes_key(aes_key, receiver['public_key'])
        else:
            # For public sharing, base64 encode the AES key
            import base64
            encrypted_aes_key = base64.b64encode(aes_key).decode()
        
        # Store content
        content_model = get_content_model()
        metadata = {
            'type': 'text',
            'length': len(text),
            'is_public': not bool(receiver_id),
            'encryption_level': encryption_level,
            'encryption_name': enc_config['name']
        }
        
        content_id, content = content_model.share_content(
            user_id, receiver_id, encrypted_text, metadata, 
            encrypted_aes_key, expires_in
        )
        
        # Generate QR code
        qr_data = {
            'content_id': content_id,
            'encrypted_key': encrypted_aes_key,
            'sender_id': user_id,
            'metadata': metadata
        }
        
        qr_generator = get_qr_generator()
        qr_code = qr_generator.generate_qr_code(qr_data)
        
        # Send notification to receiver if not public
        if receiver_id:
            socketio = get_socketio()
            socketio.emit('new_content', {
                'from': user_id,
                'content_id': content_id
            }, room=receiver_id)
            
            # Create notification if receiver has notifications enabled
            notification_model = get_notification_model()
            receiver_settings = receiver.get('settings', {})
            if receiver_settings.get('notify_new_content', True):
                sender = user_model.get_by_id(user_id)
                notification_model.create_content_received_notification(
                    receiver_id,
                    user_id,
                    sender['username'],
                    content_id,
                    'text'
                )
        
        # Log activity
        activity_model = get_activity_model()
        user_model_for_name = user_model.get_by_id(user_id)
        receiver_name = receiver['username'] if receiver else 'public'
        activity_model.log_activity(
            user_id,
            'share_qr',
            f"Shared encrypted text QR code with {receiver_name}",
            {
                'content_id': content_id,
                'content_type': 'text',
                'encryption_level': encryption_level,
                'receiver_id': receiver_id,
                'is_public': not bool(receiver_id)
            },
            visibility='friends' if receiver_id else 'public'
        )
        
        return jsonify({
            'content_id': content_id,
            'qr_code': qr_code,
            'encryption_level': encryption_level,
            'encryption_name': enc_config['name'],
            'message': 'Content shared successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/send-qr-email', methods=['POST'])
@jwt_required()
def send_qr_email():
    """Send QR code to receiver's email"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        receiver_id = data.get('receiver_id')
        content_id = data.get('content_id')
        metadata = data.get('metadata', {})
        
        if not receiver_id or not content_id:
            return jsonify({'error': 'Receiver ID and Content ID required'}), 400
        
        # Get user models
        user_model = get_user_model()
        sender = user_model.get_by_id(user_id)
        receiver = user_model.get_by_id(receiver_id)
        
        if not receiver:
            return jsonify({'error': 'Receiver not found'}), 404
        
        receiver_email = receiver.get('email')
        if not receiver_email:
            return jsonify({'error': 'Receiver email not available'}), 400
        
        # Get content to generate QR again
        content_model = get_content_model()
        content = content_model.collection.find_one({'_id': ObjectId(content_id)})
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Generate QR code
        qr_data = {
            'content_id': content_id,
            'encrypted_key': content.get('encrypted_aes_key'),
            'sender_id': user_id,
            'metadata': metadata
        }
        
        qr_generator = get_qr_generator()
        qr_code = qr_generator.generate_qr_code(qr_data)
        
        # Send email using email_notifier
        try:
            from utils.email_notifier import send_qr_email as send_email
            
            sender_name = sender.get('username', 'A friend')
            content_type = metadata.get('type', 'content')
            encryption_level = metadata.get('encryption_level', 'standard')
            
            success = send_email(
                receiver_email=receiver_email,
                sender_name=sender_name,
                qr_code_base64=qr_code,
                content_type=content_type,
                encryption_level=encryption_level
            )
            
            if success:
                current_app.logger.info(f"✅ QR Code email sent to {receiver_email}")
                return jsonify({
                    'message': 'QR code email sent successfully',
                    'receiver': receiver.get('username')
                }), 200
            else:
                current_app.logger.error(f"❌ Failed to send email to {receiver_email}")
                return jsonify({
                    'error': 'Failed to send email. Please check server logs.',
                    'receiver': receiver.get('username')
                }), 500
                
        except Exception as email_error:
            current_app.logger.error(f"Email sending failed: {str(email_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': f'Email service error: {str(email_error)}',
                'receiver': receiver.get('username')
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error sending QR email: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@content_bp.route('/share/file', methods=['POST'])
@jwt_required()
def share_file():
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        receiver_id = request.form.get('receiver_id')
        expires_in = request.form.get('expires_in')
        encryption_level = request.form.get('encryption_level', 'standard')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        print(f"Sharing file: {file.filename}, type: {file.content_type}, encryption: {encryption_level}")
        
        # Get encryption configuration
        encryption = get_encryption_manager()
        from utils.encryption import get_encryption_levels
        enc_levels = get_encryption_levels()
        enc_config = enc_levels.get(encryption_level, enc_levels['standard'])
        
        # Read file
        file_data = file.read()
        print(f"File data read: {len(file_data)} bytes")
        
        # Get receiver
        user_model = get_user_model()
        receiver = user_model.get_by_id(receiver_id) if receiver_id else None
        
        # Generate AES key based on encryption level
        aes_key = encryption.generate_aes_key(enc_config['aes_key_size'])
        
        # Encrypt file data
        encrypted_data = encryption.encrypt_data(file_data, aes_key)
        print(f"File encrypted: {len(encrypted_data)} bytes")
        
        # Encrypt AES key
        if receiver:
            encrypted_aes_key = encryption.encrypt_aes_key(aes_key, receiver['public_key'])
        else:
            # For public sharing, base64 encode the AES key
            import base64
            encrypted_aes_key = base64.b64encode(aes_key).decode()
        
        # Store content
        content_model = get_content_model()
        metadata = {
            'type': 'file',
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(file_data),
            'is_public': not bool(receiver_id),
            'encryption_level': encryption_level,
            'encryption_name': enc_config['name']
        }
        
        print(f"Storing content with metadata: {metadata}")
        try:
            content_id, content = content_model.share_content(
                user_id, receiver_id, encrypted_data, metadata,
                encrypted_aes_key, int(expires_in) if expires_in else None
            )
            print(f"Content stored with ID: {content_id}")
        except Exception as storage_error:
            print(f"ERROR storing content: {storage_error}")
            import traceback
            traceback.print_exc()
            raise
        
        # Generate QR
        qr_data = {
            'content_id': content_id,
            'encrypted_key': encrypted_aes_key,
            'sender_id': user_id,
            'metadata': metadata
        }
        
        print("Generating QR code...")
        qr_generator = get_qr_generator()
        qr_code = qr_generator.generate_qr_code(qr_data)
        print("QR code generated successfully")
        
        # Notify receiver
        if receiver_id:
            socketio = get_socketio()
            socketio.emit('new_content', {
                'from': user_id,
                'content_id': content_id
            }, room=receiver_id)
            
            # Create notification if receiver has notifications enabled
            notification_model = get_notification_model()
            receiver_settings = receiver.get('settings', {})
            if receiver_settings.get('notify_new_content', True):
                sender = user_model.get_by_id(user_id)
                notification_model.create_content_received_notification(
                    receiver_id,
                    user_id,
                    sender['username'],
                    content_id,
                    'file'
                )
        
        # Log activity
        activity_model = get_activity_model()
        receiver_name = receiver['username'] if receiver else 'public'
        activity_model.log_activity(
            user_id,
            'share_qr',
            f"Shared encrypted file QR code ({file.filename}) with {receiver_name}",
            {
                'content_id': content_id,
                'content_type': 'file',
                'filename': file.filename,
                'encryption_level': encryption_level,
                'receiver_id': receiver_id,
                'is_public': not bool(receiver_id)
            },
            visibility='friends' if receiver_id else 'public'
        )
        
        return jsonify({
            'content_id': content_id,
            'qr_code': qr_code,
            'encryption_level': encryption_level,
            'encryption_name': enc_config['name'],
            'message': 'File shared successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/decode', methods=['POST'])
@jwt_required()
def decode_content():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        qr_data = data.get('qr_data')
        if not qr_data:
            return jsonify({'error': 'QR data required'}), 400
        
        # Decode secure QR data if it's in encoded format
        qr_generator = get_qr_generator()
        try:
            # Try to decode if it's secure format (new or old scheme)
            if isinstance(qr_data, str) and ('qrs://' in qr_data or 'hideanythingqr://' in qr_data or len(qr_data) > 50):
                decoded_data = qr_generator.decode_secure_data(qr_data)
                if isinstance(decoded_data, dict) and 'content_id' in decoded_data:
                    content_id = decoded_data['content_id']
                else:
                    content_id = qr_data
            else:
                content_id = qr_data
        except:
            # If decoding fails, use as-is
            content_id = qr_data
        
        # Get content
        content_model = get_content_model()
        
        # First try to find by content_id
        from bson import ObjectId
        content = content_model.collection.find_one({'_id': ObjectId(content_id)})
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Check if content is active
        if not content.get('is_active', True):
            return jsonify({'error': 'This content has been deactivated by the sender'}), 403
        
        # Check permissions
        if str(content['receiver_id']) != user_id and not content['metadata'].get('is_public'):
            return jsonify({'error': 'Not authorized to view this content'}), 403
        
        # Get user's private key for decryption
        user_model = get_user_model()
        user = user_model.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Decrypt the content
        encryption = get_encryption_manager()
        decrypted_data = None
        decryption_error = None
        
        try:
            # Get AES key first
            if content['metadata'].get('is_public'):
                # For public content, the AES key is base64 encoded
                import base64
                aes_key = base64.b64decode(content['encrypted_key'])
            else:
                # For private content, decrypt AES key with RSA
                # Check if current user is the receiver
                receiver_id = content.get('receiver_id')
                if not receiver_id:
                    # No specific receiver, use public decryption
                    import base64
                    aes_key = base64.b64decode(content['encrypted_key'])
                elif str(receiver_id) != user_id:
                    # User is not the receiver, check if sender
                    if str(content['sender_id']) == user_id:
                        # Sender viewing their own content
                        # Use sender's private key
                        user_private_key = user.get('private_key')
                        if not user_private_key:
                            raise Exception("Your private key not found. Please log out and log in again to decrypt content.")
                        aes_key = encryption.decrypt_aes_key(content['encrypted_key'], user_private_key)
                    else:
                        raise Exception("You are not authorized to decrypt this content. It was shared with someone else.")
                else:
                    # Current user is the receiver
                    user_private_key = user.get('private_key')
                    if not user_private_key:
                        raise Exception("Your private key not found. Please log out and log in again to decrypt content.")
                    aes_key = encryption.decrypt_aes_key(content['encrypted_key'], user_private_key)
            
            # Get encrypted data
            if content['metadata'].get('type') == 'file' and 'file_id' in content:
                # For files, retrieve from GridFS first
                grid_file = content_model.get_file(content['file_id'])
                if grid_file:
                    encrypted_data_str = grid_file.read().decode('utf-8')
                else:
                    raise Exception("File not found in GridFS")
            else:
                # For text, use encrypted_data directly
                encrypted_data_str = content['encrypted_data']
            
            # Decrypt the data with the AES key
            is_file = content['metadata'].get('type') == 'file'
            decrypted_data = encryption.decrypt_data(encrypted_data_str, aes_key, return_bytes=is_file)
            
            # For files, convert bytes to base64 for JSON response
            if is_file and isinstance(decrypted_data, bytes):
                import base64
                decrypted_data = base64.b64encode(decrypted_data).decode('utf-8')
            
        except Exception as e:
            print(f"[DECRYPTION ERROR] {e}")
            import traceback
            traceback.print_exc()
            decrypted_data = None
            decryption_error = str(e)
        
        # Mark as viewed
        content_model.mark_as_viewed(content_id)
        
        # Notify sender that their content was viewed (if not public and not the sender viewing)
        sender_id = str(content['sender_id'])
        if sender_id != user_id and content.get('receiver_id'):
            sender = user_model.get_by_id(sender_id)
            if sender:
                sender_settings = sender.get('settings', {})
                if sender_settings.get('notify_activities', True):
                    notification_model = get_notification_model()
                    viewer = user_model.get_by_id(user_id)
                    notification_model.create_content_viewed_notification(
                        sender_id,
                        user_id,
                        viewer['username'],
                        content_id
                    )
        
        # Log scan activity
        activity_model = get_activity_model()
        sender = user_model.get_by_id(str(content['sender_id']))
        sender_name = sender.get('username', 'Unknown') if sender else 'Unknown'
        
        content_type = content['metadata'].get('type', 'unknown')
        activity_model.log_activity(
            user_id,
            'scan_qr',
            f"Scanned QR code from {sender_name} ({content_type})",
            {
                'content_id': content_id,
                'content_type': content_type,
                'sender_id': str(content['sender_id']),
                'sender_name': sender_name
            },
            visibility='private'
        )
        
        response_data = {
            'content_id': str(content['_id']),
            'sender_id': str(content['sender_id']),
            'sender_name': sender_name,
            'metadata': content['metadata'],
            'created_at': content['created_at'].isoformat() if content.get('created_at') else None,
            'decrypted_content': decrypted_data,
            'is_encrypted': decrypted_data is None,
            'decryption_error': decryption_error
        }
        
        # If decryption failed, include encrypted data for debugging (only first 200 chars)
        if decrypted_data is None:
            response_data['encrypted_data'] = content.get('encrypted_data', '')[:200] if content.get('encrypted_data') else None
        
        # If it's a file, provide download link
        if content['metadata'].get('type') == 'file' and 'file_id' in content:
            response_data['download_url'] = f'/api/content/download/{content_id}'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/download/<content_id>', methods=['GET'])
@jwt_required()
def download_file(content_id):
    try:
        user_id = get_jwt_identity()
        
        content_model = get_content_model()
        from bson import ObjectId
        
        content = content_model.collection.find_one({'_id': ObjectId(content_id)})
        
        if not content or 'file_id' not in content:
            return jsonify({'error': 'File not found'}), 404
        
        # Check permissions
        if str(content['receiver_id']) != user_id and not content['metadata'].get('is_public'):
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get file from GridFS
        file_data = content_model.get_file(content['file_id'])
        if not file_data:
            return jsonify({'error': 'File data not found'}), 404
        
        # For demo, return the encrypted file
        # In real app, you would decrypt it first
        return send_file(
            BytesIO(file_data.read()),
            mimetype=content['metadata']['content_type'],
            as_attachment=True,
            download_name=content['metadata']['filename']
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/received', methods=['GET'])
@jwt_required()
def get_received_content():
    try:
        user_id = get_jwt_identity()
        content_type = request.args.get('type')
        
        content_model = get_content_model()
        contents = content_model.get_content_for_user(user_id, content_type)
        
        return jsonify({'contents': contents}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/encryption-levels', methods=['GET'])
def get_encryption_levels_route():
    """Get available encryption levels"""
    try:
        from utils.encryption import get_encryption_levels
        levels = get_encryption_levels()
        
        # Format for frontend
        formatted_levels = []
        for key, config in levels.items():
            formatted_levels.append({
                'value': key,
                'name': config['name'],
                'description': config['description'],
                'aes_bits': config['aes_key_size'] * 8,
                'rsa_bits': config['rsa_key_size']
            })
        
        return jsonify({'levels': formatted_levels}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/my-shared', methods=['GET'])
@jwt_required()
def get_my_shared_content():
    """Get all content shared by the current user"""
    try:
        user_id = get_jwt_identity()
        content_model = get_content_model()
        user_model = get_user_model()
        
        shared_content = content_model.get_shared_by_user(user_id)
        
        # Add receiver names
        for content in shared_content:
            if content['receiver_id']:
                receiver = user_model.get_by_id(content['receiver_id'])
                content['receiver_name'] = receiver['username'] if receiver else 'Unknown'
            else:
                content['receiver_name'] = 'Public'
        
        return jsonify({'shared_content': shared_content}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/deactivate/<content_id>', methods=['POST'])
@jwt_required()
def deactivate_content(content_id):
    """Deactivate a shared content"""
    try:
        user_id = get_jwt_identity()
        content_model = get_content_model()
        
        success = content_model.deactivate_content(content_id, user_id)
        
        if success:
            return jsonify({'message': 'Content deactivated successfully'}), 200
        else:
            return jsonify({'error': 'Content not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/activate/<content_id>', methods=['POST'])
@jwt_required()
def activate_content(content_id):
    """Activate a shared content"""
    try:
        user_id = get_jwt_identity()
        content_model = get_content_model()
        
        success = content_model.activate_content(content_id, user_id)
        
        if success:
            return jsonify({'message': 'Content activated successfully'}), 200
        else:
            return jsonify({'error': 'Content not found or unauthorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/qr/<content_id>', methods=['GET'])
@jwt_required()
def get_content_qr(content_id):
    """Get QR code for a shared content"""
    try:
        user_id = get_jwt_identity()
        content_model = get_content_model()
        
        # Get content - verify user is the sender
        from bson import ObjectId
        content = content_model.get_by_id(content_id)
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        if str(content['sender_id']) != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Regenerate QR code from stored data
        qr_data = {
            'content_id': content_id,
            'encrypted_key': content['encrypted_key'],
            'sender_id': user_id,
            'metadata': content.get('metadata', {})
        }
        
        qr_generator = get_qr_generator()
        qr_code = qr_generator.generate_qr_code(qr_data)
        
        return jsonify({
            'qr_code': qr_code,
            'content_id': content_id,
            'encryption_level': content.get('metadata', {}).get('encryption_level', 'standard'),
            'encryption_name': content.get('metadata', {}).get('encryption_name', 'Standard Encryption'),
            'is_active': content.get('is_active', True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/delete/<content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    """Delete a shared content permanently"""
    try:
        user_id = get_jwt_identity()
        content_model = get_content_model()
        
        # Get content - verify user is the sender
        from bson import ObjectId
        content = content_model.get_by_id(content_id)
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        if str(content['sender_id']) != user_id:
            return jsonify({'error': 'Unauthorized - you can only delete your own content'}), 403
        
        # Delete the content
        success = content_model.delete_content(content_id)
        
        if success:
            return jsonify({'message': 'Content deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete content'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

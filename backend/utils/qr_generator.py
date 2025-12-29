import qrcode
import base64
import json
from io import BytesIO
from PIL import Image

class QRGenerator:
    @staticmethod
    def encode_secure_data(data):
        """Encode data to prevent sensitive info exposure in regular scanners"""
        # Convert dict to JSON string
        if isinstance(data, dict):
            json_str = json.dumps(data, ensure_ascii=False)
        else:
            json_str = str(data)
        
        # Base64 encode the JSON to obfuscate it
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        # Use generic URL scheme so normal scanners don't reveal platform
        # This hides both sensitive info and platform identity
        secure_url = f"qrs://v?d={encoded}"
        return secure_url
    
    @staticmethod
    def decode_secure_data(encoded_url):
        """Decode the secure QR data back to original format"""
        try:
            # Handle both URL format and direct base64
            if encoded_url.startswith('qrs://v?d='):
                encoded = encoded_url.replace('qrs://v?d=', '')
            elif encoded_url.startswith('hideanythingqr://decode?data='):
                # Backward compatibility with old format
                encoded = encoded_url.replace('hideanythingqr://decode?data=', '')
            else:
                encoded = encoded_url
            
            # Decode from base64
            json_str = base64.b64decode(encoded).decode('utf-8')
            # Parse JSON
            return json.loads(json_str)
        except Exception as e:
            # If decoding fails, return as-is (for backward compatibility)
            return encoded_url
    
    @staticmethod
    def generate_qr_code(data, size=400, secure=True):
        """Generate QR code from data
        Args:
            data: Data to encode (dict or string)
            size: Size of QR code image
            secure: If True, encodes data to hide sensitive information
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # If secure mode, encode the data to hide sensitive info
        if secure and isinstance(data, dict):
            qr_data = QRGenerator.encode_secure_data(data)
        else:
            # If data is dict, convert to JSON string
            if isinstance(data, dict):
                qr_data = json.dumps(data, ensure_ascii=False)
            else:
                qr_data = data
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize if needed
        if size != 400:
            img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return img_str
    
    @staticmethod
    def generate_content_qr(content_id, encrypted_key, metadata):
        """Generate QR code for content sharing"""
        qr_data = {
            'type': 'hideanything_content',
            'content_id': content_id,
            'encrypted_key': encrypted_key,
            'metadata': metadata,
            'version': '1.0'
        }
        return QRGenerator.generate_qr_code(qr_data)
    
    @staticmethod
    def generate_friend_qr(user_id, public_key, username):
        """Generate QR code for friend requests"""
        qr_data = {
            'type': 'hideanything_friend',
            'user_id': user_id,
            'public_key': public_key,
            'username': username,
            'version': '1.0'
        }
        return QRGenerator.generate_qr_code(qr_data)
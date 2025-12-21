import qrcode
import base64
import json
from io import BytesIO
from PIL import Image

class QRGenerator:
    @staticmethod
    def generate_qr_code(data, size=400):
        """Generate QR code from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # If data is dict, convert to JSON string
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        
        qr.add_data(data)
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
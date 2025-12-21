"""
Helper functions to access app context objects in routes
"""
from flask import current_app

def get_db():
    """Get database instance from current app"""
    return current_app.db

def get_user_model():
    """Get User model instance"""
    from models.user import User
    return User(current_app.db)

def get_friend_model():
    """Get Friend model instance"""
    from models.friend import Friend
    return Friend(current_app.db)

def get_content_model():
    """Get Content model instance"""
    from models.content import Content
    return Content(current_app.db)

def get_notification_model():
    """Get Notification model instance"""
    from models.notification import Notification
    return Notification(current_app.db)

def get_activity_model():
    """Get Activity model instance"""
    from models.activity import Activity
    return Activity(current_app.db)

def get_socketio():
    """Get SocketIO instance"""
    return current_app.socketio

def get_encryption_manager():
    """Get EncryptionManager class"""
    from utils.encryption import EncryptionManager
    return EncryptionManager

def get_qr_generator():
    """Get QRGenerator class"""
    from utils.qr_generator import QRGenerator
    return QRGenerator

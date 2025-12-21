from .auth import auth_bp
from .content import content_bp
from .friends import friends_bp
from .notifications import notifications_bp
from .profile import profile_bp

__all__ = ['auth_bp', 'content_bp', 'friends_bp', 'notifications_bp', 'profile_bp']

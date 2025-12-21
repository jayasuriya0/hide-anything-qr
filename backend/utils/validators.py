import re
from datetime import datetime

def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email too long"
    
    return True, email

def validate_phone(phone):
    """
    Validate phone number in international format (E.164)
    Format: +[country code][number]
    Example: +1234567890, +447911123456
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number is required"
    
    # Remove spaces and dashes for validation
    phone_cleaned = phone.replace(' ', '').replace('-', '').strip()
    
    # E.164 format: + followed by 7-15 digits
    pattern = r'^\+[1-9]\d{6,14}$'
    
    if not re.match(pattern, phone_cleaned):
        return False, "Invalid phone format. Use international format (e.g., +1234567890)"
    
    return True, phone_cleaned

def validate_username(username):
    """Validate username format"""
    if not username or not isinstance(username, str):
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be 30 characters or less"
    
    # Only alphanumeric, underscore, and hyphen
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, username

def validate_password(password):
    """Validate password strength"""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password too long"
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for at least one letter
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    
    return True, password

def validate_bio(bio):
    """Validate user bio"""
    if bio is None:
        return True, ""
    
    if not isinstance(bio, str):
        return False, "Bio must be text"
    
    bio = bio.strip()
    
    if len(bio) > 500:
        return False, "Bio must be 500 characters or less"
    
    return True, bio

def validate_file_size(file_size, max_size_mb=50):
    """Validate file size"""
    max_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_bytes:
        return False, f"File size must be {max_size_mb}MB or less"
    
    return True, file_size

def validate_file_type(filename, allowed_types):
    """Validate file type by extension"""
    if not filename or '.' not in filename:
        return False, "Invalid filename"
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in allowed_types:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
    
    return True, extension

def validate_content_text(text, max_length=100000):
    """Validate shared text content"""
    if not text or not isinstance(text, str):
        return False, "Text content is required"
    
    if len(text) > max_length:
        return False, f"Text must be {max_length} characters or less"
    
    return True, text

def validate_expiration(expires_in):
    """Validate expiration time in seconds"""
    if expires_in is None:
        return True, None
    
    try:
        expires_in = int(expires_in)
    except (ValueError, TypeError):
        return False, "Expiration time must be a number"
    
    if expires_in < 60:
        return False, "Expiration time must be at least 60 seconds"
    
    # Max 30 days
    if expires_in > 2592000:
        return False, "Expiration time cannot exceed 30 days"
    
    return True, expires_in

def validate_object_id(object_id):
    """Validate MongoDB ObjectId format"""
    if not object_id or not isinstance(object_id, str):
        return False, "Invalid ID format"
    
    # ObjectId is 24 hex characters
    pattern = r'^[a-f0-9]{24}$'
    if not re.match(pattern, object_id):
        return False, "Invalid ID format"
    
    return True, object_id

def sanitize_html(text):
    """Remove HTML tags from text"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags and content
    clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    
    return clean.strip()

def validate_search_query(query):
    """Validate search query"""
    if not query or not isinstance(query, str):
        return False, "Search query is required"
    
    query = query.strip()
    
    if len(query) < 2:
        return False, "Search query must be at least 2 characters"
    
    if len(query) > 100:
        return False, "Search query too long"
    
    return True, query

def validate_message(message, max_length=500):
    """Validate message content"""
    if message is None:
        return True, ""
    
    if not isinstance(message, str):
        return False, "Message must be text"
    
    message = message.strip()
    
    if len(message) > max_length:
        return False, f"Message must be {max_length} characters or less"
    
    return True, message

def validate_settings(settings):
    """Validate user settings object"""
    if not isinstance(settings, dict):
        return False, "Settings must be an object"
    
    allowed_keys = ['notifications', 'privacy', 'theme']
    
    # Check for invalid keys
    for key in settings.keys():
        if key not in allowed_keys:
            return False, f"Invalid setting: {key}"
    
    # Validate notifications
    if 'notifications' in settings:
        if not isinstance(settings['notifications'], bool):
            return False, "Notifications setting must be true or false"
    
    # Validate privacy
    if 'privacy' in settings:
        if settings['privacy'] not in ['public', 'friends_only', 'private']:
            return False, "Privacy must be: public, friends_only, or private"
    
    # Validate theme
    if 'theme' in settings:
        if settings['theme'] not in ['light', 'dark']:
            return False, "Theme must be: light or dark"
    
    return True, settings

def validate_pagination(page, limit, max_limit=100):
    """Validate pagination parameters"""
    try:
        page = int(page) if page else 1
        limit = int(limit) if limit else 20
    except (ValueError, TypeError):
        return False, "Invalid pagination parameters"
    
    if page < 1:
        return False, "Page must be 1 or greater"
    
    if limit < 1:
        return False, "Limit must be 1 or greater"
    
    if limit > max_limit:
        return False, f"Limit cannot exceed {max_limit}"
    
    return True, (page, limit)

# Helper function to validate all registration data
def validate_registration_data(email, username, password):
    """Validate all registration fields"""
    errors = []
    
    valid, result = validate_email(email)
    if not valid:
        errors.append(result)
    
    valid, result = validate_username(username)
    if not valid:
        errors.append(result)
    
    valid, result = validate_password(password)
    if not valid:
        errors.append(result)
    
    if errors:
        return False, errors
    
    return True, None

# Helper function to validate content sharing data
def validate_content_share(text=None, file=None, receiver_id=None, expires_in=None):
    """Validate content sharing parameters"""
    errors = []
    
    if not text and not file:
        errors.append("Either text or file is required")
    
    if text:
        valid, result = validate_content_text(text)
        if not valid:
            errors.append(result)
    
    if receiver_id:
        valid, result = validate_object_id(receiver_id)
        if not valid:
            errors.append(result)
    
    if expires_in:
        valid, result = validate_expiration(expires_in)
        if not valid:
            errors.append(result)
    
    if errors:
        return False, errors
    
    return True, None

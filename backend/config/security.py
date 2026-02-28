# Security Configuration
import os
from functools import wraps
from flask import request, jsonify
import bleach
import re
from email_validator import validate_email, EmailNotValidError

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'},
    'archive': {'zip', 'rar', '7z', 'tar', 'gz'}
}

# Maximum file sizes by type (in bytes)
MAX_FILE_SIZES = {
    'image': 10 * 1024 * 1024,      # 10MB
    'video': 50 * 1024 * 1024,      # 50MB
    'audio': 20 * 1024 * 1024,      # 20MB
    'document': 10 * 1024 * 1024,   # 10MB
    'archive': 20 * 1024 * 1024     # 20MB
}

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.socket.io https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data: blob:; media-src 'self' data: blob:; connect-src 'self' ws: wss: https://cdn.socket.io",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=(self)'
}

def get_allowed_origins():
    """Get allowed origins from environment or defaults"""
    env_origins = os.environ.get('ALLOWED_ORIGINS', '')
    if env_origins:
        return [origin.strip() for origin in env_origins.split(',')]
    
    # Development defaults
    if os.environ.get('FLASK_ENV') == 'development':
        return [
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://localhost:3000',
            'http://127.0.0.1:3000'
        ]
    
    # Production: Must be explicitly set
    return []

def validate_file_upload(file, file_type='document'):
    """Validate uploaded file"""
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    if '.' not in file.filename:
        return False, "File must have an extension"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    allowed = ALLOWED_EXTENSIONS.get(file_type, set())
    
    if ext not in allowed:
        return False, f"File type .{ext} not allowed for {file_type}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    max_size = MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024)
    if size > max_size:
        return False, f"File too large. Max size: {max_size / (1024 * 1024):.1f}MB"
    
    # Check for null bytes (file upload attacks)
    if '\x00' in file.filename:
        return False, "Invalid filename"
    
    return True, "File is valid"

def sanitize_html(text):
    """Sanitize HTML content to prevent XSS"""
    if not text:
        return ""
    return bleach.clean(text, strip=True)

def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be less than 30 characters"
    
    # Only alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, "Valid"

def validate_email_address(email):
    """Validate email format"""
    try:
        valid = validate_email(email, check_deliverability=False)
        return True, valid.normalized
    except EmailNotValidError as e:
        return False, str(e)

def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password too long"
    
    # Check complexity
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, "Valid"

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return True, "Optional"
    
    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid international format
    if not re.match(r'^\+?[1-9]\d{7,14}$', clean_phone):
        return False, "Invalid phone format. Use international format: +1234567890"
    
    return True, "Valid"

def validate_text_content(text, max_length=10000):
    """Validate text content"""
    if not text:
        return False, "Content cannot be empty"
    
    if len(text) > max_length:
        return False, f"Content too long. Maximum {max_length} characters"
    
    # Check for suspicious patterns
    if text.count('\x00') > 0:
        return False, "Invalid content"
    
    return True, "Valid"

def validate_object_id(oid):
    """Validate MongoDB ObjectId format"""
    if not oid:
        return False, "ID required"
    
    if not re.match(r'^[0-9a-fA-F]{24}$', str(oid)):
        return False, "Invalid ID format"
    
    return True, "Valid"

def secure_filename(filename):
    """Make filename secure"""
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Replace spaces and special chars
    filename = re.sub(r'[^\w\s\.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext

def require_valid_key(key_name):
    """Decorator to ensure environment key is set"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not os.environ.get(key_name):
                return jsonify({'error': f'{key_name} not configured'}), 500
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def add_security_headers(response):
    """Add security headers to response"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Rate limit configurations
RATE_LIMITS = {
    'default': '200 per hour',
    'auth': '10 per minute',
    'upload': '20 per hour',
    'decode': '100 per hour',
    'api': '1000 per hour',
    'messages': '500 per hour'  # Higher limit for real-time messaging
}

def get_rate_limit_key():
    """Get unique key for rate limiting"""
    # Use IP + user agent for better tracking
    return f"{request.remote_addr}:{request.headers.get('User-Agent', 'unknown')}"

def is_production():
    """Check if running in production"""
    return os.environ.get('FLASK_ENV') == 'production'

def validate_environment():
    """Validate required environment variables"""
    required = ['SECRET_KEY', 'JWT_SECRET_KEY', 'MONGO_URI']
    
    if is_production():
        required.extend(['ALLOWED_ORIGINS', 'REDIS_URL'])
    
    missing = []
    weak = []
    
    for key in required:
        value = os.environ.get(key)
        if not value:
            missing.append(key)
        elif key in ['SECRET_KEY', 'JWT_SECRET_KEY']:
            # Check if it's a weak dev key
            if len(value) < 32 or 'dev' in value.lower() or 'change' in value.lower():
                weak.append(f"{key} (appears to be a dev/weak key)")
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    if weak and is_production():
        raise ValueError(f"Weak keys detected in production: {', '.join(weak)}")
    
    return True

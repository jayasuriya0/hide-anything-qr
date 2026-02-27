import os
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
import redis

# Load environment variables
load_dotenv()

# Validate environment before starting
from config.security import (
    validate_environment, 
    get_allowed_origins, 
    add_security_headers,
    RATE_LIMITS,
    is_production
)

try:
    validate_environment()
except ValueError as e:
    print(f"[ERROR] Configuration Error: {e}")
    if is_production():
        raise  # Fail fast in production
    else:
        print("[WARNING] Running in development mode with weak keys - DO NOT USE IN PRODUCTION!")

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configure CORS with restricted origins
allowed_origins = get_allowed_origins()
print(f"[SECURITY] CORS allowed origins: {allowed_origins}")

CORS(app, 
     supports_credentials=True,
     resources={r"/api/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"]
     }}
)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/hide_anything_qr')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Session security
app.config['SESSION_COOKIE_SECURE'] = is_production()  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')

# Initialize rate limiter (without app context for now)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMITS['default']],
    storage_uri=os.environ.get('REDIS_URL', 'memory://')
)
limiter.init_app(app)

# Database connections
try:
    # Get MongoDB URI
    mongo_uri = app.config['MONGO_URI']
    
    if 'mongodb+srv://' in mongo_uri or 'mongodb.net' in mongo_uri:
        print(f"[INFO] Connecting to MongoDB Atlas...")
    else:
        print(f"[INFO] Connecting to MongoDB (localhost)...")
    
    # Connect to MongoDB
    mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Test connection
    mongo_client.admin.command('ping')
    print("[SUCCESS] MongoDB connected successfully")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    if '@' in str(mongo_uri):
        masked_uri = f"mongodb://***@{mongo_uri.split('@')[1] if '@' in mongo_uri else 'unknown'}"
    else:
        masked_uri = "mongodb://localhost:27017"
    print(f"   Connection URI (masked): {masked_uri}")
    # Create a dummy client for development
    mongo_client = None
    if is_production():
        raise
    
db = mongo_client.hide_anything_qr if mongo_client else None
try:
    redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
except:
    print("Warning: Redis connection failed. Some features may not work.")
    redis_client = None

# Import models
from models.user import User
from models.friend import Friend
from models.content import Content
from models.notification import Notification
from models.activity import Activity

# Make db and models available globally
app.db = db
app.User = User
app.Friend = Friend
app.Content = Content
app.Notification = Notification
app.Activity = Activity
app.socketio = socketio

# Import and register blueprints
from routes.auth import auth_bp
from routes.content import content_bp
from routes.friends import friends_bp
from routes.notifications import notifications_bp
from routes.profile import profile_bp
from routes.activity import activity_bp
from routes.messages import messages_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(content_bp, url_prefix='/api/content')
app.register_blueprint(friends_bp, url_prefix='/api/friends')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(activity_bp, url_prefix='/api/activity')
app.register_blueprint(messages_bp, url_prefix='/api/messages')

# Apply rate limits to specific blueprints
limiter.limit(RATE_LIMITS['auth'])(auth_bp)
limiter.limit(RATE_LIMITS['upload'])(content_bp)
limiter.limit(RATE_LIMITS['messages'])(messages_bp)

# Add security headers to all responses
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({'error': 'Too many requests. Please slow down.'}), 429

@app.errorhandler(500)
def internal_error(error):
    # Don't leak error details in production
    if is_production():
        return jsonify({'error': 'Internal server error'}), 500
    else:
        return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

# Root route - serve frontend
@app.route('/')
@limiter.exempt  # Don't rate limit static content
def index():
    return send_file('../frontend/index.html')

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    response = send_from_directory('../frontend', path)
    # Disable caching for development
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Hide Anything with QR'})

# SocketIO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('user_id')
    from flask_socketio import join_room
    join_room(room)

if __name__ == '__main__':
    # Get port from environment variable (for Render/production) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
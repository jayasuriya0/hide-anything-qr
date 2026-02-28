# CRITICAL: Eventlet monkey patching MUST be done before any other imports
# This prevents "ReferenceError: weakly-referenced object no longer exists"
import eventlet
eventlet.monkey_patch()

from app import app, socketio

# For production deployment (Render/Heroku/etc)
# Gunicorn with eventlet worker will use this
# The socketio app wraps the Flask app for WebSocket support

if __name__ == '__main__':
    # For local development only
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

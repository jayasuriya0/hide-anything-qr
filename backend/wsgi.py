# Gevent monkey patching for Python 3.13+ compatibility
from gevent import monkey
monkey.patch_all()

from app import app, socketio

# For production deployment (Render/Heroku/etc)
# Gunicorn with gevent worker will use this
# The socketio app wraps the Flask app for WebSocket support

if __name__ == '__main__':
    # For local development only
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

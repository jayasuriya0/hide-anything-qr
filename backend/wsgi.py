from app import app, socketio

# For production deployment (Render/Heroku/etc)
# Gunicorn will use this app object
if __name__ == '__main__':
    # For local development only
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

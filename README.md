# Hide Anything with QR

A secure, end-to-end encrypted content sharing platform that uses QR codes to share sensitive information between users. Share text, files, and messages with military-grade encryption, ensuring only the intended recipient can access the content.

## 🔐 Features

- **End-to-End Encryption**: RSA-2048 and AES-256-GCM encryption for all shared content
- **QR Code Sharing**: Generate QR codes for easy and secure content sharing
- **Friend System**: Connect with friends and share encrypted content
- **Real-time Notifications**: WebSocket-powered live updates for messages and friend requests
- **File Sharing**: Upload and share encrypted files (up to 50MB)
- **Content Expiration**: Set automatic expiration times for shared content
- **Public & Private Sharing**: Share content publicly or privately with specific users
- **User Profiles**: Customizable profiles with privacy settings
- **Secure Authentication**: JWT-based authentication with refresh tokens

## 🏗️ Architecture

### Backend (Flask/Python)
- **Framework**: Flask with Socket.IO for real-time features
- **Database**: MongoDB for data persistence, GridFS for file storage
- **Cache**: Redis for session management and caching
- **Encryption**: Cryptography library with RSA and AES-GCM
- **Authentication**: JWT tokens with bcrypt password hashing

### Frontend (Vanilla JS)
- Single-page application with responsive design
- WebSocket integration for real-time updates
- Camera API for QR code scanning
- Modern ES6+ JavaScript

## 📋 Prerequisites

- Python 3.11+
- MongoDB 7.0+
- Redis 7.0+
- Node.js (optional, for development tools)
- Docker & Docker Compose (optional, for containerized deployment)

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hide-anything-qr.git
   cd hide-anything-qr
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update the secret keys and passwords.

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:5000
   - MongoDB: localhost:27017
   - Redis: localhost:6379

### Option 2: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hide-anything-qr.git
   cd hide-anything-qr
   ```

2. **Install MongoDB and Redis**
   - Install MongoDB: https://docs.mongodb.com/manual/installation/
   - Install Redis: https://redis.io/download

3. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Update the configuration values in `.env`:
   ```
   SECRET_KEY=your-super-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   MONGO_URI=mongodb://localhost:27017/hide_anything_qr
   REDIS_URL=redis://localhost:6379/0
   ```

6. **Start MongoDB and Redis**
   ```bash
   # Start MongoDB
   mongod
   
   # Start Redis
   redis-server
   ```

7. **Run the application**
   ```bash
   # From the backend directory
   python app.py
   ```

8. **Access the application**
   - Open `frontend/index.html` in your browser
   - Or serve it with a simple HTTP server:
     ```bash
     python -m http.server 8000 --directory frontend
     ```
   - Access: http://localhost:8000

## 📁 Project Structure

```
hide-anything-qr/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── wsgi.py               # WSGI entry point
│   ├── requirements.txt      # Python dependencies
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── content.py       # Content sharing model
│   │   ├── friend.py        # Friend relationships
│   │   └── notification.py  # Notification system
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── content.py       # Content sharing endpoints
│   │   ├── friends.py       # Friend management
│   │   ├── notifications.py # Notification endpoints
│   │   └── profile.py       # User profile management
│   ├── utils/
│   │   ├── encryption.py    # Encryption utilities
│   │   ├── qr_generator.py  # QR code generation
│   │   └── validators.py    # Input validation
│   └── static/
│       └── uploads/          # File upload storage
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── styles/
│   │   └── main.css         # Stylesheets
│   ├── scripts/
│   │   ├── app.js           # Main application logic
│   │   ├── auth.js          # Authentication
│   │   ├── encryption.js    # Client-side encryption
│   │   ├── friends.js       # Friend management
│   │   └── qr.js            # QR code handling
│   └── assets/
│       ├── icons/
│       └── images/
├── docker-compose.yml        # Docker composition
├── Dockerfile               # Docker image definition
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout user

### Content Sharing
- `POST /api/content/share/text` - Share encrypted text
- `POST /api/content/share/file` - Share encrypted file
- `POST /api/content/decode` - Decode QR content
- `GET /api/content/download/<id>` - Download file
- `GET /api/content/received` - Get received content

### Friends
- `GET /api/friends/search` - Search users
- `POST /api/friends/request` - Send friend request
- `POST /api/friends/accept` - Accept friend request
- `POST /api/friends/reject` - Reject friend request
- `GET /api/friends/list` - Get friends list
- `GET /api/friends/requests` - Get pending requests
- `DELETE /api/friends/remove/<id>` - Remove friend

### Profile
- `GET /api/profile/` - Get own profile
- `GET /api/profile/<user_id>` - Get user profile
- `PUT /api/profile/update` - Update profile
- `POST /api/profile/upload-picture` - Upload profile picture
- `PUT /api/profile/change-password` - Change password
- `DELETE /api/profile/delete` - Delete account

### Notifications
- `GET /api/notifications/` - Get notifications
- `PUT /api/notifications/<id>/read` - Mark as read
- `PUT /api/notifications/read-all` - Mark all as read

## 🔒 Security Features

1. **End-to-End Encryption**
   - RSA-2048 key pairs generated for each user
   - AES-256-GCM for content encryption
   - Private keys encrypted with user password

2. **Secure Authentication**
   - JWT tokens with short expiration
   - Refresh token rotation
   - Bcrypt password hashing (cost factor 12)

3. **Data Protection**
   - HTTPS recommended for production
   - CORS configured for allowed origins
   - Input validation and sanitization
   - XSS and CSRF protection

4. **Privacy Controls**
   - Public, friends-only, and private content
   - Content expiration support
   - User privacy settings

## 🛠️ Development

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=backend tests/
```

### Code Quality
```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `MONGO_URI` | MongoDB connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `FLASK_ENV` | Environment (development/production) | production |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes | 52428800 (50MB) |
| `ALLOWED_ORIGINS` | CORS allowed origins | * |

## 📦 Production Deployment

### Using Docker

1. Update environment variables in `.env`
2. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

1. **Set up production database**
   ```bash
   # MongoDB with authentication
   mongod --auth --dbpath /data/db
   ```

2. **Configure environment**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret
   # ... other variables
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -k eventlet -w 4 -b 0.0.0.0:5000 backend.wsgi:app
   ```

4. **Set up Nginx reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /socket.io {
           proxy_pass http://localhost:5000/socket.io;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

5. **Enable HTTPS with Let's Encrypt**
   ```bash
   certbot --nginx -d your-domain.com
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework and community
- MongoDB and Redis teams
- Cryptography library maintainers
- QR code generation libraries

## 🔮 Future Enhancements

- [ ] Mobile applications (iOS/Android)
- [ ] Browser extensions
- [ ] Multi-factor authentication
- [ ] Group messaging
- [ ] Voice/video calls
- [ ] Self-destructing messages
- [ ] Blockchain integration for audit trails
- [ ] Advanced file type support
- [ ] Internationalization (i18n)

---

**⚠️ Security Notice**: This application handles sensitive data. Always use HTTPS in production, keep dependencies updated, and follow security best practices.

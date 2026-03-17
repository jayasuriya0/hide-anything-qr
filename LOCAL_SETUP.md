# 🚀 Local Development Setup Guide

## Quick Start (Recommended - Using Docker for MongoDB & Redis)

### Prerequisites
- Python 3.9+ installed
- Docker & Docker Compose installed ([Download Docker Desktop](https://www.docker.com/products/docker-desktop))

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start MongoDB & Redis with Docker
```bash
# From project root directory
docker-compose -f docker-compose.local.yml up -d
```

This starts:
- MongoDB on `localhost:27017`
- Redis on `localhost:6379`

### Step 3: Run the Flask Backend
```bash
cd backend
python app.py
```

The server will start at `http://localhost:5000`

### Step 4: Open in Browser
Visit `http://localhost:5000` and start using the app!

---

## Alternative: Manual Setup (Without Docker)

### Prerequisites
- Python 3.9+
- MongoDB 5.0+ installed and running locally
- Redis 6.0+ installed and running locally

### Step 1: Install MongoDB
- **Windows**: Download from [mongodb.com](https://www.mongodb.com/try/download/community)
- **Mac**: `brew install mongodb-community`
- **Linux**: `sudo apt install mongodb`

Verify MongoDB is running:
```bash
mongo --version
```

### Step 2: Install Redis
- **Windows**: Download from [releases.redis.io](https://releases.redis.io/)
- **Mac**: `brew install redis`
- **Linux**: `sudo apt install redis-server`

Verify Redis is running:
```bash
redis-cli ping
# Should respond with: PONG
```

### Step 3: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Flask Backend
```bash
cd backend
python app.py
```

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```
Error: MongoDB connection failed
```
**Solution:**
```bash
# Check if MongoDB is running
sudo service mongod status  # Linux
brew services list | grep mongo  # Mac
# or start Docker containers if using Option 1
docker-compose -f docker-compose.local.yml up -d
```

### Redis Connection Error
```
Error: Redis connection refused
```
**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should respond: PONG

# Or start Docker containers
docker-compose -f docker-compose.local.yml up -d
```

### Port Already in Use
```
Error: Port 5000 already in use
```
**Solution:**
```bash
# Change port in .env
# FLASK_ENV=development
# PORT=5001  # Change this

# Or kill the process using port 5000
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Module Not Found Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:**
```bash
# Activate virtual environment (optional but recommended)
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📝 Configuration

### `.env` File (Already Configured)
```env
FLASK_ENV=development
FLASK_DEBUG=1
MONGO_URI=mongodb://localhost:27017/hide_anything_qr
REDIS_URL=redis://localhost:6379/0
```

**Don't change URLs** - they're set for local development.

### Email Configuration (Optional)
If you want email notifications:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🧪 Testing the Setup

### Test Backend is Running
```bash
curl http://localhost:5000/api/health
# Should respond: {"status":"healthy","service":"Hide Anything with QR"}
```

### Test MongoDB Connection
```bash
mongosh
> db.adminCommand( { ping: 1 } )
# Should respond: { ok: 1 }
```

### Test Redis Connection
```bash
redis-cli ping
# Should respond: PONG
```

---

## 📦 Stop Services

### Using Docker
```bash
docker-compose -f docker-compose.local.yml down
```

### Stop Flask
Press `Ctrl+C` in the terminal

---

## 🔗 Access Points (After Setup)

- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

---

## 💡 Development Tips

1. **Hot Reload**: `FLASK_DEBUG=1` enables hot reload on file changes
2. **Database**: Data persists in MongoDB locally
3. **Logs**: Check browser console for frontend errors
4. **API Logs**: Check terminal for backend errors

---

## Next Steps

1. Create a test user account in the app
2. Test QR code generation
3. Test content sharing between users
4. Check browser console for any frontend errors

Good luck! 🎉

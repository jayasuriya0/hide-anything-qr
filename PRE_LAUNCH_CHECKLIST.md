# ✅ Pre-Launch Checklist

Run this before starting your project to ensure everything is configured correctly!

## 🔍 Installation Check

- [ ] Python 3.9+ installed
  ```powershell
  python --version
  ```

- [ ] Docker Desktop installed and running
  ```powershell
  docker --version
  docker-compose --version
  ```

- [ ] Project folder exists at correct location
  ```powershell
  cd c:\Users\teddy\OneDrive\Desktop\hide-anything-qr
  ```

## 📁 File Structure Check

Verify these files exist in your project:
- [ ] `backend/app.py` - Main Flask app
- [ ] `backend/requirements.txt` - Python dependencies
- [ ] `backend/.env` - Environment configuration
- [ ] `docker-compose.local.yml` - Docker services definition
- [ ] `frontend/index.html` - Frontend
- [ ] `LOCAL_SETUP.md` - Setup guide
- [ ] `WINDOWS_SETUP.md` - Windows guide
- [ ] `start-local.ps1` - Windows startup script

## ⚙️ Environment Configuration

Check `.env` file contains:
- [ ] `FLASK_ENV=development`
- [ ] `FLASK_DEBUG=1`
- [ ] `MONGO_URI=mongodb://localhost:27017/hide_anything_qr`
- [ ] `REDIS_URL=redis://localhost:6379/0`
- [ ] `ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000`

**If any value is different, update `.env` to match above!**

## 🐳 Docker & Services

- [ ] Docker Desktop is running (check system tray)
- [ ] Docker containers are available (Windows: Docker Desktop → running)
- [ ] Docker Compose can find local compose file:
  ```powershell
  docker-compose -f docker-compose.local.yml config
  ```

## 🔧 Network & Ports

Check these ports are not already in use:
- [ ] Port 5000 (Flask)
  ```powershell
  netstat -ano | findstr :5000
  # Should show nothing or your Flask app
  ```

- [ ] Port 27017 (MongoDB)
  ```powershell
  netstat -ano | findstr :27017
  # Should be empty or only Docker
  ```

- [ ] Port 6379 (Redis)
  ```powershell
  netstat -ano | findstr :6379
  # Should be empty or only Docker
  ```

## 🚀 Ready to Launch!

If all checkboxes are marked ✅, you're ready! Run in this order:

### Step 1: Start Services
```powershell
.\start-local.ps1
```
Wait for: "✅ Services are ready!"

### Step 2: Start Backend (new terminal)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Wait for: "Running on http://0.0.0.0:5000"

### Step 3: Open Browser
```
http://localhost:5000
```

## 🧪 Post-Launch Tests

After starting the app, verify:

- [ ] **Health Check**
  ```powershell
  curl http://localhost:5000/api/health
  # Should respond with JSON
  ```

- [ ] **Frontend Loads**
  - Open http://localhost:5000
  - Should see login/register form
  - No red errors in browser console (F12)

- [ ] **Can Register**
  - Try creating an account
  - Should see success message or validation errors

- [ ] **Can Login**
  - Login with created account
  - Should see dashboard

- [ ] **WebSocket Connected**
  - F12 → Console tab
  - Should see "Socket connected" message
  - No WebSocket errors

## 🔴 Something Not Working?

Run this diagnostic:

```powershell
# Check Docker containers
docker ps

# Should show:
# - hideanything-mongodb
# - hideanything-redis

# Check MongoDB connection
mongosh.exe --eval "db.adminCommand({ ping: 1 })"

# Check Redis connection  
redis-cli.exe ping
# Should respond: PONG

# Check Flask logs
# Look in the terminal where you ran: python app.py
# Look for error messages in red

# Check browser console
# Open http://localhost:5000
# Press F12
# Go to Console tab
# Look for red error messages
```

## 📚 Next Steps

Once everything is working:

1. **Create Test Account**
   - Email: `test@example.com`
   - Password: `Test@Password123`
   - Username: `testuser`

2. **Test Core Features**
   - Generate QR codes
   - Share content
   - Add friends
   - Send messages
   - Check notifications

3. **Check Logs**
   - Browser Console (F12)
   - Terminal output for Flask
   - Docker logs:
     ```powershell
     docker-compose -f docker-compose.local.yml logs -f
     ```

## ⚙️ Useful Commands

```powershell
# View Docker container logs
docker-compose -f docker-compose.local.yml logs -f mongodb
docker-compose -f docker-compose.local.yml logs -f redis

# Stop all services
docker-compose -f docker-compose.local.yml down

# Restart services
docker-compose -f docker-compose.local.yml restart

# Remove all data and start fresh
docker-compose -f docker-compose.local.yml down -v

# Connect to MongoDB
mongosh.exe mongodb://localhost:27017/hide_anything_qr

# Connect to Redis
redis-cli.exe
```

## 🎉 Success!

If all tests pass, your local development environment is working perfectly!

Happy coding! 🚀

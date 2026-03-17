# 🖥️ Windows Local Development Quick Start

**This is the easiest way to run Hide Anything with QR locally on Windows!**

## 📋 Prerequisites (Install in Order)

### 1. Python 3.11+ 
- Download: https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during installation
- Verify: Open PowerShell and run:
  ```powershell
  python --version
  ```

### 2. Docker Desktop
- Download: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Verify: Open PowerShell and run:
  ```powershell
  docker --version
  docker-compose --version
  ```

## 🚀 Start Services (2 Steps)

### Step 1️⃣: Start Database & Cache Services
Right-click `start-local.ps1` → Run with PowerShell

OR open PowerShell in the project folder and run:
```powershell
.\start-local.ps1
```

✅ This starts MongoDB and Redis in Docker containers

### Step 2️⃣: Start Flask Backend
Open a NEW PowerShell window in the project folder:

```powershell
# Navigate to backend
cd backend

# (Recommended) Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Python packages
pip install -r requirements.txt

# Start the Flask app
python app.py
```

Wait for this message:
```
Running on http://0.0.0.0:5000
```

## 🌐 Open the App

Go to: **http://localhost:5000**

## ✅ Verify Everything Works

Open browser developer console (F12) and check:
- ✅ No red errors in Console tab
- ✅ Network tab shows successful API calls
- ✅ Can see login/register form

## 🧪 Quick Test

1. **Register an account**
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `Test@1234`

2. **Generate QR Code**
   - Type some text
   - Click "Generate QR"

3. **Scan QR Code**
   - Click "Scan QR"
   - Allow camera access
   - Point at QR code

## ⚠️ Common Issues

### Issue: "Python not found"
```powershell
# Python not in PATH - reinstall and check "Add to PATH"
python --version
```

### Issue: "Docker is not running"
- Open Docker Desktop app and wait for it to fully start

### Issue: "Port 5000 already in use"
```powershell
# Find and kill process on port 5000
$tcpConnections = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($tcpConnections) {
    Stop-Process -Id $tcpConnections.OwningProcess -Force
}

# Then restart Flask
python app.py
```

### Issue: "MongoDB connection refused"
```powershell
# Check if containers are running
docker ps

# Restart containers
docker-compose -f docker-compose.local.yml restart
```

### Issue: "ModuleNotFoundError: No module named 'flask'"
```powershell
# Activate venv and install
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🛑 Stop Everything

When done developing:

```powershell
# Stop Flask (in backend terminal)
Ctrl + C

# Stop database services (in services terminal)
Ctrl + C

# Or use Docker
docker-compose -f docker-compose.local.yml down
```

## 📊 Check Service Status

```powershell
# List running Docker containers
docker ps

# View Docker logs
docker-compose -f docker-compose.local.yml logs -f

# MongoDB connection
mongosh

# Redis connection
redis-cli.exe
```

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5000 |
| API | http://localhost:5000/api |
| Health Check | http://localhost:5000/api/health |
| MongoDB | localhost:27017 |
| Redis | localhost:6379 |

## 📝 Environment File

Your `.env` is already configured for local development:
```
MONGO_URI=mongodb://localhost:27017/hide_anything_qr
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

**Don't change these values unless needed!**

## 🆘 Still Having Issues?

1. Check browser console for errors (F12)
2. Check terminal for Flask errors
3. Run this to test MongoDB:
   ```powershell
   mongosh
   > show databases
   > exit()
   ```
4. Run this to test Redis:
   ```powershell
   redis-cli.exe ping
   # Should respond: PONG
   ```

## 🎉 You're All Set!

Happy developing! Start by registering a test account and exploring the app.

---

**Need help?** Check the full `LOCAL_SETUP.md` for more detailed instructions.

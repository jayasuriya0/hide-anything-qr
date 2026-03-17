# 🔧 Local Development Troubleshooting Guide

## Common Issues & Solutions

### 1. "MongoDB connection refused"

**Error Message:**
```
[ERROR] MongoDB connection failed: [Errno 111] Connection refused
```

**Solutions:**

A) **MongoDB Container Not Running**
```powershell
# Check if containers are running
docker ps

# If not showing mongodb container:
docker-compose -f docker-compose.local.yml up -d

# Wait 5 seconds and try again
Start-Sleep -Seconds 5
python app.py
```

B) **MongoDB Not Responding**
```powershell
# Check MongoDB logs
docker-compose -f docker-compose.local.yml logs mongodb

# Restart MongoDB
docker-compose -f docker-compose.local.yml restart mongodb

# Nuclear option: Remove and recreate
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up -d
```

C) **Port Already in Use**
```powershell
# Kill process using port 27017
Get-Process | Where-Object {$_.Name -like "*mongo*"} | Stop-Process -Force

# Or in Docker
docker ps | findstr mongodb
docker stop <container-id>
```

---

### 2. "Redis connection refused"

**Error Message:**
```
[ERROR] Redis connection failed: Connection refused
```

**Solutions:**

```powershell
# Check if Redis is running
docker ps | findstr redis

# If not running:
docker-compose -f docker-compose.local.yml up -d redis

# Test Redis connection
redis-cli.exe -h localhost ping
# Should respond: PONG

# Restart Redis
docker-compose -f docker-compose.local.yml restart redis
```

---

### 3. "Port 5000 already in use"

**Error Message:**
```
ERROR: Address already in use
Address family not supported by protocol
```

**Solutions:**

**Option A: Kill Process on Port 5000**
```powershell
# Find process on port 5000
$connection = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($connection) {
    Write-Host "Process on port 5000: $($connection.OwningProcess)"
    Stop-Process -Id $connection.OwningProcess -Force
}

# Verify port is free
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
```

**Option B: Use Different Port**
```powershell
# Edit backend/app.py - change last line to:
# socketio.run(app, host='0.0.0.0', port=5001, debug=debug)

# Or set PORT in .env:
# PORT=5001

python app.py
# Then access at http://localhost:5001
```

---

### 4. "ModuleNotFoundError: No module named 'flask'"

**Error Message:**
```
ModuleNotFoundError: No module named 'flask'
Traceback (most recent call last):
  File "app.py", line 1, in <module>
    from flask import Flask
```

**Solutions:**

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt

# Verify Flask is installed
pip show flask

# Try again
python app.py
```

---

### 5. "CORS policy: No 'Access-Control-Allow-Origin' header"

**Error in Browser Console:**
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' 
from origin 'http://127.0.0.1:5000' has been blocked by CORS policy
```

**Solutions:**

```powershell
# Check .env file
type .env | findstr ALLOWED_ORIGINS
# Should show: ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000

# Add more origins if needed:
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000,http://localhost:3000,http://127.0.0.1:3000

# Restart Flask app
python app.py
```

---

### 6. "WebSocket connection failed"

**Error in Browser Console:**
```
WebSocket connection to 'ws://localhost/socket.io/?EIO=4&transport=websocket' failed
```

**Solutions:**

```powershell
# Check if Flask is running
curl http://localhost:5000/api/health

# Verify app.py has SocketIO enabled
findstr "socketio" backend/app.py
# Should find lines with socketio.run

# Check for eventlet issues
pip show eventlet
# If missing:
pip install eventlet==0.33.3

# Restart Flask
python app.py
```

---

### 7. "SyntaxError in Python file"

**Error:**
```
SyntaxError: invalid syntax
  File "backend/app.py", line X
```

**Solutions:**

```powershell
# Check Python version
python --version
# Should be 3.9+

# Validate syntax of problem file
python -m py_compile backend/app.py

# If error, check file encoding
# Make sure file is UTF-8 without BOM
```

---

### 8. "Import Error: No module named 'gmpy'"

**Error:**
```
ImportError: No module named 'gmpy'
Or cryptography module issues
```

**Solutions:**

```powershell
# This usually happens on Windows with cryptography
# Reinstall cryptography
pip uninstall cryptography -y
pip install cryptography==42.0.0

# Or reinstall all requirements
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

---

### 9. "Docker image build failed"

**Error:**
```
docker build . -f Dockerfile -t hideanything-backend
# BuildError
```

**Note:** For local dev, you DON'T need to build Docker images!

```powershell
# You only need docker-compose.local.yml which downloads pre-built images
# If you accidentally tried to build:

# Clean up
docker image prune -f

# Use compose (it downloads images automatically)
docker-compose -f docker-compose.local.yml up -d
```

---

### 10. "Virtual Environment Not Activating"

**Problem:** Activation script fails

**Solutions:**

```powershell
# If scripts disabled error appears:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activating again
.\venv\Scripts\Activate.ps1

# Verify activation (should show (venv) in prompt)
# If still failing, create new venv:
rmdir venv -Recurse -Force
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 11. "Frontend stuck on login page"

**Problem:** Can't register or login

**Debugging:**

```powershell
# 1. Check Flask is running properly
curl http://localhost:5000/api/health
# Should return JSON with "healthy" status

# 2. Check browser console for errors
# Open http://localhost:5000
# Press F12
# Go to Console tab
# Look for red errors

# 3. Check network requests
# F12 → Network tab
# Try to login
# Look for failed requests (red)
# Click request to see error details

# 4. Check MongoDB has data
mongosh.exe mongodb://localhost:27017/hide_anything_qr
# In mongosh:
> db.users.find().pretty()
# Should show users (if you created any)
```

---

### 12. "SSL Certificate errors"

**Error:**
```
[SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

```powershell
# Usually not a problem in development
# But if you see it during registration/email:

# Check your .env EMAIL settings
# Make sure SMTP configuration is correct

# Or temporarily disable SSL verification (dev only!)
# Don't use in production!

# Restart Flask without SSL checks
python app.py
```

---

### 13. "Database is locked"

**Error:**
```
OperationalError('database is locked')
```

**This usually won't happen with MongoDB, but if it does:**

```powershell
# Restart MongoDB
docker-compose -f docker-compose.local.yml restart mongodb

# Or nuke and restart
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up -d
```

---

### 14. "Out of Memory errors"

**Error:**
```
MemoryError
```

**Solutions:**

```powershell
# Check system resources
# If running low on RAM, stop other apps

# Docker might need more memory
# In Docker Desktop settings → Resources → Memory
# Increase available memory to at least 4GB

# Restart Docker
docker restart $(docker ps -q)
```

---

### 15. "Fresh Start (Nuclear Option)"

If nothing else works, do a complete reset:

```powershell
# Stop everything
docker-compose -f docker-compose.local.yml down -v

# Remove virtual environment
rmdir backend\venv -Recurse -Force

# Clean Docker
docker system prune -af --volumes

# Start fresh
docker-compose -f docker-compose.local.yml up -d

# Wait 10 seconds
Start-Sleep -Seconds 10

# New terminal - backend setup
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

---

## 📊 Debug Information

When reporting issues, include:

```powershell
# 1. Python version
python --version

# 2. Docker status
docker ps
docker-compose -f docker-compose.local.yml ps

# 3. Flask output (last 20 lines)
# Copy from terminal where you ran: python app.py

# 4. Browser console errors
# F12 → Console tab → Screenshot

# 5. Network errors
# F12 → Network tab → Failed request → Response

# 6. MongoDB status
mongosh.exe --eval "db.adminCommand({ ping: 1 })"

# 7. Redis status
redis-cli.exe ping
```

---

## 🆘 Still Need Help?

1. ✅ Check this file first
2. ✅ Read LOCAL_SETUP.md or WINDOWS_SETUP.md
3. ✅ Check PRE_LAUNCH_CHECKLIST.md
4. ✅ Search the error message in `app.py` file
5. ✅ Search GitHub for similar issues

---

## ✨ Pro Tips

- **Keep Docker running:** Don't close Docker Desktop while developing
- **Check logs often:** Terminal output is your friend
- **Use F12 Console:** Browser console shows frontend errors
- **Restart helps:** 90% of issues fixed by restarting Flask or Docker
- **Read error messages:** They usually tell you exactly what's wrong!

Good luck! You got this! 🚀

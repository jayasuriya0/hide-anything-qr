# ✅ Local Development Setup - Complete!

## 🎉 What Was Done

I've prepared your "Hide Anything with QR" project for local development. Here's what was configured:

### ✅ Documentation Created
- **QUICK_START.md** - Quick reference guide
- **WINDOWS_SETUP.md** - Step-by-step for Windows users
- **LOCAL_SETUP.md** - Detailed setup guide for all platforms
- **PRE_LAUNCH_CHECKLIST.md** - Pre-flight verification
- **TROUBLESHOOTING.md** - Common issues & fixes

### ✅ Configuration Files
- **docker-compose.local.yml** - MongoDB & Redis for local development
- **start-local.ps1** - One-click startup script (Windows)
- **start-local.sh** - One-click startup script (Mac/Linux)

### ✅ Already Configured in `.env`
```env
FLASK_ENV=development
FLASK_DEBUG=1
MONGO_URI=mongodb://localhost:27017/hide_anything_qr
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```
✅ All correct for local development - **No changes needed!**

---

## 🚀 To Run Locally RIGHT NOW

### Prerequisites (Install if missing)
1. **Python 3.11+** - https://python.org
2. **Docker Desktop** - https://docker.com/products/docker-desktop

### Start in 3 Steps

#### Step 1: Start Services (Terminal 1)
```powershell
cd c:\Users\teddy\OneDrive\Desktop\hide-anything-qr
.\start-local.ps1
```
✅ Wait for message: "✅ Services are ready!"

#### Step 2: Start Backend (Terminal 2)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
✅ Wait for: "Running on http://0.0.0.0:5000"

#### Step 3: Open Browser
```
http://localhost:5000
```
✅ Done! App is running!

---

## 📖 Full Documentation

**Choose based on your needs:**

| For You | Read This |
|---------|-----------|
| Want quickest start | **QUICK_START.md** |
| On Windows & new | **WINDOWS_SETUP.md** (👈 best) |
| Want all details | **LOCAL_SETUP.md** |
| Before launching | **PRE_LAUNCH_CHECKLIST.md** |
| Something broke | **TROUBLESHOOTING.md** |

---

## 🧪 Verify It Works

After starting the app:

```powershell
# 1. Health check
curl http://localhost:5000/api/health
# Should return: {"status":"healthy","service":...}

# 2. Open browser
# http://localhost:5000
# Should see login form

# 3. Check console (F12)
# Should be NO red errors

# 4. Try creating account
# Email: test@example.com
# Username: testuser
# Password: Test@1234
```

---

## 🔑 Key Information

### Services Running Locally
| Service | Port | URL |
|---------|------|-----|
| Flask (Backend) | 5000 | http://localhost:5000 |
| MongoDB | 27017 | mongodb://localhost:27017 |
| Redis | 6379 | redis://localhost:6379 |

### Important Files
- **Backend**: `backend/app.py` - Main Flask application
- **Frontend**: `frontend/index.html` - Web interface
- **Database**: MongoDB running in Docker
- **Cache**: Redis running in Docker

### Environment
- **Python version**: 3.9+ required
- **Python location**: `backend/.env`
- **Database**: Uses local MongoDB (hosted in Docker)
- **Cache**: Uses local Redis (hosted in Docker)

---

## ⚠️ If Something Goes Wrong

**99% of problems fixed by:**

1. **MongoDB connection error**
   ```powershell
   docker-compose -f docker-compose.local.yml restart mongodb
   ```

2. **Port 5000 already in use**
   ```powershell
   Get-Process -Id (Get-NetTCPConnection -LocalPort 5000 -ea 0).OwningProcess | Stop-Process -Force
   ```

3. **Module not found errors**
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

4. **Docker not found**
   - Install Docker Desktop and restart PowerShell

5. **Can't connect to database**
   - Make sure Docker Desktop is running
   - Run: `docker ps` to verify containers are up

**See TROUBLESHOOTING.md for full list of solutions!**

---

## 🎯 Next Steps

1. ✅ Install Python & Docker (if not already done)
2. ✅ Run the 3-step start process above
3. ✅ Create a test account
4. ✅ Explore the app features:
   - Generate QR codes
   - Share content
   - Add friends
   - Send messages
   - Check notifications

---

## 📝 Development Tips

- **Hot reload**: Flask automatically restarts when you change Python files (because `FLASK_DEBUG=1`)
- **JavaScript changes**: Press Ctrl+Shift+R to hard refresh in browser
- **CSS changes**: Same - hard refresh with Ctrl+Shift+R
- **Database persists**: Data stays in MongoDB between restarts
- **Check logs**: Look at Terminal 2 (where Flask runs) for error details

---

## 🛑 When Done

```powershell
# Stop Flask (in Terminal 2)
Ctrl + C

# Stop services (in Terminal 1)
Ctrl + C

# Or in new terminal:
docker-compose -f docker-compose.local.yml down
```

---

## 💡 Pro Tips

1. ✅ **Start services first**, then Flask app
2. ✅ **Keep both terminals open** while developing
3. ✅ **Check F12 console** if frontend has issues
4. ✅ **Check Terminal 2** if backend has issues
5. ✅ **Restart everything** if something acts weird
6. ✅ **Read error messages** - they're very helpful!

---

## 📚 All Files Created/Modified

```
✅ Created:
  - QUICK_START.md               (this file)
  - WINDOWS_SETUP.md             (Windows guide)
  - LOCAL_SETUP.md               (detailed guide)
  - PRE_LAUNCH_CHECKLIST.md      (verification)
  - TROUBLESHOOTING.md           (fixes)
  - docker-compose.local.yml     (Docker services)
  - start-local.ps1              (Windows script)
  - start-local.sh               (Mac/Linux script)

✅ Already Correct:
  - .env                         (local config)
  - backend/app.py               (Flask app)
  - backend/requirements.txt      (dependencies)
```

---

## 🎬 Ready to Start?

### **👉 For Windows Users:**
Go to: **WINDOWS_SETUP.md**

### **👉 For Mac/Linux Users:**
Go to: **LOCAL_SETUP.md**

### **👉 Quick Reference:**
Go to: **QUICK_START.md**

---

## 🆘 Need Help?

1. **Quick answer?** Check QUICK_START.md
2. **Issues?** Check TROUBLESHOOTING.md
3. **Before launching?** Check PRE_LAUNCH_CHECKLIST.md
4. **Still stuck?** Run these commands:

```powershell
# Show all running Docker containers
docker ps

# Show Docker service logs
docker-compose -f docker-compose.local.yml logs -f

# Check if ports are available
netstat -ano | findstr :5000

# Test MongoDB
mongosh mongodb://localhost:27017

# Test Redis
redis-cli.exe ping
```

---

## ✨ Success!

Your project is now fully configured for local development! 

**Everything is ready - just follow the 3 steps above to get started!**

Happy coding! 🚀

---

**Created**: March 14, 2026
**Project**: Hide Anything with QR
**Status**: ✅ Ready for local development

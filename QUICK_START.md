# 🚀 Local Development - Quick Reference

## 📚 Documentation Files Created

| File | Purpose |
|------|---------|
| **WINDOWS_SETUP.md** | 👈 **START HERE** - Windows users quick start |
| **LOCAL_SETUP.md** | Detailed setup for Mac/Linux/Windows |
| **PRE_LAUNCH_CHECKLIST.md** | Pre-flight checklist before launching |
| **TROUBLESHOOTING.md** | Common issues & solutions |
| **docker-compose.local.yml** | Docker config for local development |
| **start-local.ps1** | Windows startup script |
| **start-local.sh** | Mac/Linux startup script |

---

## ⚡ 30-Second Quick Start (Windows)

### Prerequisites
- Python 3.11+
- Docker Desktop

### Commands
```powershell
# Terminal 1: Start services
.\start-local.ps1
# Wait for "✅ Services are ready!"

# Terminal 2: Start backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
# Wait for "Running on http://0.0.0.0:5000"

# Terminal 3: Open in browser
http://localhost:5000
```

---

## 🛠️ Current Configuration

### Environment Files

**File: `.env` (Already Configured)**
```env
FLASK_ENV=development
FLASK_DEBUG=1
MONGO_URI=mongodb://localhost:27017/hide_anything_qr
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000,http://localhost:3000,http://127.0.0.1:3000
```

✅ **This is already set correctly for local development!**

### Services

**Docker Compose (docker-compose.local.yml)**
- **MongoDB**: Port 27017
- **Redis**: Port 6379
- Both configured with default credentials for development

**Flask Backend**
- **URL**: http://localhost:5000
- **Debug Mode**: Enabled (hot reload on file changes)
- **API Prefix**: `/api`

---

## 📋 Setup Checklist

- [ ] Install Python 3.11+
- [ ] Install Docker Desktop
- [ ] Navigate to project folder: `c:\Users\teddy\OneDrive\Desktop\hide-anything-qr`
- [ ] Run `.\start-local.ps1` in first terminal
- [ ] Wait 10 seconds for services to start
- [ ] Open second terminal in `backend` folder
- [ ] Create venv: `python -m venv venv`
- [ ] Activate venv: `.\venv\Scripts\Activate.ps1`
- [ ] Install deps: `pip install -r requirements.txt`
- [ ] Run app: `python app.py`
- [ ] Open browser: `http://localhost:5000`

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5000 |
| **API Health** | http://localhost:5000/api/health |
| **MongoDB** | localhost:27017 |
| **Redis** | localhost:6379 |

---

## 🚨 Common Issues (5 Most Frequent)

### 1. "Port 5000 already in use"
```powershell
$p = Get-NetTCPConnection -LocalPort 5000 -ea 0
if ($p) { Stop-Process -Id $p.OwningProcess -Force }
```

### 2. "MongoDB connection refused"
```powershell
docker-compose -f docker-compose.local.yml restart mongodb
```

### 3. "ModuleNotFoundError: flask"
```powershell
cd backend
pip install -r requirements.txt
```

### 4. "Docker not found"
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Restart PowerShell after installation

### 5. "WebSocket connection failed"
- Make sure Flask app is fully started
- Check browser console: F12 → Console tab
- Restart Flask app

**Full troubleshooting guide**: See `TROUBLESHOOTING.md`

---

## 📂 Project Structure

```
hide-anything-qr/
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Configuration (DON'T EDIT!)
│   ├── config/
│   │   └── security.py        # Security configuration
│   ├── models/                # Database models
│   ├── routes/                # API endpoints
│   ├── utils/                 # Utilities (encryption, etc)
│   └── static/uploads/        # Uploaded files
│
├── frontend/
│   ├── index.html             # Main page
│   ├── index_new.html
│   ├── scripts/               # JavaScript files
│   └── styles/                # CSS files
│
├── docker-compose.local.yml   # Docker services
├── LOCAL_SETUP.md
├── WINDOWS_SETUP.md
├── PRE_LAUNCH_CHECKLIST.md
├── TROUBLESHOOTING.md
└── .env                       # Environment config
```

---

## 🧪 Test the Setup

After everything is running:

```powershell
# 1. Test API health
curl http://localhost:5000/api/health

# 2. Check MongoDB
mongosh mongodb://localhost:27017

# 3. Check Redis
redis-cli.exe ping

# 4. Open in browser
# http://localhost:5000
# F12 to check console for errors
```

---

## 🎯 Development Workflow

### Daily Startup
```powershell
# Terminal 1: Services
.\start-local.ps1

# Terminal 2: Backend
cd backend
.\venv\Scripts\Activate.ps1
python app.py

# Terminal 3: Browser
http://localhost:5000
```

### Code Changes
- **Python files**: Auto-reload enabled (FLASK_DEBUG=1)
- **JavaScript files**: Hard refresh (Ctrl+Shift+R)
- **CSS files**: Hard refresh to see changes

### Make a Commit
```powershell
git add .
git commit -m "Description of changes"
git push origin main
```

---

## 📚 Documentation Map

```
👤 **You are here:** Quick Reference
    ├── 👶 Start: WINDOWS_SETUP.md (easiest)
    ├── 📖 Details: LOCAL_SETUP.md (detailed)
    ├── ✅ Verify: PRE_LAUNCH_CHECKLIST.md (before running)
    └── 🔧 Fix: TROUBLESHOOTING.md (if errors)
```

---

## ✨ Pro Tips

1. **Keep Docker open**: Close Docker Desktop = no databases
2. **Use virtual env**: Always activate venv before `pip install`
3. **Check console**: F12 → Console tab for frontend errors
4. **Read error logs**: Terminal output tells you what's wrong
5. **Restart fixes most things**: Restart Flask if errors happen
6. **Git frequently**: Commit often to save progress
7. **Check network**: F12 → Network tab to debug API calls

---

## 🎬 Next Steps

1. ✅ Follow **WINDOWS_SETUP.md** or **LOCAL_SETUP.md**
2. ✅ Use **PRE_LAUNCH_CHECKLIST.md** before running
3. ✅ If issues: Check **TROUBLESHOOTING.md**
4. ✅ Create test account and explore the app!


---

## 📞 Quick Help Commands

```powershell
# View this file
type QUICK_START.md

# Check all services running
docker ps

# View service logs
docker-compose -f docker-compose.local.yml logs -f

# Stop everything
docker-compose -f docker-compose.local.yml down

# Start fresh (clear all data)
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up -d
```

---

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ `http://localhost:5000` loads without errors
- ✅ Can see login/register form
- ✅ F12 Console shows no red errors
- ✅ Can create an account
- ✅ Can login to dashboard
- ✅ Can generate QR codes

---

**Happy developing! 🚀**

Need help? Check the docs or see TROUBLESHOOTING.md

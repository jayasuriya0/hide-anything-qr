# 🚀 Quick Deploy to Render.com

## What You Need

✅ MongoDB Atlas connection string  
✅ Upstash Redis connection string  
✅ GitHub account  
✅ Render.com account  

---

## 📋 Step-by-Step (10 minutes)

### 1️⃣ Configure MongoDB Atlas

**Setup Database User**:
1. Go to **Database Access** → Add user with username `hide` and a strong password
2. Set privileges to **Read and write to any database**

**Whitelist Render IPs**:
1. Go to **Network Access** → **Add IP Address**
2. Add: `0.0.0.0/0` (Allow from anywhere for Render)
3. Description: "Render deployment"
4. Click **Confirm**

**Get Connection String**:
```
mongodb+srv://hide:YOUR_PASSWORD@cluster.mongodb.net/?appName=hideanything
```

**Upstash Redis**:
```
rediss://default:password@endpoint.upstash.io:6379
```

---

### 2️⃣ Push to GitHub

```powershell
# In your project folder
git init
git add .
git commit -m "Ready for deployment"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/hide-anything-qr.git
git branch -M main
git push -u origin main
```

---

### 3️⃣ Deploy to Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in:
   - **Name**: `hideanything-qr`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT --worker-class eventlet --timeout 120 app:app`

5. Click **"Advanced"** and add these **Environment Variables**:

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `MONGO_URI` | Your MongoDB connection string |
| `REDIS_URL` | Your Upstash Redis URL |
| `SECRET_KEY` | Click "Generate" button |
| `JWT_SECRET_KEY` | Click "Generate" button (different!) |
| `ALLOWED_ORIGINS` | `https://hideanything-qr.onrender.com` |
| `SESSION_COOKIE_SECURE` | `True` |

6. Click **"Create Web Service"**

---

### 4️⃣ Wait for Deployment (5-10 minutes)

Watch the logs as Render:
- ✅ Installs Python dependencies
- ✅ Builds your application
- ✅ Starts the server
- ✅ Provides HTTPS URL

---

### 5️⃣ Test Your Live Site!

Visit: `https://hideanything-qr.onrender.com`

- Create an account
- Generate a QR code
- Share it!

---

## 🎉 You're Live!

Your app is now:
- ✅ Hosted on HTTPS
- ✅ Connected to MongoDB
- ✅ Using Redis for rate limiting
- ✅ Fully secured with secret keys
- ✅ Accessible worldwide

---

## 💡 Tips

**Free Tier**: Service sleeps after 15 min of inactivity. First request wakes it up (takes ~30 seconds).

**Custom Domain**: Go to Render Dashboard → Settings → Custom Domain to add your own domain.

**Logs**: Click "Logs" tab in Render dashboard to see what's happening.

**Updates**: Just push to GitHub - Render auto-deploys!

---

## 🆘 Need Help?

Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting!

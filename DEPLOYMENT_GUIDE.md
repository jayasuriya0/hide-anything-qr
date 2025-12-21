# 🚀 Render.com Deployment Guide

## Prerequisites ✅
- [x] MongoDB Atlas account created
- [x] Render.com account created  
- [x] Upstash Redis account created
- [ ] GitHub repository (needed for Render)

---

## Step 1: Setup MongoDB Atlas

1. **Go to MongoDB Atlas Dashboard**: https://cloud.mongodb.com/
2. **Create a FREE Cluster** (M0 - 512MB)
   - Cloud Provider: AWS
   - Region: Choose closest to Oregon (us-west-2)
   - Cluster Name: `hideanything-cluster`

3. **Create Database User**:
   - Click "Database Access" → "Add New Database User"
   - Authentication: Password
   - Username: `hideanything_user`
   - Password: **Generate a strong password** (save it!)
   - Database User Privileges: "Read and write to any database"
   - Click "Add User"

4. **Whitelist All IPs** (for Render to connect):
   - Click "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere"
   - IP: `0.0.0.0/0`
   - Click "Confirm"

5. **Get Connection String**:
   - Click "Database" → "Connect"
   - Choose "Connect your application"
   - Driver: Python, Version: 3.11 or later
   - Copy the connection string:
     ```
     mongodb+srv://hideanything_user:<password>@hideanything-cluster.xxxxx.mongodb.net/hide_anything_qr?retryWrites=true&w=majority
     ```
   - **Replace `<password>` with your actual password**
   - **Add database name** at the end: `/hide_anything_qr`

   Example:
   ```
   mongodb+srv://hideanything_user:MySecurePass123@hideanything-cluster.abc123.mongodb.net/hide_anything_qr?retryWrites=true&w=majority
   ```

---

## Step 2: Setup Upstash Redis

1. **Go to Upstash Dashboard**: https://console.upstash.com/
2. **Create Redis Database**:
   - Click "Create Database"
   - Name: `hideanything-redis`
   - Type: Regional
   - Region: Choose `us-west-1` (closest to Render Oregon)
   - TLS: Enabled ✅
   - Click "Create"

3. **Get Connection URL**:
   - Click on your database
   - Scroll to "REST API" section
   - Copy the **"UPSTASH_REDIS_REST_URL"**:
     ```
     rediss://default:XXXXXXXXXXXX@us1-full-url.upstash.io:6379
     ```

---

## Step 3: Push Code to GitHub

1. **Create GitHub Repository**:
   ```powershell
   # Initialize git (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit - Ready for deployment"
   
   # Create repo on GitHub (via web): https://github.com/new
   # Repository name: hide-anything-qr
   # Public or Private: Your choice
   
   # Add remote and push
   git remote add origin https://github.com/YOUR_USERNAME/hide-anything-qr.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 4: Deploy to Render

### Option A: Using Blueprint (Automatic - Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Blueprint"**
3. **Connect GitHub Repository**:
   - Click "Connect Account" if not connected
   - Select your `hide-anything-qr` repository
   - Click "Connect"

4. **Render will detect `render.yaml`** and show deployment plan
5. **Click "Apply"** to create the service

### Option B: Manual Setup

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub Repository**:
   - Select your `hide-anything-qr` repository
   - Click "Connect"

4. **Configure Service**:
   - **Name**: `hideanything-qr`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT --worker-class eventlet --timeout 120 app:app
     ```
   - **Plan**: Free

5. **Add Environment Variables** (Click "Advanced" → "Add Environment Variable"):

   | Key | Value | Notes |
   |-----|-------|-------|
   | `PYTHON_VERSION` | `3.11.0` | Python version |
   | `FLASK_ENV` | `production` | Production mode |
   | `FLASK_DEBUG` | `0` | Disable debug |
   | `SESSION_COOKIE_SECURE` | `True` | HTTPS cookies |
   | `MONGO_URI` | `mongodb+srv://...` | **From Step 1** |
   | `REDIS_URL` | `rediss://...` | **From Step 2** |
   | `SECRET_KEY` | Click **"Generate"** | Auto-generate |
   | `JWT_SECRET_KEY` | Click **"Generate"** | Auto-generate (different from above!) |
   | `ALLOWED_ORIGINS` | `https://hideanything-qr.onrender.com` | Your Render URL (update after deploy) |

6. **Click "Create Web Service"**

---

## Step 5: Update ALLOWED_ORIGINS

1. **After first deployment completes**, you'll get a URL like:
   ```
   https://hideanything-qr.onrender.com
   ```

2. **Update Environment Variable**:
   - Go to your service dashboard
   - Click "Environment"
   - Edit `ALLOWED_ORIGINS` to:
     ```
     https://hideanything-qr.onrender.com
     ```
   - Click "Save Changes"
   - Service will auto-redeploy

---

## Step 6: Test Your Deployment

1. **Visit Your Site**:
   ```
   https://hideanything-qr.onrender.com
   ```

2. **Test Registration**:
   - Create a new account
   - Should work without errors

3. **Test QR Generation**:
   - Generate a QR code
   - Scan it and verify decoding works

4. **Check Logs** (if issues):
   - Go to Render Dashboard
   - Click "Logs" tab
   - Look for errors in red

---

## 🎉 You're Live!

Your application is now deployed at:
```
https://hideanything-qr.onrender.com
```

### Important Notes:

⚠️ **Free Tier Limitations**:
- Service **sleeps after 15 minutes of inactivity**
- First request after sleep takes **~30 seconds** to wake up
- 750 hours/month limit (enough for always-on if single service)

💡 **To Keep It Always-On**:
- Upgrade to paid plan ($7/month)
- OR use a service like UptimeRobot to ping every 10 minutes

🔒 **Security Checklist**:
- [x] HTTPS enabled automatically
- [x] CORS restricted to your domain
- [x] Strong secret keys auto-generated
- [x] Session cookies secure
- [x] MongoDB authentication enabled
- [x] Redis TLS enabled

---

## Troubleshooting

### Service Won't Start
- Check "Logs" tab for errors
- Verify all environment variables are set
- Ensure MongoDB connection string is correct (password special chars?)

### CORS Errors
- Make sure `ALLOWED_ORIGINS` matches your actual Render URL
- Include `https://` prefix
- No trailing slash

### Database Connection Failed
- Verify MongoDB IP whitelist includes `0.0.0.0/0`
- Check connection string format
- Ensure database user has correct permissions

### Redis Connection Failed
- Verify Upstash Redis URL format starts with `rediss://`
- Check if TLS is enabled in Upstash

---

## Optional: Custom Domain

To use your own domain (e.g., `hideanything.com`):

1. **Go to Render Dashboard** → Your Service → "Settings"
2. **Click "Add Custom Domain"**
3. **Enter your domain**: `hideanything.com` and `www.hideanything.com`
4. **Add DNS Records** at your domain registrar:
   ```
   Type: CNAME
   Name: @
   Value: hideanything-qr.onrender.com
   
   Type: CNAME
   Name: www
   Value: hideanything-qr.onrender.com
   ```
5. **Wait for DNS propagation** (5-60 minutes)
6. **Update `ALLOWED_ORIGINS`** environment variable to include your custom domain

---

## Support

- **Render Docs**: https://render.com/docs
- **MongoDB Docs**: https://docs.mongodb.com/
- **Upstash Docs**: https://docs.upstash.com/

Need help? Check the logs first, they usually show the exact error!

# How to Fix the Login Error - MongoDB Not Running

## The Problem
Your backend can't connect to MongoDB, causing the 500 error when trying to login.

## Quick Solution 1: Start MongoDB Manually

Open a **NEW PowerShell as Administrator** and run:

```powershell
# Method 1: Start as Windows Service
net start MongoDB

# OR Method 2: Start mongod directly
& "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
```

Then restart your backend server.

---

## Quick Solution 2: Use MongoDB Atlas (Cloud - Free Tier)

1. **Create a free MongoDB Atlas account**: https://www.mongodb.com/cloud/atlas/register

2. **Create a cluster** (M0 Free tier)

3. **Get your connection string**:
   - Click "Connect" → "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

4. **Update your `.env` file**:
   ```env
   MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hide_anything_qr?retryWrites=true&w=majority
   ```

5. **Restart your backend**

---

## Quick Solution 3: Use SQLite Alternative (Emergency)

If MongoDB is too complex, I can create a quick SQLite-based alternative for local development.

---

## Verify MongoDB is Working

After starting MongoDB, test the connection:

```powershell
# Test if MongoDB is listening
Test-NetConnection localhost -Port 27017
```

If it shows `TcpTestSucceeded: True`, MongoDB is running!

# 📤 Push to GitHub - Step by Step Guide

## Prerequisites
- Git installed on your computer
- GitHub account created

---

## Step 1: Install Git (if not installed)

### Check if Git is installed:
```powershell
git --version
```

### If not installed, download from:
https://git-scm.com/download/win

**During installation, use these settings:**
- ✅ Use Visual Studio Code as Git's default editor
- ✅ Git from the command line and also from 3rd-party software
- ✅ Use bundled OpenSSH
- ✅ Use the OpenSSL library
- ✅ Checkout Windows-style, commit Unix-style line endings
- ✅ Use MinTTY
- ✅ Default (fast-forward or merge)
- ✅ Git Credential Manager
- ✅ Enable file system caching

---

## Step 2: Configure Git (First Time Setup)

```powershell
# Set your name (will appear in commits)
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

## Step 3: Create GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `hide-anything-qr`
   - **Description**: "Secure QR code generator and sharing platform"
   - **Visibility**: Choose **Public** or **Private**
   - ❌ **DO NOT** initialize with README (we already have files)
   - ❌ **DO NOT** add .gitignore (we created one)
   - ❌ **DO NOT** add license yet
3. Click **"Create repository"**
4. **Keep this page open** - you'll need the URL

---

## Step 4: Initialize Git in Your Project

Open PowerShell in your project folder:

```powershell
# Navigate to your project
cd C:\Users\teddy\OneDrive\Desktop\hide-anything-qr

# Initialize Git repository
git init

# Check status (see what files will be added)
git status
```

---

## Step 5: Add Files to Git

```powershell
# Add all files (respects .gitignore)
git add .

# Check what was staged
git status

# You should see files in green (staged)
# Files in .gitignore won't appear
```

---

## Step 6: Create Your First Commit

```powershell
# Commit with a message
git commit -m "Initial commit - HideAnything QR application ready for deployment"

# Verify commit was created
git log
```

---

## Step 7: Connect to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```powershell
# Add GitHub as remote repository
git remote add origin https://github.com/YOUR_USERNAME/hide-anything-qr.git

# Verify remote was added
git remote -v
```

Example:
```powershell
git remote add origin https://github.com/johndoe/hide-anything-qr.git
```

---

## Step 8: Push to GitHub

```powershell
# Rename branch to 'main' (GitHub's default)
git branch -M main

# Push code to GitHub
git push -u origin main
```

**First time?** You'll be prompted to authenticate:
1. A browser window will open
2. Sign in to GitHub
3. Click "Authorize"
4. Return to PowerShell - push will continue

---

## Step 9: Verify on GitHub

1. Go to: `https://github.com/YOUR_USERNAME/hide-anything-qr`
2. You should see all your files
3. ✅ README.md should be displayed
4. ✅ Check that `.env` files are NOT there (gitignored)
5. ✅ Check that `__pycache__/` folders are NOT there

---

## 🎉 Success! Your code is now on GitHub!

Your repository URL:
```
https://github.com/YOUR_USERNAME/hide-anything-qr
```

---

## 📝 Daily Workflow (Making Updates)

### After making changes to your code:

```powershell
# 1. Check what changed
git status

# 2. Add changed files
git add .

# 3. Commit with descriptive message
git commit -m "Add new feature: XYZ"

# 4. Push to GitHub
git push
```

---

## 🔧 Common Git Commands

```powershell
# See commit history
git log

# See recent commits (one line each)
git log --oneline

# See what changed in files
git diff

# Undo changes to a file (before adding)
git checkout -- filename.py

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch into main
git checkout main
git merge feature-name

# Pull latest changes from GitHub
git pull
```

---

## 🆘 Troubleshooting

### Problem: "fatal: remote origin already exists"
```powershell
# Remove old remote and add new one
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/hide-anything-qr.git
```

### Problem: "refusing to merge unrelated histories"
```powershell
git pull origin main --allow-unrelated-histories
```

### Problem: Large files rejected
```powershell
# Check file sizes
git ls-files -s | awk '{print $4, $2}' | sort -n

# Remove file from git (keep local copy)
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push
git commit -m "Remove large file"
git push
```

### Problem: Accidentally committed .env file
```powershell
# Remove from git (keep local)
git rm --cached backend/.env

# Make sure it's in .gitignore
echo ".env" >> .gitignore

# Commit the removal
git commit -m "Remove .env from repository"
git push

# ⚠️ Important: Go to GitHub → Settings → Secrets
# And regenerate all keys/passwords that were exposed!
```

---

## 🔐 Security Checklist Before Pushing

✅ `.gitignore` file created  
✅ `.env` files are gitignored  
✅ No passwords in code  
✅ No API keys in code  
✅ No database credentials in code  
✅ `__pycache__` folders gitignored  
✅ Virtual environment (`.venv`) gitignored  

---

## 📚 Next Step: Deploy to Render

Once your code is on GitHub, follow:
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - Fast deployment (10 min)
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed guide

---

## 🎯 Quick Reference

```powershell
# The three essential commands you'll use daily:
git add .
git commit -m "Your message here"
git push
```

That's it! You're now a Git user! 🚀

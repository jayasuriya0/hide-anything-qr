# 🔒 Security & Production Deployment Guide

## ✅ Security Improvements Implemented

### 1. **Restricted CORS**
- ❌ Before: `origins: "*"` (allowed ALL websites)
- ✅ After: Only specified domains in `ALLOWED_ORIGINS`
- Configure in `.env`: `ALLOWED_ORIGINS=https://yourdomain.com`

### 2. **Rate Limiting**
- Added Flask-Limiter with Redis backend
- Limits per endpoint:
  - Auth endpoints: 10 requests/minute
  - Upload endpoints: 20 requests/hour
  - Decode endpoints: 100 requests/hour
  - General API: 1000 requests/hour

### 3. **Input Validation & Sanitization**
- Username: 3-30 chars, alphanumeric only
- Email: Proper RFC validation
- Password: Min 8 chars, requires uppercase, lowercase, numbers
- Phone: International format validation
- Text content: Max 10,000 chars, XSS protection
- All inputs sanitized with bleach library

### 4. **Strong Key Enforcement**
- No fallback dev keys in production
- Application fails fast if keys are missing/weak
- Validation on startup
- Generate keys: `python -c "import secrets; print(secrets.token_hex(32))"`

### 5. **File Upload Security**
- File type validation by extension
- File size limits by type (10-50MB)
- Null byte injection protection
- Filename sanitization
- Proper MIME type checking

### 6. **Security Headers**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy` (CSP)
- `Referrer-Policy`
- `Permissions-Policy`

### 7. **Session Security**
- `HttpOnly` cookies (prevent JavaScript access)
- `Secure` flag in production (HTTPS only)
- `SameSite: Lax` (CSRF protection)

### 8. **Error Handling**
- No sensitive info leaked in production errors
- Proper HTTP status codes
- Rate limit error responses (429)
- File too large errors (413)

---

## 🚀 Production Deployment Steps

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Generate Strong Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate JWT_SECRET_KEY (different from above!)
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

### Step 3: Configure MongoDB with Authentication

```bash
# Start MongoDB shell
mongosh

# Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "YOUR_STRONG_PASSWORD_HERE",
  roles: [ { role: "root", db: "admin" } ]
})

# Create app user
use hide_anything_qr
db.createUser({
  user: "hideanything_user",
  pwd: "ANOTHER_STRONG_PASSWORD",
  roles: [ { role: "readWrite", db: "hide_anything_qr" } ]
})

# Exit and restart MongoDB with auth
mongod --auth --bind_ip 127.0.0.1
```

### Step 4: Configure Redis with Password

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Add this line:
requirepass YOUR_STRONG_REDIS_PASSWORD

# Restart Redis
sudo systemctl restart redis
```

### Step 5: Setup SSL/HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
# Test renewal: sudo certbot renew --dry-run
```

### Step 6: Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/hide-anything-qr

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/hide-anything-qr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Create Production .env File

```bash
cp .env.production .env
nano .env

# Update ALL values:
# - SECRET_KEY (from Step 2)
# - JWT_SECRET_KEY (from Step 2)
# - MONGO_URI (with your passwords from Step 3)
# - REDIS_URL (with your password from Step 4)
# - ALLOWED_ORIGINS (your actual domain)
```

### Step 8: Create Systemd Service

```ini
# /etc/systemd/system/hide-anything-qr.service

[Unit]
Description=Hide Anything QR Application
After=network.target mongodb.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/hide-anything-qr/backend
Environment="PATH=/path/to/hide-anything-qr/.venv/bin"
ExecStart=/path/to/hide-anything-qr/.venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --worker-class eventlet \
    --timeout 120 \
    --access-logfile /var/log/hide-anything-qr/access.log \
    --error-logfile /var/log/hide-anything-qr/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/hide-anything-qr
sudo chown www-data:www-data /var/log/hide-anything-qr

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hide-anything-qr
sudo systemctl start hide-anything-qr

# Check status
sudo systemctl status hide-anything-qr
```

### Step 9: Setup Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verify
sudo ufw status
```

### Step 10: Setup Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-hideanything.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/hide-anything-qr"
DATE=$(date +%Y%m%d_%H%M%S)

# MongoDB backup
mongodump --uri="mongodb://admin:PASSWORD@localhost:27017/hide_anything_qr?authSource=admin" \
    --out="$BACKUP_DIR/mongo_$DATE"

# File uploads backup
rsync -av /path/to/hide-anything-qr/backend/static/uploads/ \
    "$BACKUP_DIR/uploads_$DATE/"

# Keep only last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-hideanything.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-hideanything.sh
```

---

## 🔍 Security Testing

### Before Launch Checklist

```bash
# 1. Test with security scanner
pip install safety
safety check

# 2. Check for outdated packages
pip list --outdated

# 3. Test SSL configuration
https://www.ssllabs.com/ssltest/

# 4. Test security headers
https://securityheaders.com/

# 5. Test rate limiting
# Try multiple rapid requests and verify 429 errors

# 6. Verify no debug mode
curl https://yourdomain.com/nonexistent
# Should return generic 404, not detailed error

# 7. Test CORS
# Try accessing API from unauthorized origin - should fail

# 8. Verify HTTPS redirect
curl -I http://yourdomain.com
# Should return 301 to https://
```

---

## 📊 Monitoring & Maintenance

### Setup Error Tracking (Sentry)

```bash
pip install sentry-sdk[flask]
```

Add to `app.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

if os.environ.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )
```

### Monitor Logs

```bash
# Application logs
sudo tail -f /var/log/hide-anything-qr/error.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# System logs
sudo journalctl -u hide-anything-qr -f
```

### Regular Maintenance

```bash
# Weekly: Update dependencies
pip install --upgrade -r requirements.txt

# Monthly: Security audit
pip-audit

# Monthly: Check SSL expiry
sudo certbot certificates

# Monthly: Analyze logs for attacks
sudo fail2ban-client status

# Quarterly: Review and rotate API keys
```

---

## 🚨 Still Required (Not Yet Implemented)

1. **2FA / MFA** - Add two-factor authentication
2. **Email Verification** - Verify user emails on signup
3. **Virus Scanning** - Scan uploaded files (ClamAV)
4. **Content Moderation** - Review user-generated content
5. **IP Blocking** - Ban malicious IPs
6. **Audit Logging** - Log all security events
7. **CAPTCHA** - Prevent bot registrations
8. **Database Encryption** - Encrypt MongoDB data at rest
9. **Secrets Management** - Use HashiCorp Vault or AWS Secrets Manager
10. **Penetration Testing** - Hire security consultant

---

## 📞 Security Incident Response

If you detect a security breach:

1. **Immediately**: Take site offline (`sudo systemctl stop hide-anything-qr`)
2. **Isolate**: Disconnect affected servers
3. **Investigate**: Review logs for attack vectors
4. **Patch**: Fix vulnerability
5. **Reset**: Rotate all keys, passwords, and tokens
6. **Notify**: Inform affected users
7. **Review**: Conduct post-mortem
8. **Improve**: Implement additional security measures

---

## ✅ Production Ready?

**After implementing all steps above**:
- ✅ HTTPS with valid SSL certificate
- ✅ Strong random keys (64+ chars)
- ✅ MongoDB authentication enabled
- ✅ Redis password protected
- ✅ CORS restricted to your domain
- ✅ Rate limiting active
- ✅ Input validation in place
- ✅ Security headers configured
- ✅ Firewall configured
- ✅ Backups automated
- ✅ Monitoring setup
- ✅ Error tracking enabled

**You are now ready for production! 🚀**

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Security Tips](https://www.nginx.com/blog/mitigating-ddos-attacks-with-nginx-and-nginx-plus/)

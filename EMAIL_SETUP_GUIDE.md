# Email Configuration Guide

## Issues Fixed

### 1. ✅ Yanked Package Version
**Problem**: `email-validator==2.1.0` was yanked by maintainer

**Solution**: Updated to `email-validator==2.1.2` in [requirements.txt](backend/requirements.txt)

### 2. ✅ Missing SMTP Credentials Check
**Problem**: App showed "Email sent successfully" even when SMTP credentials weren't configured

**Solution**: 
- Added upfront validation in [routes/content.py](backend/routes/content.py) - returns 503 error if credentials missing
- Enhanced error messages in [utils/email_notifier.py](backend/utils/email_notifier.py)

## Setting Up Email on Render

Your local `.env` has email configured, but **Render needs these environment variables**:

### Required Environment Variables for Render

Go to **Render Dashboard → Your Service → Environment** and add:

| Variable | Value | Description |
|----------|-------|-------------|
| `SMTP_HOST` | `smtp.gmail.com` | Gmail SMTP server |
| `SMTP_PORT` | `587` | SMTP port for TLS |
| `SMTP_USER` | ` | Your Gmail address |
| `SMTP_PASSWORD` |  | Your Gmail App Password |
| `SMTP_TLS` | `true` | Enable TLS encryption |

### ⚠️ Important: Gmail App Password

The password in your `.env` appears to be a Gmail App Password (16 characters). This is correct!

**If email still doesn't work:**

1. **Enable 2-Factor Authentication** on your Gmail account:
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Create a new App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Hide Anything QR"
   - Copy the 16-character password
   - Update `SMTP_PASSWORD` in Render with this password

3. **Verify your Gmail settings**:
   - Go to Gmail → Settings → Forwarding and POP/IMAP
   - Make sure "IMAP access" is enabled

## Testing Email Locally

1. **Check your `.env` file** (should already have these):
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=xyzx@gmail.com
   SMTP_PASSWORD=************
   SMTP_TLS=true
   ```

2. **Test email function**:
   ```bash
   cd backend
   python test_email.py
   ```

3. **Check console output**:
   - ✅ Should see: "✅ Email sent successfully"
   - ❌ If you see credential errors, regenerate App Password

## Testing Email on Production

After setting environment variables in Render:

1. **Redeploy** (or wait for auto-deploy)

2. **Check Render logs** for:
   ```
   📧 Attempting to send email to: test@example.com
   📮 Using SMTP: smtp.gmail.com:587
   🔌 Connecting to smtp.gmail.com:587...
   🔒 Starting TLS encryption...
   🔑 Logging in as xyz@gmail.com...
   📤 Sending email to test@example.com...
   ✅ Email sent successfully!
   ```

3. **Test from UI**:
   - Generate a QR code
   - Click "Share via Email"
   - Enter recipient email
   - Check Render logs for email status

## Common Issues

### Issue: "Email service not configured" (503 error)
**Solution**: SMTP environment variables not set in Render dashboard

### Issue: "Authentication failed"
**Solution**: 
- Make sure you're using an App Password (not your regular Gmail password)
- Regenerate App Password in Google Account settings

### Issue: "Connection timeout"
**Solution**:
- Check if Render has outbound SMTP access (port 587)
- Some hosting providers block SMTP ports

### Issue: Email takes too long
**Solution**: Already implemented - emails are sent in background thread, UI returns immediately

## Alternative Email Services

If Gmail doesn't work on Render, consider these alternatives:

### 1. SendGrid (Free tier: 100 emails/day)
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_TLS=true
```

### 2. Mailgun (Free tier: 5,000 emails/month)
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
SMTP_TLS=true
```

### 3. Amazon SES (Free tier: 62,000 emails/month)
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
SMTP_TLS=true
```

## Deployment Steps

1. **Commit changes**:
   ```bash
   git add .
   git commit -m "Fix email sending - update validator & add credential checks"
   git push origin main
   ```

2. **Set Render environment variables** (as listed above)

3. **Wait for deployment** and test

## Verification Checklist

- [ ] Updated `email-validator` to 2.1.2
- [ ] Set all SMTP environment variables in Render
- [ ] Verified Gmail App Password is correct
- [ ] Tested email sending after deployment
- [ ] Checked Render logs for email status
- [ ] Received test email successfully

---

After deployment, the email feature should work correctly! 📧✨

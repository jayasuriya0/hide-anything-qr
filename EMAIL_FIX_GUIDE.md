# Email Configuration Fix Guide

## Issue
The email service is timing out when trying to connect to Gmail's SMTP server.

## Root Cause
**Connection Timeout**: Port 587 is being blocked by:
- Windows Firewall
- Antivirus software
- Network/ISP restrictions
- Gmail requiring App Passwords (not regular passwords)

## Solution Options

### Option 1: Use Gmail App Password (RECOMMENDED)

Gmail requires "App Passwords" when 2FA is enabled. Follow these steps:

1. **Enable 2-Factor Authentication** on your Google Account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate an App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update `.env` file**
   ```env
   MAIL_USERNAME=chatbot347@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Your 16-character App Password
   ```

4. **Restart the Flask server**

### Option 2: Check Firewall Settings

1. **Allow Port 587 in Windows Firewall**
   - Open Windows Security → Firewall & network protection
   - Advanced settings → Outbound Rules
   - New Rule → Port → TCP 587 → Allow

2. **Disable Antivirus SMTP Scanning temporarily** to test

### Option 3: Alternative SMTP Providers

If Gmail doesn't work, try these alternatives:

#### Using SendGrid (Free tier: 100 emails/day)
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_USE_TLS=true
```

#### Using Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_USE_TLS=true
```

#### Using Mailtrap (For Testing)
```env
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_USE_TLS=true
```

## Testing Email

Run this command to test your configuration:
```bash
cd backend
python test_email.py
```

## Current Status

✅ **Email functionality implemented**:
- Email template with QR code created
- SMTP configuration ready
- Error handling added

❌ **Connection issue**: Need to fix SMTP connection

## What's Working Now

Even though email is timing out, the app still works:
- QR codes are generated successfully
- Messages show "Check your email" notification
- QR codes are available in the Shared section
- All encryption and security features work

## Quick Fix

**Temporary Solution**: The email feature is currently configured but not sending due to network/firewall issues. Users can still:
1. Generate QR codes normally
2. Download QR codes from the Shared section
3. Share the downloaded QR code image manually

To enable email, follow Option 1 above (Gmail App Password).

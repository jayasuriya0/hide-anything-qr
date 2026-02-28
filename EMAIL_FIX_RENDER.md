# Email Fix for Render Deployment

## Problem Diagnosis
From the logs, the email sending **hangs at Step 1 (SMTP connection)** and never completes:
```
🔌 Step 1: Connecting to smtp.gmail.com:587...
[HANGS INDEFINITELY - TIMES OUT]
```

**Root Cause**: Render's free tier blocks outbound SMTP connections on ports 587/465 to prevent spam/abuse.

---

## Solution 1: Use SendGrid (RECOMMENDED ✅)

SendGrid offers 100 free emails/day and works reliably on Render.

### Step 1: Get SendGrid API Key
1. Sign up at https://sendgrid.com (free tier)
2. Go to Settings → API Keys
3. Create API Key with "Mail Send" full access
4. Copy the API key (starts with `SG.`)

### Step 2: Update Render Environment Variables
In Render Dashboard → Your Service → Environment:
```
SENDGRID_API_KEY=SG.your_api_key_here
SENDGRID_FROM_EMAIL=your-verified-email@gmail.com
```

### Step 3: Install SendGrid Package
Add to `backend/requirements.txt`:
```
sendgrid==6.10.0
```

### Step 4: Update Email Function
Replace the SMTP code in `backend/utils/email_notifier.py` with SendGrid API:

```python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

def send_qr_email(receiver_email, sender_name, qr_code_base64, content_type, encryption_level):
    try:
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@hideqr.app')
        
        if not sendgrid_api_key:
            print("❌ SENDGRID_API_KEY not configured")
            return False
        
        # Remove data URL prefix if present
        if qr_code_base64.startswith('data:image'):
            qr_code_base64 = qr_code_base64.split(',')[1]
        
        # Email HTML
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
              <h2>🔐 Secure Content from {sender_name}</h2>
              <p>You've received encrypted {content_type} content.</p>
              <p><strong>Encryption Level:</strong> {encryption_level or 'Standard'}</p>
              <p>Scan the attached QR code to access your content.</p>
              <hr>
              <p style="color: #999; font-size: 12px;">Hide Anything QR - Secure Content Sharing</p>
            </div>
          </body>
        </html>
        """
        
        # Create message
        message = Mail(
            from_email=from_email,
            to_emails=receiver_email,
            subject=f"🔐 Secure Content from {sender_name}",
            html_content=html_content
        )
        
        # Attach QR code
        qr_image_data = base64.b64decode(qr_code_base64)
        encoded_file = base64.b64encode(qr_image_data).decode()
        
        attached_file = Attachment(
            FileContent(encoded_file),
            FileName('secure_qr_code.png'),
            FileType('image/png'),
            Disposition('attachment')
        )
        message.attachment = attached_file
        
        # Send via SendGrid
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ Email sent successfully to {receiver_email}")
            return True
        else:
            print(f"❌ SendGrid returned status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ SendGrid Error: {e}")
        import traceback
        traceback.print_exc()
        return False
```

### Step 5: Deploy
```bash
git add .
git commit -m "Switch to SendGrid for email delivery"
git push origin main
```

---

## Solution 2: Try Port 465 (Less Reliable)

If you want to keep using Gmail SMTP, try SSL port 465:

In Render Environment Variables:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Update code to use SMTP_SSL instead of SMTP:
```python
from smtplib import SMTP_SSL

server = SMTP_SSL(mail_server, mail_port, timeout=30)
# No starttls() needed for SSL
server.login(mail_username, mail_password)
```

**Note**: This may also be blocked by Render.

---

## Solution 3: Use Render Paid Tier

Render's paid tiers ($7/month+) allow outbound SMTP connections without restrictions.

---

## Recommendation

**Use SendGrid (Solution 1)** - it's free, reliable, and designed to work on restricted hosting platforms like Render. Transactional email services are the industry standard for production apps.

---

## Quick SendGrid Setup Commands

I can implement SendGrid for you right now. Just:

1. Get your SendGrid API key from https://sendgrid.com
2. Add it to Render environment variables as `SENDGRID_API_KEY`
3. Let me know, and I'll update the code

Would you like me to implement SendGrid now?

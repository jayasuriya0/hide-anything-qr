import os
import base64
import requests

def send_qr_email(receiver_email, sender_name, qr_code_base64, content_type, encryption_level):
    """
    Send QR code via email using Mailgun (works on Render, no domain verification needed)
    
    Args:
        receiver_email: Email address of the receiver
        sender_name: Username of the sender
        qr_code_base64: Base64 encoded QR code image
        content_type: Type of content (text/file)
        encryption_level: Encryption level used
    """
    try:
        # Get Mailgun configuration from environment
        mailgun_api_key = os.environ.get('MAILGUN_API_KEY', '')
        mailgun_domain = os.environ.get('MAILGUN_DOMAIN', '')
        from_email = os.environ.get('MAILGUN_FROM_EMAIL', f'HideQR <noreply@{mailgun_domain}>')
        
        if not mailgun_api_key or not mailgun_domain:
            print("=" * 60)
            print("❌ MAILGUN NOT CONFIGURED")
            print("=" * 60)
            print(f"MAILGUN_API_KEY: {'Set' if mailgun_api_key else 'NOT SET'}")
            print(f"MAILGUN_DOMAIN: {'Set' if mailgun_domain else 'NOT SET'}")
            print("\n📋 To fix this:")
            print("1. Sign up at https://signup.mailgun.com (free 5000 emails/month)")
            print("2. Get API key from dashboard")
            print("3. Add to Render Environment Variables:")
            print("   MAILGUN_API_KEY=your_api_key_here")
            print("   MAILGUN_DOMAIN=sandboxXXX.mailgun.org")
            print("   MAILGUN_FROM_EMAIL=HideQR <noreply@sandboxXXX.mailgun.org>")
            print("=" * 60)
            return False
        
        print("=" * 80)
        print(f"📧 SENDING EMAIL VIA MAILGUN TO: {receiver_email}")
        print(f"📨 From: {from_email}")
        print(f"👤 Sender Name: {sender_name}")
        print(f"📦 Content Type: {content_type}")
        print(f"🔐 Encryption Level: {encryption_level}")
        print(f"🌐 Mailgun Domain: {mailgun_domain}")
        print("=" * 80)
        
        print("📝 Step 1: Creating email content...")
        
        # HTML body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        margin: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 40px 20px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.9;
                        font-size: 16px;
                    }}
                    .content {{
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .qr-container {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 15px;
                        margin: 30px 0;
                        display: inline-block;
                    }}
                    .qr-container img {{
                        max-width: 300px;
                        width: 100%;
                        height: auto;
                        border-radius: 10px;
                    }}
                    .info-box {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        text-align: left;
                    }}
                    .info-row {{
                        display: flex;
                        justify-content: space-between;
                        padding: 10px 0;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    .info-row:last-child {{
                        border-bottom: none;
                    }}
                    .info-label {{
                        font-weight: 600;
                        color: #667eea;
                    }}
                    .info-value {{
                        color: #555;
                    }}
                    .instructions {{
                        background: #e3f2fd;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 30px 0;
                        border-left: 4px solid #2196f3;
                    }}
                    .instructions h3 {{
                        margin: 0 0 15px 0;
                        color: #1976d2;
                        font-size: 18px;
                    }}
                    .instructions ol {{
                        margin: 0;
                        padding-left: 20px;
                        text-align: left;
                    }}
                    .instructions li {{
                        margin: 10px 0;
                        color: #555;
                    }}
                    .footer {{
                        background: #f8f9fa;
                        padding: 30px;
                        text-align: center;
                        color: #888;
                        font-size: 14px;
                    }}
                    .btn {{
                        display: inline-block;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: 600;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎁 New QR Code Received!</h1>
                        <p>From: {sender_name}</p>
                    </div>
                    
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin: 0 0 20px 0;">
                            <strong>{sender_name}</strong> has shared an encrypted QR code with you!
                        </p>
                        
                        <div class="qr-container">
                            <img src="cid:qrcode" alt="QR Code" />
                        </div>
                        
                        <div class="info-box">
                            <div class="info-row">
                                <span class="info-label">📦 Content Type:</span>
                                <span class="info-value">{content_type.upper()}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">🔒 Encryption:</span>
                                <span class="info-value">{encryption_level.upper()}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">👤 From:</span>
                                <span class="info-value">{sender_name}</span>
                            </div>
                        </div>
                        
                        <div class="instructions">
                            <h3>📱 How to Access Your Content:</h3>
                            <ol>
                                <li>Open the HideAnything.QR app</li>
                                <li>Go to the "Scan QR" section</li>
                                <li>Scan this QR code or upload this image</li>
                                <li>View your decrypted content securely!</li>
                            </ol>
                        </div>
                        
                        <p style="color: #888; font-size: 14px; margin-top: 30px;">
                            🔐 Your content is end-to-end encrypted and can only be accessed by you.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>HideAnything.QR - Secure Content Sharing</p>
                        <p style="margin: 10px 0 0 0; font-size: 12px;">
                            This QR code contains encrypted content. Keep it secure!
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        print("📎 Step 2: Preparing QR code attachment...")
        
        # Remove data URL prefix if present
        if qr_code_base64.startswith('data:image'):
            qr_code_base64 = qr_code_base64.split(',')[1]
        
        # Decode QR image data
        qr_image_data = base64.b64decode(qr_code_base64)
        
        print("💌 Step 3: Creating Mailgun email...")
        
        # Mailgun API endpoint
        mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
        
        # Prepare email data
        data = {
            "from": from_email,
            "to": receiver_email,
            "subject": f"🎁 {sender_name} shared a QR Code with you!",
            "html": html_body
        }
        
        # Prepare attachment
        files = {
            "attachment": ("qrcode.png", qr_image_data, "image/png")
        }
        
        print("🚀 Step 4: Sending via Mailgun API...")
        print(f"   API URL: {mailgun_url}")
        
        # Send email via Mailgun
        response = requests.post(
            mailgun_url,
            auth=("api", mailgun_api_key),
            data=data,
            files=files,
            timeout=30
        )
        
        print("📊 Step 5: Checking response...")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("=" * 80)
            print(f"🎉 SUCCESS: Email delivered to {receiver_email}")
            response_data = response.json()
            print(f"   Message ID: {response_data.get('id', 'N/A')}")
            print("=" * 80)
            return True
        else:
            print(f"❌ Mailgun returned status {response.status_code}: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Mailgun Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n📋 Troubleshooting:")
        print("   1. Verify MAILGUN_API_KEY is set correctly in Render")
        print("   2. Check API key is valid (from Mailgun dashboard)")
        print("   3. Verify MAILGUN_DOMAIN matches your sandbox domain")
        print("   4. Add recipient to 'Authorized Recipients' in Mailgun")
        return False


def send_simple_email(receiver_email, subject, body):
    """
    Send a simple text email via Mailgun
    """
    try:
        mailgun_api_key = os.environ.get('MAILGUN_API_KEY', '')
        mailgun_domain = os.environ.get('MAILGUN_DOMAIN', '')
        from_email = os.environ.get('MAILGUN_FROM_EMAIL', f'HideQR <noreply@{mailgun_domain}>')
        
        if not mailgun_api_key or not mailgun_domain:
            print("Mailgun not configured")
            return False
        
        mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
        
        response = requests.post(
            mailgun_url,
            auth=("api", mailgun_api_key),
            data={
                "from": from_email,
                "to": receiver_email,
                "subject": subject,
                "html": body
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Email sent to {receiver_email}")
            return True
        else:
            print(f"❌ Mailgun returned: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

import os
import base64
import resend

def send_qr_email(receiver_email, sender_name, qr_code_base64, content_type, encryption_level):
    """
    Send QR code via email using Resend (works on Render)
    
    Args:
        receiver_email: Email address of the receiver
        sender_name: Username of the sender
        qr_code_base64: Base64 encoded QR code image
        content_type: Type of content (text/file)
        encryption_level: Encryption level used
    """
    try:
        # Get Resend configuration from environment
        resend_api_key = os.environ.get('RESEND_API_KEY', '')
        from_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
        
        if not resend_api_key:
            print("=" * 60)
            print("❌ RESEND API KEY NOT CONFIGURED")
            print("=" * 60)
            print("RESEND_API_KEY is not set")
            print("\n📋 To fix this:")
            print("1. Sign up at https://resend.com (free 100 emails/day)")
            print("2. Create API Key: Dashboard → API Keys → Create")
            print("3. Add to Render Environment Variables:")
            print("   RESEND_API_KEY=your_api_key_here")
            print("   RESEND_FROM_EMAIL=onboarding@resend.dev")
            print("=" * 60)
            return False
        
        # Set Resend API key
        resend.api_key = resend_api_key
        
        print("=" * 80)
        print(f"📧 SENDING EMAIL VIA RESEND TO: {receiver_email}")
        print(f"📨 From: {from_email}")
        print(f"👤 Sender Name: {sender_name}")
        print(f"📦 Content Type: {content_type}")
        print(f"🔐 Encryption Level: {encryption_level}")
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
        
        print("💌 Step 3: Creating Resend email...")
        
        # Send via Resend
        params = {
            "from": from_email,
            "to": [receiver_email],
            "subject": f"🎁 {sender_name} shared a QR Code with you!",
            "html": html_body,
            "attachments": [
                {
                    "filename": "qrcode.png",
                    "content": list(qr_image_data)
                }
            ]
        }
        
        print("🚀 Step 4: Sending via Resend API...")
        
        # Send email
        email = resend.Emails.send(params)
        
        print("📊 Step 5: Checking response...")
        print(f"   Response: {email}")
        
        if email and 'id' in email:
            print("=" * 80)
            print(f"🎉 SUCCESS: Email delivered to {receiver_email}")
            print(f"   Email ID: {email['id']}")
            print("=" * 80)
            return True
        else:
            print(f"❌ Resend returned unexpected response: {email}")
            return False
        
    except Exception as e:
        print(f"❌ Resend Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n📋 Troubleshooting:")
        print("   1. Verify RESEND_API_KEY is set correctly in Render")
        print("   2. Check API key is valid (from https://resend.com/api-keys)")
        print("   3. Verify sender email domain (use onboarding@resend.dev for testing)")
        return False


def send_simple_email(receiver_email, subject, body):
    """
    Send a simple text email via Resend
    """
    try:
        resend_api_key = os.environ.get('RESEND_API_KEY', '')
        from_email = os.environ.get('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
        
        if not resend_api_key:
            print("Resend API key not configured")
            return False
        
        resend.api_key = resend_api_key
        
        params = {
            "from": from_email,
            "to": [receiver_email],
            "subject": subject,
            "html": body
        }
        
        email = resend.Emails.send(params)
        
        if email and 'id' in email:
            print(f"✅ Email sent to {receiver_email}")
            return True
        else:
            print(f"❌ Resend returned: {email}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

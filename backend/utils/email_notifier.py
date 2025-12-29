import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
from io import BytesIO
import socket

def send_qr_email(receiver_email, sender_name, qr_code_base64, content_type, encryption_level):
    """
    Send QR code via email
    
    Args:
        receiver_email: Email address of the receiver
        sender_name: Username of the sender
        qr_code_base64: Base64 encoded QR code image
        content_type: Type of content (text/file)
        encryption_level: Encryption level used
    """
    try:
        # Get email configuration from environment
        mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = int(os.environ.get('MAIL_PORT', 587))
        mail_username = os.environ.get('MAIL_USERNAME', '')
        mail_password = os.environ.get('MAIL_PASSWORD', '')
        mail_use_tls = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        
        if not mail_username or not mail_password:
            print("❌ Email credentials not configured in .env file")
            print("Please set MAIL_USERNAME and MAIL_PASSWORD")
            return False
        
        print(f"📧 Attempting to send email to: {receiver_email}")
        print(f"📮 Using SMTP: {mail_server}:{mail_port}")
        
        # Create message
        msg = MIMEMultipart('related')
        msg['Subject'] = f'🎁 {sender_name} shared a QR Code with you!'
        msg['From'] = mail_username
        msg['To'] = receiver_email
        
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
        
        # Attach HTML body
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        html_part = MIMEText(html_body, 'html')
        msg_alternative.attach(html_part)
        
        # Attach QR code image
        try:
            # Remove data URL prefix if present
            if qr_code_base64.startswith('data:image'):
                qr_code_base64 = qr_code_base64.split(',')[1]
            
            qr_image_data = base64.b64decode(qr_code_base64)
            qr_image = MIMEImage(qr_image_data)
            qr_image.add_header('Content-ID', '<qrcode>')
            qr_image.add_header('Content-Disposition', 'inline', filename='qrcode.png')
            msg.attach(qr_image)
        except Exception as img_error:
            print(f"Error attaching QR image: {img_error}")
        
        # Send email
        print(f"🔌 Connecting to {mail_server}:{mail_port}...")
        
        # Set socket timeout to avoid hanging
        socket.setdefaulttimeout(30)
        
        # Try connecting with timeout
        try:
            server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        except socket.timeout:
            print("❌ Connection timeout. Please check:")
            print("   1. Your internet connection")
            print("   2. Firewall settings (allow port 587)")
            print("   3. Antivirus blocking SMTP")
            return False
        except socket.gaierror:
            print(f"❌ Cannot resolve hostname: {mail_server}")
            return False
        
        if mail_use_tls:
            print("🔒 Starting TLS encryption...")
            server.starttls()
        
        print(f"🔑 Logging in as {mail_username}...")
        try:
            server.login(mail_username, mail_password)
        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed!")
            print("For Gmail:")
            print("   1. Enable 2-Factor Authentication")
            print("   2. Generate an App Password: https://myaccount.google.com/apppasswords")
            print("   3. Use the App Password (not your regular password)")
            server.quit()
            return False
        
        print(f"📤 Sending email to {receiver_email}...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {receiver_email}!")
        return True
        
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"❌ SMTP Authentication Error: {auth_error}")
        print("📋 Troubleshooting Steps:")
        print("   For Gmail:")
        print("   1. Enable 2-Factor Authentication in your Google Account")
        print("   2. Go to: https://myaccount.google.com/apppasswords")
        print("   3. Generate an 'App Password' for 'Mail'")
        print("   4. Update MAIL_PASSWORD in .env with the App Password")
        return False
    except socket.timeout:
        print(f"❌ Connection Timeout")
        print("📋 Check:")
        print("   1. Your internet connection")
        print("   2. Firewall/Antivirus blocking port 587")
        print("   3. VPN or proxy settings")
        return False
    except smtplib.SMTPException as smtp_error:
        print(f"❌ SMTP Error: {smtp_error}")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_simple_email(receiver_email, subject, body):
    """
    Send a simple text email
    """
    try:
        mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = int(os.environ.get('MAIL_PORT', 587))
        mail_username = os.environ.get('MAIL_USERNAME', '')
        mail_password = os.environ.get('MAIL_PASSWORD', '')
        mail_use_tls = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
        
        if not mail_username or not mail_password:
            print("Email credentials not configured")
            return False
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = mail_username
        msg['To'] = receiver_email
        
        server = smtplib.SMTP(mail_server, mail_port)
        if mail_use_tls:
            server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

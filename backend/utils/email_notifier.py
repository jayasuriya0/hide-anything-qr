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
        mail_server = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        mail_port = int(os.environ.get('SMTP_PORT', 587))
        mail_username = os.environ.get('SMTP_USER', '')
        mail_password = os.environ.get('SMTP_PASSWORD', '')
        mail_use_tls = os.environ.get('SMTP_TLS', 'true').lower() == 'true'
        
        if not mail_username or not mail_password:
            print("=" * 60)
            print("❌ EMAIL CREDENTIALS NOT CONFIGURED")
            print("=" * 60)
            print("SMTP_USER is not set" if not mail_username else f"SMTP_USER: {mail_username}")
            print("SMTP_PASSWORD is not set" if not mail_password else "SMTP_PASSWORD: [SET]")
            print("\n📋 To fix this:")
            print("1. For local development: Set in backend/.env file")
            print("2. For production (Render): Set in Environment Variables")
            print("\nRequired variables:")
            print("   SMTP_HOST=smtp.gmail.com")
            print("   SMTP_PORT=587")
            print("   SMTP_USER=your-email@gmail.com")
            print("   SMTP_PASSWORD=your-app-password")
            print("   SMTP_TLS=true")
            print("=" * 60)
            return False
        
        print("=" * 80)
        print(f"📧 SENDING EMAIL TO: {receiver_email}")
        print(f"📮 SMTP Server: {mail_server}:{mail_port}")
        print(f"👤 SMTP User: {mail_username}")
        print(f"🔐 Password Length: {len(mail_password)} characters")
        print(f"🔒 TLS Enabled: {mail_use_tls}")
        print(f"📨 From: {sender_name}")
        print(f"📦 Content Type: {content_type}")
        print(f"🔐 Encryption Level: {encryption_level}")
        print("=" * 80)
        
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
        print(f"🔌 Step 1: Connecting to {mail_server}:{mail_port}...")
        
        # Set socket timeout to avoid hanging
        socket.setdefaulttimeout(30)
        
        # Try connecting with timeout
        try:
            server = smtplib.SMTP(mail_server, mail_port, timeout=30)
            print(f"✅ Step 1: Connected successfully!")
        except socket.timeout:
            print("❌ Step 1 FAILED: Connection timeout!")
            print("   Possible causes:")
            print("   1. Render/hosting provider blocking outbound SMTP (port 587)")
            print("   2. Firewall settings blocking the connection")
            print("   3. SMTP server is down")
            print("\n💡 Solution: Check if Render allows outbound SMTP connections")
            return False
        except socket.gaierror as dns_error:
            print(f"❌ Step 1 FAILED: Cannot resolve hostname: {mail_server}")
            print(f"   DNS Error: {dns_error}")
            return False
        except ConnectionRefusedError:
            print(f"❌ Step 1 FAILED: Connection refused by {mail_server}:{mail_port}")
            print("   Server actively refused the connection")
            return False
        except Exception as conn_error:
            print(f"❌ Step 1 FAILED: Connection error: {conn_error}")
            import traceback
            traceback.print_exc()
            return False
        
        try:
            if mail_use_tls:
                print("🔒 Step 2: Starting TLS encryption...")
                server.starttls()
                print("✅ Step 2: TLS encryption started!")
            
            print(f"🔑 Step 3: Logging in as {mail_username}...")
            server.login(mail_username, mail_password)
            print("✅ Step 3: Login successful!")
        
        except smtplib.SMTPAuthenticationError as auth_err:
            print(f"❌ Step 3 FAILED: Authentication error!")
            print(f"   Error code: {auth_err.smtp_code}")
            print(f"   Error message: {auth_err.smtp_error}")
            print("\n📋 Troubleshooting:")
            print("   1. Verify SMTP_USER is correct email address")
            print("   2. For Gmail: Must use App Password (not regular password)")
            print("   3. Generate App Password: https://myaccount.google.com/apppasswords")
            print("   4. Enable 2-Factor Authentication first")
            server.quit()
            return False
        except smtplib.SMTPException as smtp_err:
            print(f"❌ SMTP Error during setup: {smtp_err}")
            try:
                server.quit()
            except:
                pass
            return False
        except Exception as setup_error:
            print(f"❌ Setup error: {setup_error}")
            import traceback
            traceback.print_exc()
            try:
                server.quit()
            except:
                pass
            return False
        
        # Send the email
        try:
            print(f"📤 Step 4: Sending email to {receiver_email}...")
            server.send_message(msg)
            print("✅ Step 4: Email sent successfully!")
            
            print("🔌 Step 5: Closing connection...")
            server.quit()
            print("✅ Step 5: Connection closed!")
            
            print("=" * 80)
            print(f"🎉 SUCCESS: Email delivered to {receiver_email}")
            print("=" * 80)
            return True
            
        except smtplib.SMTPException as send_err:
            print(f"❌ Step 4 FAILED: Error sending email!")
            print(f"   SMTP Error: {send_err}")
            try:
                server.quit()
            except:
                pass
            return False
        except Exception as send_error:
            print(f"❌ Step 4 FAILED: Unexpected error: {send_error}")
            import traceback
            traceback.print_exc()
            try:
                server.quit()
            except:
                pass
            return False
        
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
        mail_server = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        mail_port = int(os.environ.get('SMTP_PORT', 587))
        mail_username = os.environ.get('SMTP_USER', '')
        mail_password = os.environ.get('SMTP_PASSWORD', '')
        mail_use_tls = os.environ.get('SMTP_TLS', 'true').lower() == 'true'
        
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

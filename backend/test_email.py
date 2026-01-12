import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.email_notifier import send_simple_email, send_qr_email

print("Testing Email Configuration...")
print("=" * 50)

# Check environment variables
mail_server = os.environ.get('SMTP_HOST', 'Not set')
mail_port = os.environ.get('SMTP_PORT', 'Not set')
mail_username = os.environ.get('SMTP_USER', 'Not set')
mail_password = os.environ.get('SMTP_PASSWORD', 'Not set')
mail_use_tls = os.environ.get('SMTP_TLS', 'Not set')

print(f"SMTP_HOST: {mail_server}")
print(f"SMTP_PORT: {mail_port}")
print(f"SMTP_USER: {mail_username}")
print(f"SMTP_PASSWORD: {'*' * len(mail_password) if mail_password != 'Not set' else 'Not set'}")
print(f"SMTP_TLS: {mail_use_tls}")
print("=" * 50)

# Test sending a simple email
test_email = input("\nEnter email address to test (or press Enter to skip): ").strip()

if test_email:
    print(f"\nSending test email to {test_email}...")
    success = send_simple_email(
        receiver_email=test_email,
        subject="Test Email from HideAnything.QR",
        body="This is a test email. If you received this, the email configuration is working!"
    )
    
    if success:
        print("\n✅ Email sent successfully! Check your inbox.")
    else:
        print("\n❌ Failed to send email. Check the error messages above.")
else:
    print("\nSkipping email test.")

print("\nEmail configuration check complete!")

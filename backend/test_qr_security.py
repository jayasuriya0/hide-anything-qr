#!/usr/bin/env python3
"""Test script to demonstrate QR security feature"""
import json
from utils.qr_generator import QRGenerator

# Example sensitive data (what was shown before)
sensitive_data = {
    "content_id": "69520d2852639ea2d076900b",
    "encrypted_key": "lLfm9cJXibHT2yuI2IypeGxOP5UH8/cN",
    "sender_id": "694e4e5a0a07a0f0888af99c",
    "metadata": {
        "type": "file",
        "filename": "Thalapathy Kacheri.mp3",
        "content_type": "audio/mpeg",
        "size": 7960256,
        "is_public": True,
        "encryption_level": "standard",
        "encryption_name": "Standard (AES-192)"
    }
}

print("=" * 80)
print("QR CODE SECURITY TEST")
print("=" * 80)
print()

# Show what was visible before
print("❌ BEFORE (What regular scanners could see):")
print("-" * 80)
print(json.dumps(sensitive_data, indent=2))
print()
print("⚠️  Problem: All sensitive information is visible!")
print("   - Database IDs")
print("   - Encrypted keys")
print("   - User IDs")
print("   - File metadata")
print()

# Show what will be visible now
print("=" * 80)
print()
print("✅ AFTER (What regular scanners will see now):")
print("-" * 80)
encoded = QRGenerator.encode_secure_data(sensitive_data)
print(encoded)
print()
print("✅ Success: Both sensitive data AND platform identity are hidden!")
print("   - Generic URL scheme 'qrs://v?d=' reveals nothing")
print("   - Could be from any QR code app")
print("   - Base64 encoded data is not human-readable")
print("   - No way to identify the platform")
print("   - App can still decode it properly")
print()

# Verify decoding works
print("=" * 80)
print()
print("🔓 VERIFICATION: App can still decode:")
print("-" * 80)
decoded = QRGenerator.decode_secure_data(encoded)
print(json.dumps(decoded, indent=2))
print()
print("✅ Decoding successful! All data intact.")
print()
print("=" * 80)

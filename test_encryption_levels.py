#!/usr/bin/env python
"""Test encryption levels implementation"""

import sys
sys.path.insert(0, 'backend')

from utils.encryption import EncryptionManager, get_encryption_levels

def test_encryption_levels():
    em = EncryptionManager()
    levels = get_encryption_levels()
    
    test_data = b'Hello World! This is a test of the encryption system.'
    
    print("=" * 60)
    print("TESTING ENCRYPTION LEVELS")
    print("=" * 60)
    
    for level_name, config in levels.items():
        print(f"\n📊 Testing: {config['name']}")
        print(f"   AES Key Size: {config['aes_key_size']} bytes ({config['aes_key_size'] * 8} bits)")
        print(f"   RSA Key Size: {config['rsa_key_size']} bits")
        
        try:
            # Generate AES key
            aes_key = em.generate_aes_key(config['aes_key_size'])
            print(f"   ✅ AES key generated: {len(aes_key)} bytes")
            
            # Encrypt data
            encrypted = em.encrypt_data(test_data, aes_key)
            print(f"   ✅ Data encrypted: {len(encrypted)} chars")
            
            # Decrypt data
            decrypted = em.decrypt_data(encrypted, aes_key, return_bytes=True)
            print(f"   ✅ Data decrypted: {len(decrypted)} bytes")
            
            # Verify
            if decrypted == test_data:
                print(f"   ✅ VERIFICATION PASSED - Data matches original!")
            else:
                print(f"   ❌ VERIFICATION FAILED - Data mismatch!")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING RSA KEY GENERATION")
    print("=" * 60)
    
    for level_name, config in levels.items():
        print(f"\n📊 Testing RSA-{config['rsa_key_size']} for {config['name']}")
        
        try:
            # Generate RSA keypair
            private_pem, public_pem = em.generate_keypair(config['rsa_key_size'])
            print(f"   ✅ RSA keypair generated")
            print(f"   Private key length: {len(private_pem)} chars")
            print(f"   Public key length: {len(public_pem)} chars")
            
            # Test encrypting AES key with RSA
            aes_key = em.generate_aes_key(config['aes_key_size'])
            encrypted_aes = em.encrypt_aes_key(aes_key, public_pem)
            print(f"   ✅ AES key encrypted with RSA: {len(encrypted_aes)} chars")
            
            # Decrypt AES key
            decrypted_aes = em.decrypt_aes_key(encrypted_aes, private_pem)
            
            if decrypted_aes == aes_key:
                print(f"   ✅ RSA ENCRYPTION PASSED - AES key recovered!")
            else:
                print(f"   ❌ RSA ENCRYPTION FAILED - Key mismatch!")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    test_encryption_levels()

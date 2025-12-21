import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import hashlib

# Encryption levels configuration
ENCRYPTION_LEVELS = {
    'basic': {
        'name': 'Basic (AES-128)',
        'aes_key_size': 16,  # 128-bit
        'rsa_key_size': 2048,
        'description': 'Fast encryption suitable for non-sensitive data'
    },
    'standard': {
        'name': 'Standard (AES-192)',
        'aes_key_size': 24,  # 192-bit
        'rsa_key_size': 2048,
        'description': 'Balanced security and performance'
    },
    'high': {
        'name': 'High (AES-256)',
        'aes_key_size': 32,  # 256-bit
        'rsa_key_size': 3072,
        'description': 'Strong encryption for sensitive data'
    },
    'maximum': {
        'name': 'Maximum (AES-256 + RSA-4096)',
        'aes_key_size': 32,  # 256-bit
        'rsa_key_size': 4096,
        'description': 'Military-grade encryption for highly confidential data'
    }
}

class EncryptionManager:
    @staticmethod
    def generate_keypair(key_size=2048):
        """Generate RSA key pair with specified key size"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
    
    @staticmethod
    def encrypt_private_key(private_key_pem, password):
        """Encrypt private key with user's password"""
        salt = os.urandom(16)
        kdf = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        key = kdf[:32]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        
        encrypted = encryptor.update(private_key_pem.encode()) + encryptor.finalize()
        
        return base64.b64encode(salt + encryptor.tag + encrypted).decode()
    
    @staticmethod
    def decrypt_private_key(encrypted_key, password):
        """Decrypt private key with user's password"""
        data = base64.b64decode(encrypted_key)
        salt = data[:16]
        tag = data[16:32]
        encrypted = data[32:]
        
        kdf = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        key = kdf[:32]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(salt, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        return decrypted.decode()
    
    @staticmethod
    def encrypt_aes_key(aes_key, public_key_pem):
        """Encrypt AES key with RSA public key"""
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        encrypted = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_aes_key(encrypted_aes_key, private_key_pem):
        """Decrypt AES key with RSA private key"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
            backend=default_backend()
        )
        
        encrypted = base64.b64decode(encrypted_aes_key)
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted
    
    @staticmethod
    def encrypt_data(data, aes_key):
        """Encrypt data with AES-GCM"""
        if isinstance(data, str):
            data = data.encode()
        
        salt = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(salt), backend=default_backend())
        encryptor = cipher.encryptor()
        
        encrypted = encryptor.update(data) + encryptor.finalize()
        return base64.b64encode(salt + encryptor.tag + encrypted).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data, aes_key, return_bytes=False):
        """Decrypt data with AES-GCM
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            aes_key: AES key for decryption
            return_bytes: If True, return raw bytes. If False, decode to string.
        """
        data = base64.b64decode(encrypted_data)
        salt = data[:16]
        tag = data[16:32]
        encrypted = data[32:]
        
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(salt, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(encrypted) + decryptor.finalize()
        
        if return_bytes:
            return decrypted
        else:
            try:
                return decrypted.decode()
            except UnicodeDecodeError:
                # If can't decode as text, return bytes
                return decrypted
    
    @staticmethod
    def generate_aes_key(key_size=32):
        """Generate random AES key with specified size (16, 24, or 32 bytes)"""
        if key_size not in [16, 24, 32]:
            raise ValueError("AES key size must be 16, 24, or 32 bytes")
        return os.urandom(key_size)
    
    @staticmethod
    def get_encryption_level_config(level='standard'):
        """Get encryption configuration for specified level"""
        return ENCRYPTION_LEVELS.get(level, ENCRYPTION_LEVELS['standard'])

# Helper functions
def generate_keypair(key_size=2048):
    return EncryptionManager.generate_keypair(key_size)

def encrypt_private_key(private_key, password):
    return EncryptionManager.encrypt_private_key(private_key, password)

def decrypt_private_key(encrypted_key, password):
    return EncryptionManager.decrypt_private_key(encrypted_key, password)

def generate_aes_key(key_size=32):
    return EncryptionManager.generate_aes_key(key_size)

def get_encryption_levels():
    """Get available encryption levels"""
    return ENCRYPTION_LEVELS
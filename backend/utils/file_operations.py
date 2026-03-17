"""
File operations utilities with retry logic, error handling, and verification
"""
import hashlib
import time
from typing import Tuple, Dict, Optional, Any
from enum import Enum


class FileErrorCode(Enum):
    """File operation error codes"""
    CHUNK_MISSING = 'CHUNK_MISSING'
    CORRUPTION_DETECTED = 'CORRUPTION_DETECTED'
    EMPTY_FILE = 'EMPTY_FILE'
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'
    READ_FAILED = 'READ_FAILED'
    WRITE_FAILED = 'WRITE_FAILED'
    UPLOAD_TIMEOUT = 'UPLOAD_TIMEOUT'
    INVALID_HASH = 'INVALID_HASH'
    RETRY_EXHAUSTED = 'RETRY_EXHAUSTED'


class FileOperationRetry:
    """Retry logic with exponential backoff for file operations"""
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 0.5, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.retry_count = 0
        self.last_error = None
    
    def execute(self, operation, *args, **kwargs) -> Tuple[Optional[Any], Optional[Dict]]:
        """
        Execute operation with retry logic
        
        Returns:
            (success_result, error_dict) - one will be None
        """
        delay = self.initial_delay
        
        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                if attempt > 0:
                    print(f"[RETRY] Operation succeeded on attempt {attempt + 1}/{self.max_retries}")
                return result, None
            
            except Exception as e:
                self.retry_count = attempt + 1
                self.last_error = str(e)
                
                if attempt < self.max_retries - 1:
                    print(f"[RETRY] Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    print(f"[RETRY] All {self.max_retries} attempts failed")
                    return None, {
                        'status': 'error',
                        'code': FileErrorCode.RETRY_EXHAUSTED.value,
                        'message': f'Operation failed after {self.max_retries} retries',
                        'last_error': self.last_error,
                        'attempts': self.retry_count
                    }
        
        return None, {
            'status': 'error',
            'code': FileErrorCode.RETRY_EXHAUSTED.value,
            'message': 'Unexpected retry logic failure'
        }


def calculate_file_hash(file_data: bytes, algorithm: str = 'sha256') -> str:
    """
    Calculate file hash
    
    Args:
        file_data: Binary file data
        algorithm: Hash algorithm (default: sha256)
    
    Returns:
        Hex digest of file hash
    """
    if algorithm == 'sha256':
        return hashlib.sha256(file_data).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(file_data).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(file_data).hexdigest()
    else:
        raise ValueError(f'Unsupported algorithm: {algorithm}')


def verify_file_hash(file_data: bytes, expected_hash: str, algorithm: str = 'sha256') -> Tuple[bool, str]:
    """
    Verify file hash matches expected value
    
    Returns:
        (is_valid, message)
    """
    actual_hash = calculate_file_hash(file_data, algorithm)
    
    if actual_hash == expected_hash:
        return True, 'File hash verified'
    else:
        return False, f'Hash mismatch: expected {expected_hash}, got {actual_hash}'


def create_error_response(code: FileErrorCode, message: str, details: Optional[str] = None) -> Dict:
    """Create standardized error response"""
    response = {
        'status': 'error',
        'code': code.value,
        'message': message
    }
    
    if details:
        response['details'] = details
    
    return response


def create_success_response(data: Any = None, message: str = 'Success') -> Dict:
    """Create standardized success response"""
    return {
        'status': 'success',
        'message': message,
        'data': data
    }


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert bytes to MB"""
    return file_size_bytes / (1024 * 1024)


def format_file_size(file_size_bytes: int) -> str:
    """Format file size as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if file_size_bytes < 1024:
            return f'{file_size_bytes:.2f}{unit}'
        file_size_bytes /= 1024
    return f'{file_size_bytes:.2f}PB'

# Error Handling & File Operations Guide

## Overview

This document explains the robust error handling, GridFS chunking verification, and recovery mechanisms implemented in the Hide Anything with QR project.

---

## ✅ Implemented Features

### 1. **Error on Write - Rollback on Partial Upload**

**Problem:** If upload fails mid-upload, orphaned chunks left in GridFS.

**Solution:** 
- Transaction-like behavior with hash verification
- Automatic cleanup on upload failure
- Upload session tracking

**Code Location:** `backend/models/content.py` - `share_content()` method

```python
# If GridFS write fails:
try:
    file_id = self.fs.put(encrypted_data_bytes, ...)
except Exception as e:
    # Automatic cleanup and error return
    return None, {
        'status': 'error',
        'code': 'WRITE_FAILED',
        'message': f'Failed to store file: {str(e)}'
    }
```

**After Document Insert Fails:**
```python
if metadata.get('type') == 'file' and 'file_id' in content:
    try:
        self.fs.delete(content['file_id'])  # Cleanup orphaned file
    except:
        pass
```

---

### 2. **Error on Read - Specific Error Types**

**Problem:** Generic "File not found" errors don't explain the actual issue (chunk missing, corruption, timeout, etc.)

**Solution:** Specific error codes for different failures

**Code Location:** `backend/models/content.py` - `read_file_with_verification()` method

**Error Codes Returned:**

```python
class FileErrorCode(Enum):
    CHUNK_MISSING = 'CHUNK_MISSING'              # EOF mid-read
    CORRUPTION_DETECTED = 'CORRUPTION_DETECTED'  # Hash mismatch
    EMPTY_FILE = 'EMPTY_FILE'                    # 0 bytes
    FILE_NOT_FOUND = 'FILE_NOT_FOUND'            # Not in GridFS
    READ_FAILED = 'READ_FAILED'                  # Read error
    WRITE_FAILED = 'WRITE_FAILED'                # Write error
    UPLOAD_TIMEOUT = 'UPLOAD_TIMEOUT'            # Timeout
    INVALID_HASH = 'INVALID_HASH'                # Hash verification failed
```

**Example Error Response:**

```json
{
    "status": "error",
    "code": "CHUNK_MISSING",
    "message": "File chunks incomplete - missing data mid-stream. Upload may have been interrupted."
}
```

---

### 3. **Corruption Detection - Verify Hash**

**Problem:** Can't detect if file got corrupted during storage.

**Solution:** SHA-256 hash verification before and after storage

**Code Location:** `backend/models/content.py` - `_verify_file_integrity()` method

**Flow:**

```
1. Calculate SHA-256 hash of original file
   ↓
2. Encrypt and store in GridFS
   ↓
3. Retrieve from GridFS
   ↓
4. Calculate SHA-256 hash again
   ↓
5. Compare - if different, file corrupted
   ↓
6. If corrupted: delete file, return error
```

**Implementation:**

```python
def _verify_file_integrity(self, file_id, expected_hash):
    grid_file = self.fs.get(ObjectId(file_id))
    file_data = grid_file.read()
    actual_hash = hashlib.sha256(file_data).hexdigest()
    
    if actual_hash != expected_hash:
        return {'valid': False, 'message': f'Hash mismatch'}
    return {'valid': True, 'message': 'File integrity verified'}
```

**Usage in share_content:**

```python
file_id = self.fs.put(encrypted_data_bytes, ...)

if file_hash:
    verification = self._verify_file_integrity(file_id, file_hash)
    if not verification['valid']:
        self.fs.delete(file_id)  # Cleanup
        return None, {'status': 'error', 'code': 'CORRUPTION_DETECTED'}
```

---

### 4. **Orphaned Cleanup - Auto-Cleanup**

**Problem:** Failed uploads leave chunks orphaned in GridFS.

**Solution:** Automatic cleanup of orphaned chunks

**Code Location:** `backend/models/content.py` - `cleanup_orphaned_chunks()` method

**How It Works:**

```python
1. Get all valid file IDs from fs.files
2. Find chunks with no matching file ID
3. Delete orphaned chunks
4. Delete expired upload sessions (2hr TTL)
```

**Endpoint:** 
```
POST /api/content/maintenance/cleanup-orphaned
```

**Manual Cleanup Example:**

```python
result = content_model.cleanup_orphaned_chunks()
# Result:
# {
#     'orphaned_chunks_removed': 150,
#     'expired_sessions_removed': 5
# }
```

**Automatic TTL Cleanup:**

Upload sessions automatically expire after 2 hours:

```python
content['expires_at'] = datetime.now(timezone.utc) + timedelta(hours=2)
# MongoDB TTL index automatically deletes after expiration
```

---

### 5. **User Feedback - Specific Error Messages**

**Problem:** Generic errors don't help users understand what went wrong.

**Solution:** Specific, actionable error messages for each scenario

**Examples:**

```json
// Chunk missing (incomplete upload)
{
    "status": "error",
    "code": "CHUNK_MISSING",
    "message": "File chunks incomplete - missing data mid-stream. Upload may have been interrupted.",
    "action": "Please check your internet connection and retry"
}

// File corrupted
{
    "status": "error",
    "code": "CORRUPTION_DETECTED",
    "message": "File corruption detected: Hash mismatch",
    "action": "Upload failed during verification. Please try again."
}

// Empty file
{
    "status": "error", 
    "code": "EMPTY_FILE",
    "message": "File is empty or corrupted",
    "action": "The file appears to be empty. Check your file and try again."
}
```

---

### 6. **Retry Logic - Retry Chunks**

**Problem:** One network glitch fails entire upload.

**Solution:** Automatic retry with exponential backoff

**Code Location:** `backend/utils/file_operations.py` - `FileOperationRetry` class

**Retry Strategy:**

```
Attempt 1: Try immediately
  ↓ (fail)
Wait 0.5s
Attempt 2: Try again
  ↓ (fail)
Wait 1s (2x backoff)
Attempt 3: Try again
  ↓ (fail)
Wait 2s (2x backoff)
FAIL - Return error after 3 attempts
```

**Usage Example:**

```python
from backend.utils.file_operations import FileOperationRetry

retry = FileOperationRetry(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
result, error = retry.execute(upload_operation, file_data, metadata)

if error:
    print(f"Upload failed: {error}")
else:
    print(f"Upload succeeded: {result}")
```

**Output:**

```
[RETRY] Attempt 1 failed: Connection timeout. Retrying in 0.5s...
[RETRY] Attempt 2 failed: Socket error. Retrying in 1.0s...
[RETRY] Operation succeeded on attempt 3/3
```

---

## 📊 Upload Session Tracking

Track upload progress from start to finish.

**Collection:** `upload_sessions`

**Document Structure:**

```json
{
    "_id": ObjectId("..."),
    "user_id": ObjectId("..."),
    "filename": "video.mp4",
    "total_size": 524288000,
    "expected_hash": "abc123def456...",
    "uploaded_size": 262144000,
    "status": "in_progress",
    "encryption_level": "high",
    "retry_count": 2,
    "last_error": "Connection timeout - retry",
    "created_at": ISODate("2025-01-15T10:30:00Z"),
    "expires_at": ISODate("2025-01-15T12:30:00Z")
}
```

**Status Values:**
- `in_progress` - Upload in progress
- `completed` - Upload complete but not verified
- `verified` - Upload complete and hash verified
- `failed` - Upload failed

**API Endpoints:**

```
# Check upload progress
GET /api/content/maintenance/upload-sessions-status

Response:
{
    "status": "success",
    "sessions_by_status": {
        "in_progress": 3,
        "completed": 12,
        "verified": 145,
        "failed": 2
    },
    "total_pending_size_mb": 1250.5
}
```

---

## 🔧 File Operations Utilities

**Module:** `backend/utils/file_operations.py`

**Functions:**

```python
from backend.utils.file_operations import (
    calculate_file_hash,
    verify_file_hash,
    create_error_response,
    create_success_response,
    format_file_size,
    FileOperationRetry,
    FileErrorCode
)

# Calculate hash
hash_value = calculate_file_hash(file_data, algorithm='sha256')

# Verify hash
is_valid, message = verify_file_hash(file_data, expected_hash)

# Create responses
error = create_error_response(FileErrorCode.CHUNK_MISSING, "Chunks incomplete")
success = create_success_response(data={'file_id': '123'}, message="Upload verified")

# Format size
formatted = format_file_size(524288000)  # "500.00MB"
```

---

## 📈 Error Flow Diagram

```
User uploads file
    ↓
Calculate SHA-256 hash
    ↓
Create upload session
    ↓
Encrypt file
    ↓
Store in GridFS (with retry logic)
    ├─ Success → Verify hash
    │           ├─ Hash match → Mark verified ✓
    │           └─ Hash mismatch → Delete file, return CORRUPTION_DETECTED ✗
    │
    └─ Failure → Delete partial file, return WRITE_FAILED ✗
         (Rollback: orphaned chunks auto-cleanup after 2hrs)
```

---

## 🧹 Cleanup & Maintenance

**Automatic:**
- TTL index on `upload_sessions` - expires after 2 hours
- TTL index on `fs.files` - respects MongoDB TTL settings

**Manual:**
```bash
# Cleanup orphaned chunks
curl -X POST http://localhost:5000/api/content/maintenance/cleanup-orphaned

# Check session status
curl http://localhost:5000/api/content/maintenance/upload-sessions-status
```

**Cron Job Example (every hour):**
```bash
0 * * * * curl -X POST http://localhost:5000/api/content/maintenance/cleanup-orphaned
```

---

## 💾 Database Collections

### `upload_sessions`
- Tracks upload progress and status
- Auto-cleanup via TTL (2 hours)
- Indexes: `expires_at`, `user_id`, `status`

### `fs.files`
- GridFS file metadata
- Contains file hashes and sizes

### `fs.chunks`
- GridFS actual chunks (256KB each)
- Auto-cleaned if file deleted

---

## 🚀 Testing Error Scenarios

**1. Test CHUNK_MISSING:**
```python
# Simulate by querying fs.chunks and deleting mid-chunk
db.fs.chunks.deleteOne({'files_id': file_id, 'n': {'$gte': 100}})
# Then try to read file
```

**2. Test CORRUPTION_DETECTED:**
```python
# Modify chunk data
db.fs.chunks.updateOne(
    {'files_id': file_id, 'n': 0},
    {'$set': {'data': BinData(...)}}
)
# Try to upload same file
```

**3. Test WRITE_FAILED:**
```python
# Disconnect database during upload
# Network error should be caught and retried
```

---

## 📚 API Response Examples

**Successful Upload:**
```json
{
    "status": 201,
    "content_id": "507f1f77bcf86cd799439011",
    "upload_session_id": "507f1f77bcf86cd799439012",
    "message": "File shared and verified successfully",
    "encryption_level": "high",
    "qr_code": "data:image/png;base64,..."
}
```

**Failed Upload:**
```json
{
    "status": 400,
    "error": "File upload failed",
    "code": "WRITE_FAILED",
    "message": "Failed to store file: Connection timeout",
    "upload_session_id": "507f1f77bcf86cd799439012"
}
```

**Failed Download (Chunk Missing):**
```json
{
    "status": 400,
    "code": "CHUNK_MISSING",
    "message": "File chunks incomplete - missing data mid-stream",
    "action": "The file upload may have been interrupted. Contact the sender for a new share."
}
```

---

## ⚠️ Important Notes

1. **Hash Verification:** Always verify after upload - don't skip this step
2. **Cleanup:** Run cleanup daily during off-peak hours to remove orphaned data
3. **Monitoring:** Monitor `upload_sessions` collection size - indicates failed uploads
4. **Storage:** GridFS chunk size is 256KB (MongoDB default) - don't change
5. **TTL:** Upload sessions expire after 2 hours - files must be downloaded within this window

---

## 🔍 Debugging

**Check orphaned chunks:**
```javascript
db.fs.chunks.find({
    files_id: {$nin: db.fs.files.distinct('_id')}
}).count()
```

**Check failed sessions:**
```javascript
db.upload_sessions.find({status: 'failed'})
```

**Check pending uploads:**
```javascript
db.upload_sessions.find({status: 'in_progress'}).forEach(doc => {
    console.log(`User: ${doc.user_id}, File: ${doc.filename}, Progress: ${doc.uploaded_size}/${doc.total_size}`)
})
```

---

**Last Updated:** March 17, 2026

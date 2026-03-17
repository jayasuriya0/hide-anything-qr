## ✅ Error Handling Testing Checklist

Use this checklist to verify all error handling features are working correctly.

---

## 1️⃣ Error on Write - Rollback Test

### Scenario: Simulate write failure and verify cleanup

**Setup:**
```python
# Test with database connection issue
# Or manually interrupt during upload
```

**Expected Result:**
- ✅ Partial file deleted from GridFS
- ✅ Upload session marked as 'failed'
- ✅ Error returned with `WRITE_FAILED` code
- ✅ User gets message about retry

**Verification:**
```bash
# Check that failed file is NOT in GridFS
db.fs.files.find({}, {_id: 1})
# Should not contain the failed file ID

# Check upload session
db.upload_sessions.findOne({status: 'failed'})
# Should show error message
```

---

## 2️⃣ Error on Read - Specific Error Types Test

### Test 2a: CHUNK_MISSING

**Setup:**
```javascript
// Find a file and delete one chunk
db.fs.files.findOne({}, {_id: 1})  // Get file_id
db.fs.chunks.deleteOne({
    files_id: file_id, 
    n: 100  // Delete middle chunk
})
```

**Expected:**
- ✅ Error code: `CHUNK_MISSING`
- ✅ Message: "File chunks incomplete - missing data mid-stream"
- ✅ User understands upload was interrupted

**Test:**
```bash
curl http://localhost:5000/api/content/decode
# Shows CHUNK_MISSING error
```

### Test 2b: EMPTY_FILE

**Expected:**
- ✅ Error code: `EMPTY_FILE`
- ✅ Message: "File is empty or corrupted"

### Test 2c: FILE_NOT_FOUND

**Expected:**
- ✅ Error code: `FILE_NOT_FOUND`
- ✅ Message: "File does not exist in database"

---

## 3️⃣ Corruption Detection - Hash Verification Test

### Scenario: Verify file hash before and after storage

**Setup:**
```python
file_hash_before = calculate_file_hash(file_data)

# Upload file (hash stored)

# Retrieve and verify
```

**Expected Result:**
- ✅ Hash calculated before upload ✓
- ✅ Hash verified after upload ✓
- ✅ Hashes match → file marked as verified
- ✅ No corruption detected

**Test Corruption Detection:**
```javascript
// Modify chunk data
db.fs.chunks.updateOne(
    {files_id: file_id, n: 0},
    {$set': {data: BinData(0, "corrupted_data")}}
)

// Try to download → Should detect corruption
```

**Expected:**
- ✅ Error code: `CORRUPTION_DETECTED`
- ✅ Original file deleted
- ✅ Message: "Hash mismatch: expected X got Y"

---

## 4️⃣ Orphaned Cleanup - Auto-Cleanup Test

### Scenario: Verify orphaned chunks are cleaned

**Setup:**
```javascript
// Let failed upload session expire (2 hours)
// Or manually call cleanup endpoint
```

**Expected Result:**
- ✅ Orphaned chunks deleted
- ✅ Cleanup result shows count removed
- ✅ Expired sessions deleted

**Manual Test:**
```bash
# Check before cleanup
db.fs.chunks.count()  # Note count

# Run cleanup
curl -X POST http://localhost:5000/api/content/maintenance/cleanup-orphaned

# Check after cleanup
db.fs.chunks.count()  # Should be less
```

**Expected:**
```json
{
    "status": "success",
    "result": {
        "orphaned_chunks_removed": 150,
        "expired_sessions_removed": 5
    }
}
```

---

## 5️⃣ User Feedback - Specific Error Messages Test

### Test each error message is clear

**CHUNK_MISSING:**
```json
{
    "code": "CHUNK_MISSING",
    "message": "File chunks incomplete - missing data mid-stream. Upload may have been interrupted."
}
```
- ✅ Clear what happened
- ✅ Implies user should retry

**CORRUPTION_DETECTED:**
```json
{
    "code": "CORRUPTION_DETECTED",
    "message": "File corruption detected: Hash mismatch"
}
```
- ✅ Clear that file is corrupted
- ✅ Specific about hash

**EMPTY_FILE:**
```json
{
    "code": "EMPTY_FILE",
    "message": "File is empty or corrupted"
}
```
- ✅ Clear about issue

---

## 6️⃣ Retry Logic - Retry Test

### Scenario: Network failure should retry automatically

**Setup:**
```bash
# Simulate network issue
# Kill connection mid-upload
# Internet turned off
```

**Expected Behavior:**
```
[RETRY] Attempt 1 failed: Connection error. Retrying in 0.5s...
[RETRY] Attempt 2 failed: Connection error. Retrying in 1.0s...
[RETRY] Attempt 3 failed: Connection error. Retrying in 2.0s...
[RETRY] Operation succeeded on attempt 3/3 (success)
```

**Or all fail:**
```
[RETRY] All 3 attempts failed
Error: RETRY_EXHAUSTED
```

**Test:**
```bash
# Slow network or intentional interruption
# Should see automatic retries
# No manual user action needed
```

---

## 📊 Full Integration Test

### Complete workflow with all features:

**Step 1: Upload file**
```bash
POST /api/content/share/file
- File: 50MB video
- Encryption: high
- Expected: Hash calculated, session created, verified
```

**Expected Response:**
```json
{
    "status": 201,
    "content_id": "...",
    "upload_session_id": "...",
    "message": "File shared and verified successfully"
}
```

✅ Check: `db.upload_sessions.findOne({upload_session_id})`
- Status should be "verified"
- File hash should be stored

**Step 2: Download file**
```bash
GET /api/content/download/{content_id}
```

**Expected:**
- ✅ File downloaded successfully
- ✅ Or specific error if chunks missing

**Step 3: Monitor**
```bash
GET /api/content/maintenance/upload-sessions-status
```

**Expected:**
```json
{
    "status": "success",
    "sessions_by_status": {
        "in_progress": 0,
        "verified": 1,
        "failed": 0
    }
}
```

---

## 🧪 Stress Test

### Test with multiple files simultaneously

**Setup:**
```bash
# Upload 10 files at once
# Mix of sizes: 1MB, 10MB, 50MB, 100MB
# Different encryption levels
```

**Expected:**
- ✅ All tracked in upload_sessions
- ✅ Progress visible
- ✅ No conflicts
- ✅ All verified correctly

---

## 🔧 Manual Verification Queries

### Check current state:

```javascript
// 1. Upload sessions
db.upload_sessions.find({}, {
    filename: 1, 
    status: 1, 
    created_at: 1
}).sort({created_at: -1}).limit(5)

// 2. GridFS stats
db.fs.files.stats()
db.fs.chunks.stats()

// 3. Orphaned chunks
db.fs.chunks.find({
    files_id: {$nin: db.fs.files.distinct('_id')}
}).count()

// 4. Failed uploads
db.upload_sessions.find({status: 'failed'}, {
    filename: 1,
    last_error: 1
})

// 5. Recent errors
db.upload_sessions.find({
    created_at: {$gte: new Date(Date.now() - 24*60*60*1000)}
}).count()
```

---

## 📋 Checklist: Mark Complete

### Basic Features
- [ ] Hash verification working
- [ ] Error codes specific and correct
- [ ] Upload sessions tracked
- [ ] Cleanup removes orphaned chunks
- [ ] Error messages clear and actionable
- [ ] Retries working automatically

### Advanced Features
- [ ] Rollback on write failure
- [ ] TTL deletion after 2 hours
- [ ] Maintenance endpoints accessible
- [ ] Monitoring dashboard shows data
- [ ] Database indexes optimized

### Production Ready
- [ ] Error handling tested end-to-end
- [ ] Cleanup cron job configured
- [ ] Monitoring alerts set up
- [ ] Documentation complete
- [ ] Team trained on new features
- [ ] Staging tests passed
- [ ] Production deployment ready

---

## ⚠️ Common Issues & Solutions

### Issue 1: Hash mismatch even though file is good

**Cause:** Different encoding or compression

**Fix:** Ensure hash calculated on raw file bytes before encryption

### Issue 2: Cleanup not removing orphaned chunks

**Check:**
```javascript
// Verify TTL index exists
db.upload_sessions.getIndexes()
// Should see: {expires_at: 1} with expireAfterSeconds: 0

// Manually trigger cleanup
curl -X POST .../cleanup-orphaned
```

### Issue 3: Upload sessions never expire

**Check:**
```javascript
// Verify TTL index on fs.files
db['fs.files'].getIndexes()

// Force cleanup
db.upload_sessions.deleteMany({
    expires_at: {$lt: new Date()}
})
```

### Issue 4: Error codes not specific

**Check:**
```python
# Verify FileErrorCode enum is imported
from backend.models.content import FileErrorCode
# Should have 8 values
```

---

## 🚀 Performance Benchmarks

### Expected Performance

| Operation | Time | Status |
|-----------|------|--------|
| Upload 100MB file | ~5-10s | ✅ |
| Hash verification | ~0.1s | ✅ |
| Cleanup orphaned (100 chunks) | ~0.5s | ✅ |
| Retry after failure | Auto, no latency | ✅ |
| Read error code | <1ms | ✅ |

---

## 📞 Support

If testing fails, check:

1. **Imports:** Verify all new utilities imported in routes/content.py
2. **MongoDB indexes:** All indexes created on upload_sessions
3. **Error codes:** FileErrorCode enum has all 8 types
4. **TTL:** MongoDB TTL index configured correctly
5. **Endpoints:** Maintenance endpoints registered

---

**Test Date:** ___________
**Tester Name:** ___________
**All Tests Passed:** ✅ Yes ❌ No

**Notes:**
_____________________________________

---

**Last Updated:** March 17, 2026

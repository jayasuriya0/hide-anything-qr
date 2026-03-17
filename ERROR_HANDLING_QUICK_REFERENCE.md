## Quick Reference: Error Handling Features

### 🔧 One-Minute Setup

The features are **automatically activated**. No configuration needed!

---

### 📊 Monitor What's Happening

```bash
# Check upload progress
curl http://localhost:5000/api/content/maintenance/upload-sessions-status

# Clean up orphaned files (run daily)
curl -X POST http://localhost:5000/api/content/maintenance/cleanup-orphaned
```

---

### 🛠️ Common Tasks

#### **Get Error Details**
```python
# Instead of generic errors, you now get:
{
    "code": "CHUNK_MISSING",           # What failed
    "message": "Chunks incomplete",    # Why it failed
    "details": "..."                   # Extra info
}
```

#### **Upload File with Hash Verification**
```python
# Hash verification happens automatically
from backend.utils.file_operations import calculate_file_hash

file_hash = calculate_file_hash(file_data)
# Send file upload - hash verified before & after storage
```

#### **Manual Cleanup (if needed)**
```python
from routes.helpers import get_content_model

content_model = get_content_model()
result = content_model.cleanup_orphaned_chunks()
print(f"Deleted {result['orphaned_chunks_removed']} orphaned chunks")
```

#### **Check Upload Session Status**
```python
db = get_db()
sessions = list(db.upload_sessions.find({'status': 'failed'}))
for session in sessions:
    print(f"{session['filename']}: {session['last_error']}")
```

---

### 🚨 Debug Error Codes

| Code | Means | Solution |
|------|-------|----------|
| `CHUNK_MISSING` | Upload incomplete (chunks lost) | User should check connection and retry |
| `CORRUPTION_DETECTED` | File hash mismatch | File corrupted - retry upload |
| `EMPTY_FILE` | 0 bytes | Invalid file or corruption |
| `FILE_NOT_FOUND` | Not in GridFS | File deleted or never uploaded |
| `READ_FAILED` | General read error | Retry or contact support |
| `WRITE_FAILED` | Failed to store | Retry - storage issue |
| `INVALID_HASH` | Hash verification failed | Retry upload |
| `RETRY_EXHAUSTED` | 3 retries failed | Network issue - user should retry later |

---

### 📈 Monitoring Queries

```javascript
// MongoDB queries for monitoring

// Active uploads
db.upload_sessions.find({status: 'in_progress'}).count()

// Failed uploads
db.upload_sessions.find({status: 'failed'})

// Total pending size
db.upload_sessions.aggregate([
    {$match: {status: 'in_progress'}},
    {$group: {_id: null, total: {$sum: '$total_size'}}}
])

// Orphaned chunks
db.fs.chunks.find({
    files_id: {$nin: db.fs.files.distinct('_id')}
}).count()

// Files with unverified uploads
db.shared_content.find({upload_verified: false}).count()
```

---

### 🔄 Retry Logic (Automatic)

No code needed! Retries happen automatically:

```
Network fails → Wait 0.5s → Retry 1
Still fails   → Wait 1.0s → Retry 2
Still fails   → Wait 2.0s → Retry 3
All fail      → Return error
```

---

### 📝 Logging

Check logs for errors:

```bash
[ERROR] GridFS upload failed: Connection timeout
[RETRY] Attempt 1 failed: Connection timeout. Retrying in 0.5s...
[RETRY] Operation succeeded on attempt 2/3
[CLEANUP] Removed 150 orphaned chunks from GridFS
[ERROR] Failed to retrieve file 507f1f77bcf86cd799439011: EOF error
```

---

### 🧹 Maintenance Tasks

**Daily (off-peak hours):**
```bash
# Clean orphaned chunks
curl -X POST http://localhost:5000/api/content/maintenance/cleanup-orphaned
```

**Weekly:**
```javascript
// Archive old failed sessions
db.upload_sessions.deleteMany({
    status: 'failed',
    created_at: {$lt: new Date(Date.now() - 7*24*60*60*1000)}
})
```

**Monthly:**
```bash
# Analyze storage usage
db.fs.files.stats()
# Compare with fs.chunks size
```

---

### 🚀 Integration Checklist

- [x] Error handling implemented
- [x] Hash verification working
- [x] Orphaned cleanup on TTL (2 hours)
- [x] Manual cleanup endpoint ready
- [x] Retry logic active
- [x] Upload session tracking
- [x] Specific error codes
- [ ] Setup cron job for daily cleanup (optional)
- [ ] Setup monitoring dashboard (optional)
- [ ] Configure alerting for failures (optional)

---

### 📚 Documentation

See **ERROR_HANDLING_GUIDE.md** for:
- Detailed implementation
- Error flow diagrams
- Testing scenarios
- Complete API reference

See **IMPLEMENTATION_SUMMARY.md** for:
- What changed
- Files modified
- New features overview

---

### ❓ FAQ

**Q: Will this slow down uploads?**
A: No. Hash verification runs in parallel with upload.

**Q: How long are upload sessions kept?**
A: 2 hours. Auto-deleted via MongoDB TTL index.

**Q: What if cleanup fails?**
A: Orphaned chunks will be cleaned up next time cleanup runs (usually within 2 hours).

**Q: Can I custom configure retry attempts?**
A: Yes - modify `FileOperationRetry(max_retries=3)` in code.

**Q: How much storage do orphaned chunks use?**
A: Depends on failed uploads. Typically 10-20% of total file size for partially uploaded files.

---

### 🎯 Next Steps

1. **Test** - Run through error scenarios
2. **Monitor** - Check upload_sessions daily
3. **Cleanup** - Set up cron job for daily cleanup
4. **Deploy** - Push to production when confident

---

**Last Updated:** March 17, 2026
**Version:** 1.0

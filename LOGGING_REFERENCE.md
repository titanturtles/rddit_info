# Logging Quick Reference

## Start App with Logging
```bash
cd /home/biajee/Documents/code/ai_trading3/rddt_info
python3 web_app.py
```

You'll see real-time logs showing all HTTP requests and responses!

---

## Log Files

| File | Purpose | Location |
|------|---------|----------|
| Console | Real-time output | Terminal window |
| dashboard.log | Permanent record | Same directory as web_app.py |

---

## View Logs

```bash
# View last 50 lines (most recent)
tail -50 dashboard.log

# Watch live (new logs appear in real-time)
tail -f dashboard.log

# View entire file
cat dashboard.log

# Search for specific patterns
grep "GET /api" dashboard.log
grep "[ERROR]" dashboard.log
grep "500" dashboard.log
```

---

## Log Format

Each request/response is separated by lines of equals signs:

```
================================================================================
[REQUEST] GET /api/dashboard/stats
[URL] http://localhost:5000/api/dashboard/stats
[CLIENT] 127.0.0.1
[HEADERS] {...headers...}
================================================================================

================================================================================
[RESPONSE] GET /api/dashboard/stats
[STATUS] 200 200 OK
[CONTENT-TYPE] application/json
[CONTENT-LENGTH] 234 bytes
[DATA] {
  "posts": 357,
  "comments": 523,
  ...
}
================================================================================
```

---

## Common Searches

| Goal | Command |
|------|---------|
| Find all requests | `grep "[REQUEST]" dashboard.log` |
| Find errors | `grep "[ERROR]" dashboard.log` |
| Find 500 errors | `grep "500" dashboard.log` |
| Find specific API | `grep "/api/sentiment" dashboard.log` |
| Find specific IP | `grep "192.168.1.100" dashboard.log` |
| Count requests | `grep "[REQUEST]" dashboard.log \| wc -l` |
| List unique endpoints | `grep "[REQUEST]" dashboard.log \| sort \| uniq` |

---

## Log Levels

- **INFO** - Normal operations (blue)
- **WARNING** - Warnings (yellow)
- **ERROR** - Errors/exceptions (red)
- **DEBUG** - Detailed info (gray)

---

## Real-Time Monitoring

**Terminal 1:**
```bash
python3 web_app.py
```

**Terminal 2:**
```bash
tail -f dashboard.log
```

**Terminal 3 (Browser):**
```
Open http://localhost:5000
Click around dashboard
Watch logs appear in Terminal 2!
```

---

## Analyzing Requests

### Check if API is being called
```bash
grep "GET /api/health" dashboard.log
# Should see many entries (health check runs every 30 sec)
```

### Check if API returns data
```bash
grep -A 5 "GET /api/sentiment" dashboard.log
# Look for [DATA] section showing JSON
```

### Find errors
```bash
grep "\[ERROR\]" dashboard.log
# Show error type and message
```

---

## Interpreting Status Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| 200 | Success | ✓ All working |
| 201 | Created | ✓ Resource created |
| 304 | Not Modified | ✓ Cached content |
| 400 | Bad Request | ✗ Invalid parameters |
| 404 | Not Found | ✗ Wrong endpoint |
| 500 | Server Error | ✗ App error (check [ERROR] logs) |
| 502 | Bad Gateway | ✗ Flask not responding |
| 503 | Unavailable | ✗ Database down |

---

## Troubleshooting with Logs

### Dashboard shows no data
1. Check logs for errors: `grep "[ERROR]" dashboard.log`
2. Look for 500 status codes: `grep "500" dashboard.log`
3. Check API responses: `grep "[DATA]" dashboard.log`

### Specific endpoint failing
1. Search for that endpoint: `grep "/api/endpoint" dashboard.log`
2. Check status code (should be 200)
3. If error, read the [ERROR] section

### Tracking user actions
1. Open logs file: `tail -f dashboard.log`
2. Click on dashboard in browser
3. Watch requests/responses appear in logs

---

## Sample Log Output

```
2025-11-07 14:27:45,156 - web_app - INFO -
================================================================================
2025-11-07 14:27:45,156 - web_app - INFO - [REQUEST] GET /api/health
2025-11-07 14:27:45,157 - web_app - INFO - [URL] http://localhost:5000/api/health
2025-11-07 14:27:45,157 - web_app - INFO - [CLIENT] 127.0.0.1
2025-11-07 14:27:45,157 - web_app - INFO - [HEADERS] {'User-Agent': 'Chrome/...'}
2025-11-07 14:27:45,157 - web_app - INFO - ================================================================================
2025-11-07 14:27:45,157 - web_app - INFO -
================================================================================
2025-11-07 14:27:45,157 - web_app - INFO - [RESPONSE] GET /api/health
2025-11-07 14:27:45,157 - web_app - INFO - [STATUS] 200 200 OK
2025-11-07 14:27:45,157 - web_app - INFO - [CONTENT-TYPE] application/json
2025-11-07 14:27:45,157 - web_app - INFO - [CONTENT-LENGTH] 85 bytes
2025-11-07 14:27:45,157 - web_app - INFO - [DATA] {
  "database": "connected",
  "status": "healthy",
  "timestamp": "2025-11-07T22:27:45.157342"
}
2025-11-07 14:27:45,157 - web_app - INFO - ================================================================================
```

---

## Clearing Old Logs

```bash
# Backup old log
cp dashboard.log dashboard.log.backup

# Or rotate with timestamp
cp dashboard.log dashboard.log.$(date +%Y%m%d_%H%M%S)

# Start fresh
rm dashboard.log
# App will create new log on next start
```

---

That's it! Now you have complete visibility into what your dashboard is doing at every step! 🔍

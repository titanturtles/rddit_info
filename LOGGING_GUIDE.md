# HTTP Request/Response Logging Guide

**Status:** ✅ Complete logging system implemented
**Date:** 2025-11-07
**Log Locations:**
- Console output (real-time)
- `dashboard.log` file (permanent record)

---

## Overview

The Flask web app now logs **every HTTP request and response** for comprehensive debugging.

### What Gets Logged

✅ **All Incoming Requests:**
- HTTP method (GET, POST, PUT, etc.)
- Request path and URL
- Client IP address
- All HTTP headers
- Request body (for POST/PUT/PATCH)

✅ **All Outgoing Responses:**
- HTTP status code
- Response content type
- Response size (bytes)
- Full JSON response data
- Response headers

✅ **All Errors:**
- Error type and message
- Full Python traceback
- Request path and method
- Stack trace for debugging

---

## Starting the App with Logging

```bash
cd /home/biajee/Documents/code/ai_trading3/rddt_info
python3 web_app.py
```

You'll see detailed logs like:

```
2025-11-07 14:27:45,138 - web_app - INFO - ================================================================================
2025-11-07 14:27:45,138 - web_app - INFO - Reddit Trading Bot Web Dashboard Starting
2025-11-07 14:27:45,138 - web_app - INFO - ================================================================================

[Later when a request comes in...]

2025-11-07 14:27:45,156 - web_app - INFO -
================================================================================
2025-11-07 14:27:45,156 - web_app - INFO - [REQUEST] GET /api/health
2025-11-07 14:27:45,157 - web_app - INFO - [URL] http://localhost/api/health
2025-11-07 14:27:45,157 - web_app - INFO - [CLIENT] 127.0.0.1
2025-11-07 14:27:45,157 - web_app - INFO - [HEADERS] {'User-Agent': 'Werkzeug/3.1.3', ...}
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

## Log Format

### Request Log
```
[REQUEST] {METHOD} {PATH}
[URL] {FULL_URL}
[CLIENT] {IP_ADDRESS}
[HEADERS] {HTTP_HEADERS}
[BODY] {REQUEST_BODY}  # Only for POST/PUT/PATCH
```

**Example:**
```
[REQUEST] GET /api/dashboard/stats
[URL] http://localhost:5000/api/dashboard/stats
[CLIENT] 192.168.1.100
[HEADERS] {'User-Agent': 'Chrome/...', 'Accept': 'application/json', ...}
```

### Response Log
```
[RESPONSE] {METHOD} {PATH}
[STATUS] {STATUS_CODE} {STATUS_TEXT}
[CONTENT-TYPE] {CONTENT_TYPE}
[CONTENT-LENGTH] {SIZE_IN_BYTES}
[DATA] {JSON_DATA}  # For JSON responses
```

**Example:**
```
[RESPONSE] GET /api/dashboard/stats
[STATUS] 200 200 OK
[CONTENT-TYPE] application/json
[CONTENT-LENGTH] 234 bytes
[DATA] {
  "posts": 357,
  "comments": 523,
  "sentiments_analyzed": 1341,
  ...
}
```

### Error Log
```
[ERROR] Exception occurred
[TYPE] {EXCEPTION_TYPE}
[MESSAGE] {ERROR_MESSAGE}
[PATH] {REQUEST_PATH}
[METHOD] {REQUEST_METHOD}
[TRACEBACK] {FULL_PYTHON_TRACEBACK}
```

**Example:**
```
[ERROR] Exception occurred
[TYPE] KeyError
[MESSAGE] 'posts' not found in data
[PATH] /api/dashboard/stats
[METHOD] GET
[TRACEBACK]
  File "web_app.py", line 156, in dashboard_stats
    posts = data['posts']
KeyError: 'posts'
```

---

## Reading the Log File

The log file `dashboard.log` contains all logs in permanent storage:

```bash
# View the entire log
cat dashboard.log

# View the last 50 lines (most recent)
tail -50 dashboard.log

# Search for specific requests
grep "GET /api" dashboard.log
grep "\[REQUEST\]" dashboard.log
grep "\[ERROR\]" dashboard.log

# Follow log in real-time (new lines appear as requests come in)
tail -f dashboard.log

# Search for specific status codes
grep "\[STATUS\] 500" dashboard.log  # Find errors
grep "\[STATUS\] 200" dashboard.log  # Find successes
```

---

## Console Output

When running `python3 web_app.py`, all logs appear in the terminal:

```
Terminal Output:
================================================================================
[REQUEST] GET /api/sentiment/summary
[URL] http://localhost:5000/api/sentiment/summary
[CLIENT] 127.0.0.1
[HEADERS] {...}
================================================================================

[RESPONSE] GET /api/sentiment/summary
[STATUS] 200 200 OK
[CONTENT-TYPE] application/json
[CONTENT-LENGTH] 89 bytes
[DATA] {
  "bullish": 4824,
  "bearish": 2297,
  "neutral": 1066,
  "total": 8187
}
================================================================================
```

### Color-Coded Output
- **INFO logs** = Blue (normal operations)
- **WARNING logs** = Yellow (warnings)
- **ERROR logs** = Red (errors/exceptions)
- **DEBUG logs** = Gray (detailed info)

---

## Debugging Tips

### 1. Finding Failed Requests
```bash
# Search for non-200 status codes
grep -E "\[STATUS\] (4|5)[0-9]{2}" dashboard.log

# Or specifically 500 errors
grep "\[STATUS\] 500" dashboard.log
```

### 2. Tracing a Specific API Call
```bash
# Find all requests to a specific endpoint
grep "/api/dashboard/stats" dashboard.log

# Find requests from a specific IP
grep "127.0.0.1" dashboard.log
```

### 3. Finding Error Details
```bash
# Find all errors
grep "\[ERROR\]" dashboard.log

# Find specific error types
grep "KeyError" dashboard.log
grep "TypeError" dashboard.log
grep "AttributeError" dashboard.log
```

### 4. Performance Monitoring
```bash
# Find slow requests (by checking timestamps)
# Manual: Look at time difference between [REQUEST] and [RESPONSE]

# Count requests per endpoint
grep "\[REQUEST\]" dashboard.log | sort | uniq -c
```

---

## Log Analysis Examples

### Example 1: Debugging a 404 Error
```bash
$ grep "404" dashboard.log

Output:
[RESPONSE] GET /api/invalid/endpoint
[STATUS] 404 404 NOT FOUND
```
**Action:** Endpoint doesn't exist or wrong URL used

### Example 2: Debugging a 500 Error
```bash
$ grep -A 10 "\[STATUS\] 500" dashboard.log

Output:
[RESPONSE] GET /api/dashboard/stats
[STATUS] 500 500 INTERNAL SERVER ERROR
[ERROR] Exception occurred
[TYPE] ValueError
[MESSAGE] invalid literal for int(): 'abc'
[TRACEBACK]
  File "web_app.py", line 156, in dashboard_stats
    posts = int(data['count'])
ValueError: invalid literal for int(): 'abc'
```
**Action:** Data is in wrong format, need to validate input

### Example 3: Monitoring API Usage
```bash
$ grep "\[REQUEST\] GET /api" dashboard.log

Output:
[REQUEST] GET /api/health
[REQUEST] GET /api/dashboard/stats
[REQUEST] GET /api/sentiment/summary
[REQUEST] GET /api/stocks/top
[REQUEST] GET /api/llm/recent
[REQUEST] GET /api/health  # Health check runs every 30 seconds
```
**Insight:** APIs are being called regularly as expected

---

## Log Rotation (Large Files)

When `dashboard.log` becomes large:

```bash
# Backup and rotate logs
mv dashboard.log dashboard.log.bak

# Compress old log
gzip dashboard.log.bak

# Start fresh
python3 web_app.py
```

---

## Real-Time Monitoring

### Monitor Logs Live While Using Dashboard

**Terminal 1 - Run Flask:**
```bash
python3 web_app.py
```

**Terminal 2 - Watch Logs:**
```bash
tail -f dashboard.log
```

**Terminal 3 - Use Dashboard:**
```bash
# Open browser to http://localhost:5000
# As you interact with dashboard, see logs appear in Terminal 2
```

---

## Log Structure

The logging system includes multiple handlers:

### 1. Console Handler
- Outputs to terminal (stdout)
- Real-time viewing while app runs
- Includes timestamp, logger name, level, message

### 2. File Handler
- Writes to `dashboard.log`
- Permanent record of all requests/responses
- Survives app restart

### 3. Error Handler
- Catches all unhandled exceptions
- Logs full traceback
- Returns error JSON to client

---

## Understanding Request/Response Flow

### Normal Flow (Success)
```
Browser Request
    ↓
[REQUEST] Log written
    ↓
Flask processes request
    ↓
[RESPONSE] Log written
    ↓
Browser receives response
```

**Console shows:**
```
[REQUEST] GET /api/health
[RESPONSE] GET /api/health
[STATUS] 200 200 OK
```

### Error Flow
```
Browser Request
    ↓
[REQUEST] Log written
    ↓
Flask encounters error
    ↓
Exception caught
    ↓
[ERROR] Log written with traceback
    ↓
Error response sent to browser
```

**Console shows:**
```
[REQUEST] GET /api/bad-endpoint
[ERROR] Exception occurred
[TYPE] ValueError
[MESSAGE] ...
[TRACEBACK] ...
[RESPONSE] GET /api/bad-endpoint
[STATUS] 500 500 INTERNAL SERVER ERROR
```

---

## Log Filtering

### Filter by Status Code
```bash
# Find all successful requests
grep "\[STATUS\] 200" dashboard.log

# Find all errors
grep -E "\[STATUS\] (4|5)[0-9]{2}" dashboard.log

# Find specific errors
grep "\[STATUS\] 404" dashboard.log  # Not found
grep "\[STATUS\] 500" dashboard.log  # Server error
```

### Filter by Endpoint
```bash
grep "/api/dashboard" dashboard.log
grep "/api/sentiment" dashboard.log
grep "/api/stocks" dashboard.log
grep "/api/llm" dashboard.log
```

### Filter by Time
```bash
# Find requests from specific hour
grep "14:27" dashboard.log  # 2:27 PM
grep "09:30" dashboard.log  # 9:30 AM
```

---

## Common Log Messages

| Message | Meaning | Action |
|---------|---------|--------|
| `[REQUEST] GET /api/health` | Health check from browser | Normal, happens every 30 sec |
| `[RESPONSE] ... [STATUS] 200` | Successful request | Everything OK ✓ |
| `[RESPONSE] ... [STATUS] 404` | Endpoint not found | Check URL spelling |
| `[RESPONSE] ... [STATUS] 500` | Server error | Check [ERROR] logs for details |
| `[ERROR] Exception occurred` | Unhandled error in code | Check [TYPE] and [TRACEBACK] |
| `[ERROR] KeyError` | Missing data in dict | Check data structure |
| `[ERROR] AttributeError` | Missing attribute | Check object attributes |

---

## Tips for Effective Debugging

1. **Start with the request log**
   - Check if request was received correctly
   - Verify headers and parameters

2. **Check the response log**
   - Verify status code (200 = good, 4xx = client error, 5xx = server error)
   - Check data format and content

3. **Look for errors**
   - Search for `[ERROR]` in logs
   - Read the traceback carefully
   - Identify the exact line that failed

4. **Compare before/after**
   - Look at successful requests
   - Compare with failed requests
   - Find what's different

5. **Use grep to search**
   - `grep "pattern" dashboard.log` - find lines with pattern
   - `grep -A 5 "pattern"` - show 5 lines after match
   - `grep -B 5 "pattern"` - show 5 lines before match

---

## Summary

**Logging system captures:**
- ✅ Every HTTP request (method, path, headers, body)
- ✅ Every HTTP response (status, content-type, data)
- ✅ All errors with full traceback
- ✅ Complete audit trail of all operations

**Output locations:**
- 📺 Console (real-time while app running)
- 📄 `dashboard.log` (permanent record)

**Access logs:**
- View in terminal: `tail -f dashboard.log`
- Search: `grep "pattern" dashboard.log`
- Analyze: Parse with command line tools

**Benefits:**
- 🔍 Complete visibility into what the app is doing
- 🐛 Easy debugging of issues
- 📊 Performance monitoring
- 🔐 Audit trail for security
- 📝 Complete record for troubleshooting

---

## Quick Reference

```bash
# View recent logs
tail -50 dashboard.log

# Watch logs in real-time
tail -f dashboard.log

# Find errors
grep "ERROR" dashboard.log

# Find specific endpoint
grep "/api/dashboard" dashboard.log

# Find failed requests
grep -E "STATUS.*[45][0-9][0-9]" dashboard.log

# Count requests by endpoint
grep "\[REQUEST\]" dashboard.log | sort | uniq -c

# View specific time period
grep "14:27" dashboard.log

# Backup old log
cp dashboard.log dashboard.log.$(date +%s).bak
```

Your dashboard now has enterprise-grade logging! 📊

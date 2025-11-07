# Troubleshooting: Dashboard Shows No Data

This guide will help you diagnose why data isn't showing on your dashboard, even though the backend is working.

---

## Step 1: Start Fresh (Clear Any Old Processes)

```bash
# Kill any existing Python processes on port 5000
lsof -i :5000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start the Flask app
cd /home/biajee/Documents/code/ai_trading3/rddt_info
python3 web_app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

---

## Step 2: Test the Debug Page First

Before testing the main dashboard, test the debug page:

**URL:** http://localhost:5000/debug

This page:
1. Logs everything that happens
2. Tests all API endpoints
3. Shows exactly what's working and what's not
4. Displays in a readable console format

### What to look for:
- `[LOAD] Chart.js loaded` ✓
- `[LOAD] common.js loaded` ✓
- `window.dashboardUtils = object` ✓
- `[LOAD] dashboard.js loaded successfully` ✓
- All API tests showing `[200]` status ✓

If you see any `[ERROR]` lines, screenshot them and share them.

---

## Step 3: Check Browser Console (F12)

This is the MOST IMPORTANT step:

1. Open http://localhost:5000/debug (or http://localhost:5000)
2. Press **F12** to open Developer Tools
3. Click on the **Console** tab
4. Look at the messages (they're logged with [Dashboard] and [Common] prefixes)

### Expected messages (in order):
```
[Common] Loading common.js utilities...
[Common] API_BASE_URL: /api
[Common] window.dashboardUtils exported successfully
[Common] Available utilities: (18) ['fetchAPI', 'formatNumber', ...]
[Dashboard] Script starting...
[Dashboard] window.dashboardUtils exists? true
[Dashboard] Successfully destructuring from window.dashboardUtils
[Dashboard] Script loaded, waiting for DOMContentLoaded event
[Dashboard] DOMContentLoaded event fired
[Dashboard] Initializing...
[Dashboard] Functions verified, starting data loads...
[Dashboard] Loading dashboard stats...
[Dashboard] Dashboard stats data: {posts: 357, comments: 523, ...}
[Dashboard] Initialization complete
```

### If you see errors:
- Screenshot the red error messages
- Note the exact error text
- This will help identify the problem

### Common errors and what they mean:

| Error | Meaning | Solution |
|-------|---------|----------|
| `Uncaught TypeError: window.dashboardUtils is undefined` | common.js didn't load | Check Network tab - did /static/js/common.js return 200? |
| `Uncaught SyntaxError: Unexpected token` | JavaScript syntax error | There's a bug in the JavaScript files |
| `CORS error` | API call blocked by browser | Check Network tab - are API calls getting 200 status? |
| `Cannot read property 'textContent' of null` | DOM element missing | Element ID doesn't exist in HTML |

---

## Step 4: Check Network Tab

1. Open F12 Developer Tools
2. Go to **Network** tab
3. Refresh the page (Ctrl+R)
4. Look for these requests:

| Request | Should be | Expected |
|---------|-----------|----------|
| / | 200 | HTML page |
| common.js | 200 | JavaScript file |
| dashboard.js | 200 | JavaScript file |
| chart.min.js | 200 | Chart.js library |
| style.css | 200 | CSS file |
| /api/dashboard/stats | 200 | JSON data |
| /api/sentiment/summary | 200 | JSON data |
| /api/stocks/top | 200 | JSON data |

If any shows red (4xx or 5xx status):
- Click on it to see the error details
- Screenshot and share the error

---

## Step 5: Manual API Testing

If debug page shows errors, test the APIs manually:

```bash
# Test 1: Health check
curl http://localhost:5000/api/health

# Test 2: Dashboard stats
curl http://localhost:5000/api/dashboard/stats

# Test 3: Sentiment summary
curl http://localhost:5000/api/sentiment/summary

# Test 4: Top stocks
curl http://localhost:5000/api/stocks/top?limit=3
```

All should return JSON. If any returns an error, that's the problem.

---

## Step 6: Check if MongoDB Has Data

```bash
mongosh
use reddit_trading
db.sentiment_analysis.count()  # Should be > 0
db.posts.count()               # Should be > 0
```

If counts are 0, the bot hasn't collected data yet.

---

## Detailed Diagnostic Flow

Start with this flow to pinpoint the issue:

```
Is Flask running?
  └─ NO: Start it: python3 web_app.py
  └─ YES: Go to next

Can you access http://localhost:5000?
  └─ NO: Flask might not be running or using different port
  └─ YES: Go to next

Does the HTML page load (shows page structure)?
  └─ NO: Flask is broken
  └─ YES: Go to next

Open F12 Console - do you see [Common] logs?
  └─ NO: common.js didn't load - check Network tab
  └─ YES: Go to next

Do you see [Dashboard] logs?
  └─ NO: dashboard.js didn't load - check Network tab
  └─ YES: Go to next

Do you see "window.dashboardUtils exists? true"?
  └─ NO: common.js didn't export properly
  └─ YES: Go to next

Do you see API data logged ("Dashboard stats data: {...")?
  └─ NO: API call failed - check Network tab for 404/500 errors
  └─ YES: Go to next

Do you see data on the page?
  └─ NO: This is unexpected - the data is being loaded but not displayed
           → Check if element IDs in HTML match the code
  └─ YES: DONE! Dashboard is working!
```

---

## If Data Loads But Doesn't Display

If console shows data is being fetched but nothing appears on the page:

1. **Check element IDs** - Open the HTML (right-click → View Page Source) and verify:
   - `<div id="posts-count">` exists
   - `<div id="comments-count">` exists
   - `<div id="sentiments-count">` exists
   - `<div id="stocks-count">` exists
   - `<div id="llm-calls">` exists
   - `<div id="patterns-count">` exists

2. **Check CSS** - The text might be white on white background:
   - Open F12
   - Click the Element Inspector (arrow icon)
   - Click on a stat card
   - Check if it has text (might just be invisible due to CSS)

3. **Check browser cache** - Old CSS might be cached:
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
   - Or clear cache: F12 → Application → Clear Storage

---

## Quick Fixes to Try

1. **Hard refresh the page:**
   ```
   Ctrl+Shift+R  (Windows/Linux)
   Cmd+Shift+R   (Mac)
   ```

2. **Clear browser cache:**
   - F12 → Application tab → Clear Storage → Click "Clear site data"

3. **Restart Flask:**
   ```bash
   # Kill Flask
   lsof -i :5000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

   # Start again
   python3 web_app.py
   ```

4. **Check MongoDB is running:**
   ```bash
   mongosh  # If this fails, start MongoDB with: mongod
   ```

---

## Complete Reproduction Steps

If you're still having issues, follow these EXACT steps:

1. Open terminal
2. `cd /home/biajee/Documents/code/ai_trading3/rddt_info`
3. `lsof -i :5000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true`
4. `sleep 2`
5. `python3 web_app.py`
6. Wait for "Running on http://0.0.0.0:5000"
7. Open browser: http://localhost:5000/debug
8. Open F12 Console tab
9. **Take a screenshot of the console output**
10. Share that screenshot

---

## Information to Share When Asking for Help

If you still need help, please provide:

1. **Screenshot of F12 Console tab** (shows all [Dashboard] and [Common] messages)
2. **Screenshot of F12 Network tab** (shows which requests succeeded/failed)
3. **Any red error messages** (copy the full text)
4. **What you see on the page** (blank? dashes? error message?)
5. **Output of:** `curl http://localhost:5000/api/health`

---

## Quick Reference: Port 5000 Issues

If you get "Address already in use":

```bash
# Find what's using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use a different port in web_app.py:
# Change: app.run(port=5000)
# To: app.run(port=8000)
```

---

## Summary

**The data IS being fetched** - the backend is confirmed working.
**The issue is in the browser** - JavaScript or DOM related.

The console logs will tell you exactly what's happening. Check F12 console first, then work through the diagnostic flow above.

If you follow all these steps and still have issues, share:
- Screenshot of F12 Console
- Screenshot of F12 Network tab
- The specific error messages you see

This will help identify the exact problem quickly.

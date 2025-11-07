# Web App Debugging Guide

## Issue: Data Not Showing on Dashboard

### Quick Diagnosis

**Step 1: Test the API endpoints directly**

Visit these URLs in your browser to see raw JSON data:
- http://localhost:5000/api/dashboard/stats
- http://localhost:5000/api/sentiment/summary
- http://localhost:5000/api/stocks/top?limit=5
- http://localhost:5000/api/health

If you see JSON data, the backend is working! ✓

### Step 2: Check browser console for errors

1. Open http://localhost:5000 in your browser
2. Press `F12` to open Developer Tools
3. Go to the `Console` tab
4. Look for red error messages

Common errors:
- `Uncaught TypeError: window.dashboardUtils is undefined`
- `Uncaught ReferenceError: createChart is not defined`
- `Fetch failed: 404 Not Found`
- `Uncaught TypeError: Cannot read property of undefined`

### Step 3: Test the Test Page

Visit http://localhost:5000/test to see API responses in real-time.

This page:
- Tests all 4 main API endpoints
- Shows responses on the page
- Logs to browser console
- Helps identify which API is failing

### Step 4: Check Flask Debug Output

Look at the terminal where you ran `python web_app.py`:

Good signs:
```
* Running on http://0.0.0.0:5000
[REMOTE_ADDR] GET /api/dashboard/stats - 200 OK
[REMOTE_ADDR] GET /api/sentiment/summary - 200 OK
```

Bad signs:
```
[REMOTE_ADDR] GET /api/stocks/top - 500 INTERNAL SERVER ERROR
Traceback (most recent call last):
  ...
```

---

## Common Issues & Fixes

### Issue 1: "Cannot read property 'bullish' of undefined"

**Cause**: API returned `null` instead of data

**Fix**: Check if MongoDB is running
```bash
mongosh
db.adminCommand({ping: 1})
```

### Issue 2: "setElementText is not a function"

**Cause**: common.js not loaded before dashboard.js

**Fix**: Check that scripts load in correct order in HTML:
```html
<script src="{{ url_for('static', filename='js/common.js') }}"></script>
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
```

### Issue 3: Charts not rendering

**Cause**: Chart.js not loaded or canvas element missing

**Fix**: Verify:
1. Chart.js CDN is accessible (http://localhost:5000/test checks this)
2. Canvas IDs in HTML match JavaScript code
   - HTML: `<canvas id="sentimentChart"></canvas>`
   - JavaScript: `createChart('sentimentChart', config)`

### Issue 4: 404 on API endpoints

**Cause**: Wrong endpoint path

**Fix**: Verify endpoint in common.js:
```javascript
const API_BASE_URL = '/api';  // Correct

// When calling:
fetchAPI('/dashboard/stats')  // becomes /api/dashboard/stats
```

### Issue 5: All "--" dashes showing

**Cause**: Data loading but elements not updating

**Fix**: Check element IDs in HTML match JavaScript

HTML example:
```html
<div class="stat-value" id="posts-count">--</div>
```

JavaScript:
```javascript
setElementText('posts-count', data.posts);
```

IDs must match!

---

## Manual Testing

### Test with curl

```bash
# Test dashboard stats
curl http://localhost:5000/api/dashboard/stats

# Test sentiment summary
curl http://localhost:5000/api/sentiment/summary

# Test top stocks
curl http://localhost:5000/api/stocks/top?limit=3

# Test health
curl http://localhost:5000/api/health
```

All should return JSON with HTTP 200.

### Test database directly

```bash
mongosh
use reddit_trading
db.sentiment_analysis.count()  # Should be > 0
db.posts.count()              # Should be > 0
```

If counts are 0, the bot hasn't collected data yet!

---

## Browser Console Logging

To add debugging, edit `static/js/dashboard.js` and add `console.log()`:

```javascript
async function loadDashboardStats() {
    console.log('Loading dashboard stats...');
    const data = await fetchAPI('/dashboard/stats');
    console.log('Received data:', data);

    if (data) {
        console.log('Setting element texts...');
        setElementText('posts-count', data.posts);
        // ... etc
    } else {
        console.error('Failed to load data');
    }
}
```

Then press F12 and watch the console output as the page loads.

---

## Step-by-Step Diagnosis

### Step 1: Backend Working?

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/path/to/rddt_info')
from web_app import app

client = app.test_client()
response = client.get('/api/dashboard/stats')
print(f"Status: {response.status_code}")
print(f"Data: {response.get_json()}")
PYEOF
```

Expected: Status 200 with JSON data

### Step 2: Database Has Data?

```bash
mongosh
use reddit_trading
db.sentiment_analysis.find({}).limit(1).pretty()
```

Expected: Returns a record (not empty)

### Step 3: Frontend Loads?

Visit http://localhost:5000 and right-click → View Page Source

Look for:
- `<script src="/static/js/common.js"></script>` ✓
- `<script src="/static/js/dashboard.js"></script>` ✓
- Chart.js CDN link ✓
- Element IDs like `<div id="posts-count">` ✓

### Step 4: Scripts Execute?

Open Developer Tools (F12) → Console

Type:
```javascript
typeof fetchAPI  // Should show: "function"
typeof createChart  // Should show: "function"
API_BASE_URL  // Should show: "/api"
```

If any show "undefined", scripts didn't load properly.

---

## Port Already in Use

If you get "Address already in use":

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
# Edit web_app.py line ~380:
app.run(port=8000)  # Change 5000 to 8000
```

---

## Network Issues

If `/test` page shows errors connecting to API:

1. Check CORS is enabled in web_app.py:
   ```python
   from flask_cors import CORS
   CORS(app)  # Should be there
   ```

2. Verify Flask is running without errors:
   ```
   python web_app.py
   ```

3. Try accessing API directly with `curl`:
   ```bash
   curl http://localhost:5000/api/health
   ```

---

## MongoDB Connection Issues

If database endpoints return empty:

```bash
# Check MongoDB is running
mongosh
```

If mongosh fails: MongoDB is not running, start it:
```bash
mongod  # On macOS/Linux
```

---

## Slow or Unresponsive Dashboard

### Check Response Times

Open F12 → Network tab, then refresh page.

Each request should take < 1 second:
- `/api/dashboard/stats` - ~100ms
- `/api/sentiment/summary` - ~200ms
- `/api/stocks/top` - ~500ms (slower, manual aggregation)

If requests take > 5 seconds:
- MongoDB might be slow
- Your system might be overloaded
- Too much data in collection (add indexes)

### Solution

Create indexes in MongoDB:
```javascript
db.sentiment_analysis.createIndex({ stock_symbol: 1 })
db.posts.createIndex({ created_at: -1 })
db.llm_responses.createIndex({ timestamp: -1 })
```

---

## Still Stuck?

Create a minimal test:

1. **Create** `/tmp/test_api.html`:
```html
<h1>Test</h1>
<div id="result"></div>
<script>
fetch('/api/health')
  .then(r => r.json())
  .then(d => document.getElementById('result').innerHTML = JSON.stringify(d))
  .catch(e => document.getElementById('result').innerHTML = 'Error: ' + e)
</script>
```

2. **Visit** http://localhost:5000/test (created in our debugging)

3. **Check** if it loads health data - if yes, API works!

---

## Summary Checklist

- [ ] MongoDB is running (`mongosh` works)
- [ ] Flask app is running (`python web_app.py`)
- [ ] Can access http://localhost:5000 (page loads)
- [ ] Test page works (http://localhost:5000/test shows data)
- [ ] API endpoints return JSON (test with curl)
- [ ] Browser console has no errors (F12)
- [ ] Element IDs match between HTML and JavaScript
- [ ] common.js loads before dashboard.js
- [ ] Chart.js CDN is accessible

If all checked: **Dashboard should work!**

If not: Use the detailed steps above to identify which part failed.

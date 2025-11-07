# Web Application Guide - Reddit Trading Bot Monitor

**Status:** ✅ Complete and Ready to Use
**Framework:** Flask
**Frontend:** HTML/CSS/JavaScript with Chart.js
**Real-time Updates:** Auto-refresh every 15-60 seconds

---

## Overview

The web application provides a comprehensive dashboard to monitor your Reddit trading bot in real-time. Track sentiment analysis, LLM API calls, trading patterns, and stock mentions all in one place.

### Features

✅ **Real-time Dashboard** - Live statistics and charts
✅ **Sentiment Analysis** - Visualization of bullish/bearish/neutral sentiment
✅ **Stock Tracking** - Top mentioned stocks with sentiment breakdowns
✅ **LLM Monitoring** - Track all API calls, success rates, and errors
✅ **Pattern Detection** - View detected trading patterns and signals
✅ **Data Timeline** - Historical view of data collection
✅ **Auto-refresh** - Automatic updates every 15-60 seconds
✅ **Responsive Design** - Works on desktop, tablet, and mobile

---

## Installation

### 1. Install Dependencies

```bash
pip install Flask==2.3.3 flask-cors==4.0.0
```

Or update requirements:

```bash
pip install -r requirements.txt
```

### 2. Project Structure

```
rddt_info/
├── web_app.py              # Main Flask application
├── templates/
│   ├── index.html          # Dashboard page
│   ├── llm_monitor.html    # LLM monitoring page
│   ├── stocks.html         # Stocks and sentiment page
│   └── patterns.html       # Trading patterns page
└── static/
    ├── css/
    │   └── style.css       # Main stylesheet
    └── js/
        ├── common.js       # Shared utility functions
        ├── dashboard.js    # Dashboard-specific code
        ├── llm_monitor.js  # LLM monitor-specific code
        ├── stocks.js       # Stocks page-specific code
        └── patterns.js     # Patterns page-specific code
```

---

## Running the Web App

### Start the Web Server

```bash
python web_app.py
```

You should see:

```
Starting Reddit Trading Bot Web Dashboard
Dashboard available at http://localhost:5000
```

### Access the Dashboard

Open your browser and navigate to:

```
http://localhost:5000
```

### Running Alongside the Bot

You can run both the bot and web app simultaneously:

```bash
# Terminal 1: Run the bot
python main.py --mode full

# Terminal 2: Run the web app
python web_app.py
```

Both will work together, with the web app displaying real-time data from the bot.

---

## Pages and Features

### 1. Dashboard (/)

**Main overview page with:**

- **Stats Cards** - Total posts, comments, sentiments, stocks, LLM calls, patterns
- **Sentiment Distribution** - Doughnut chart of bullish/neutral/bearish split
- **Data Timeline** - Line chart showing posts collected over 7 days
- **Top Stocks** - Table of most mentioned stocks with sentiment breakdown
- **Recent LLM Calls** - Latest 5 LLM API calls with status

**Auto-refresh:** Every 30 seconds

**Key Metrics:**
- Reddit Posts: Total posts analyzed from configured subreddits
- Comments: Total comments analyzed
- Sentiments: Total sentiment analyses performed
- Stocks: Unique stock symbols mentioned
- LLM Calls: Total API calls to language model
- Patterns: Trading patterns detected

---

### 2. Stocks (/stocks)

**Stock-focused analysis page:**

- **Sentiment Cards** - Bullish, Neutral, Bearish counts
- **Distribution Chart** - Bar chart of sentiment distribution
- **Top Stocks Table** - Detailed breakdown per stock:
  - Symbol
  - Total mentions
  - Bullish percentage
  - Bullish/bearish/neutral count
  - Average sentiment score

**Controls:**
- Limit selector (Top 5/10/20/50)
- Refresh button

**Color Coding:**
- Green: Bullish sentiment (buy signal)
- Gray: Neutral sentiment (no clear direction)
- Red: Bearish sentiment (sell signal)

---

### 3. LLM Monitor (/llm-monitor)

**Dedicated LLM API monitoring:**

- **LLM Stats Cards** - Total calls, successful, errors, exceptions, success rate
- **Status Distribution** - Pie chart of call outcomes
- **Recent Calls Table** - Last 20 LLM API calls with:
  - Timestamp
  - Model used
  - Status (success/error/exception)
  - Prompt length
  - Response length
  - Error details if any

- **Errors Section** - Recent API errors with details

**Auto-refresh:** Every 15 seconds

**Status Indicators:**
- ✓ Success (Green) - API call completed successfully
- ⚠ Error (Yellow) - HTTP/API error occurred
- ✗ Exception (Red) - System exception (timeout, network, etc.)

---

### 4. Patterns (/patterns)

**Trading pattern analysis page:**

- **Pattern Stats** - Total, high confidence, medium confidence patterns
- **Pattern Cards** - Visual cards for each detected pattern:
  - Stock symbol
  - Pattern type (Breakout, Reversal, Consolidation, Momentum)
  - Confidence score
  - Description
  - Detection timestamp

- **Pattern Types Legend** - Explanation of each pattern type

**Confidence Levels:**
- 🔥 High (> 70%) - Strong signal
- ⭐ Medium (50-70%) - Moderate signal
- 📊 Low (< 50%) - Weak signal

---

## API Endpoints

All endpoints return JSON data:

### Dashboard Data

**GET `/api/dashboard/stats`**
```json
{
  "posts": 150,
  "comments": 450,
  "sentiments_analyzed": 600,
  "unique_stocks": 25,
  "llm_calls": 800,
  "patterns_detected": 12
}
```

**GET `/api/sentiment/summary`**
```json
{
  "bullish": 350,
  "neutral": 200,
  "bearish": 50,
  "total": 600
}
```

**GET `/api/stocks/top?limit=10`**
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "mentions": 45,
      "bullish": 30,
      "bearish": 10,
      "neutral": 5,
      "bullish_ratio": 0.67,
      "avg_sentiment_score": 0.45
    }
  ]
}
```

### LLM Monitoring

**GET `/api/llm/stats`**
```json
{
  "total_calls": 800,
  "success": 760,
  "errors": 30,
  "exceptions": 10,
  "success_rate": 95.0
}
```

**GET `/api/llm/recent?limit=20`**
```json
{
  "calls": [
    {
      "id": "ObjectId",
      "timestamp": "2025-11-06T12:30:45.123Z",
      "model": "deepseek-chat",
      "status": "success",
      "prompt_length": 245,
      "response_length": 18,
      "error": null
    }
  ]
}
```

**GET `/api/llm/errors`**
```json
{
  "errors": [
    {
      "id": "ObjectId",
      "timestamp": "2025-11-06T12:25:00.000Z",
      "status": "error",
      "error": "Status 429: Rate limited",
      "prompt": "Extract stocks from..."
    }
  ]
}
```

### Patterns

**GET `/api/patterns/latest?limit=10`**
```json
{
  "patterns": [
    {
      "id": "ObjectId",
      "symbol": "TSLA",
      "pattern_type": "Breakout",
      "confidence": 0.85,
      "timestamp": "2025-11-06T12:00:00.000Z",
      "description": "Strong upward momentum with increased mentions"
    }
  ]
}
```

### Health Check

**GET `/api/health`**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-06T12:30:45.123Z"
}
```

---

## Customization

### Change Port

Edit `web_app.py`:

```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,  # Change this
        debug=False,
        threaded=True
    )
```

### Change Refresh Intervals

Edit JavaScript files in `static/js/`:

```javascript
// In dashboard.js
setInterval(loadDashboardStats, 30000);  // 30 seconds
```

Change the number (in milliseconds) to your desired interval.

### Custom Colors

Edit `static/css/style.css`:

```css
:root {
    --primary-color: #0066cc;      /* Change primary color */
    --success-color: #28a745;      /* Change success color */
    --error-color: #dc3545;        /* Change error color */
    /* ... more colors ... */
}
```

### Add Custom Pages

1. Create HTML template in `templates/`
2. Create JavaScript in `static/js/`
3. Add route in `web_app.py`:

```python
@app.route('/custom-page')
def custom_page():
    return render_template('custom_page.html')
```

---

## Troubleshooting

### Port Already in Use

```bash
# Change the port in web_app.py or kill the process
lsof -i :5000
kill -9 <PID>
```

### Database Connection Failed

Check MongoDB is running:

```bash
mongosh
use reddit_trading
db.posts.count()
```

### No Data Appearing

1. Make sure bot is running: `python main.py --mode analyze`
2. Wait 30 seconds for first refresh
3. Check MongoDB has data: `mongosh` → `use reddit_trading` → `db.posts.count()`
4. Check browser console for errors (F12)

### Charts Not Loading

- Check Chart.js CDN is accessible
- Check browser console for JavaScript errors
- Try clearing browser cache

### Slow Dashboard

1. Reduce auto-refresh intervals (see Customization section)
2. Check MongoDB performance: `mongosh` → `db.stats()`
3. Check network tab in browser DevTools (F12)

---

## Performance Tips

1. **Adjust Refresh Rates** - Longer intervals = less server load
   ```javascript
   setInterval(loadDashboardStats, 60000);  // 60 seconds instead of 30
   ```

2. **Limit Data** - Reduce query limits for faster responses
   ```javascript
   const data = await fetchAPI('/llm/recent?limit=10');  // Instead of 20
   ```

3. **Database Indexing** - Create indexes on frequently queried fields
   ```javascript
   db.llm_responses.createIndex({ timestamp: -1 })
   db.sentiment_analysis.createIndex({ stock_symbol: 1 })
   ```

4. **Pagination** - Implement pagination for large datasets (future enhancement)

---

## Security Notes

⚠️ **Warning:** This dashboard is designed for local/private network use.

For production deployment:

1. **Enable HTTPS** - Use SSL certificates
2. **Add Authentication** - Implement login system
3. **Restrict Access** - Use firewall rules or reverse proxy
4. **Validate Input** - Sanitize all API parameters
5. **Rate Limiting** - Implement rate limits on API endpoints
6. **CORS** - Configure CORS appropriately for your domain

Example production setup:

```python
# Add authentication
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == 'your-secure-password'

@app.route('/api/dashboard/stats')
@auth.login_required
def get_dashboard_stats():
    # ... existing code ...
```

---

## Deployment Options

### Option 1: Local Network (Recommended for Development)

```bash
python web_app.py
# Access from same network at http://<your-ip>:5000
```

### Option 2: Docker Container

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "web_app.py"]
```

Build and run:
```bash
docker build -t trading-bot-web .
docker run -p 5000:5000 trading-bot-web
```

### Option 3: Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Option 4: Heroku Deployment

Create `Procfile`:
```
web: gunicorn web_app:app
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku open
```

---

## Advanced Features (Future)

Planned enhancements:

- WebSocket support for real-time push updates
- User authentication and accounts
- Custom dashboards and widgets
- Email alerts for high-confidence signals
- API key management
- Data export (CSV, JSON, PDF)
- Advanced filtering and search
- Backtesting integration
- Trading signal webhooks

---

## File Reference

| File | Purpose | Lines |
|------|---------|-------|
| web_app.py | Flask application and API endpoints | 400+ |
| templates/index.html | Main dashboard | 200+ |
| templates/llm_monitor.html | LLM monitoring page | 150+ |
| templates/stocks.html | Stock analysis page | 150+ |
| templates/patterns.html | Pattern detection page | 120+ |
| static/css/style.css | All styling | 600+ |
| static/js/common.js | Shared utilities | 150+ |
| static/js/dashboard.js | Dashboard logic | 150+ |
| static/js/llm_monitor.js | LLM monitor logic | 120+ |
| static/js/stocks.js | Stock page logic | 120+ |
| static/js/patterns.js | Pattern page logic | 80+ |

**Total:** ~2,200 lines of web application code

---

## Support & Help

**Dashboard Not Loading?**
1. Check browser console (F12)
2. Verify MongoDB is running
3. Check web_app.py error logs

**Data Not Updating?**
1. Run bot first: `python main.py --mode analyze`
2. Wait 30 seconds for first update
3. Click refresh button on page

**Need Custom Features?**
- Edit `web_app.py` to add new endpoints
- Edit templates to add new pages
- Use `common.js` utilities for API calls

---

## Quick Start

```bash
# 1. Install dependencies
pip install Flask==2.3.3 flask-cors==4.0.0

# 2. Start MongoDB
mongosh  # in another terminal

# 3. Start the bot (optional, for data collection)
python main.py --mode analyze  # in another terminal

# 4. Start the web app
python web_app.py

# 5. Open browser
# http://localhost:5000
```

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-11-06
**Framework:** Flask 2.3.3
**License:** MIT

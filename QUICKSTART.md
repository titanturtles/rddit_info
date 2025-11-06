# Quick Start Guide

Get the Reddit Trading Bot up and running in 5 minutes!

## Step 1: Get Your API Keys (5 minutes)

### Reddit API Credentials
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: `RedditTradingBot`
   - **App Type**: Select `script`
   - **Description**: Optional
4. Copy:
   - **Client ID** (under app name)
   - **Client Secret** (the secret field)

### Deepseek API Key
1. Go to https://deepseek.ai/
2. Sign up for free account
3. Go to API section
4. Generate new API key
5. Copy the **API Key**

## Step 2: Install (3 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Verify MongoDB is running
# For Docker users:
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Step 3: Configure (2 minutes)

Edit `config.json`:

```json
{
  "reddit": {
    "client_id": "PASTE_YOUR_CLIENT_ID_HERE",
    "client_secret": "PASTE_YOUR_CLIENT_SECRET_HERE",
    "user_agent": "RedditStockBot/1.0"
  },
  "llm": {
    "api_key": "PASTE_YOUR_DEEPSEEK_API_KEY_HERE"
  },
  "mongodb": {
    "host": "mongodb://localhost:27017"
  }
}
```

## Step 4: Run! (5 minutes)

### First Test - Fetch Data
```bash
python main.py --mode fetch --subreddits wallstreetbets
```

Expected output:
```
2025-11-05 10:15:23 - __main__ - INFO - Fetching posts from r/wallstreetbets (limit: 100)
2025-11-05 10:15:45 - __main__ - INFO - Successfully fetched 87 posts from r/wallstreetbets
2025-11-05 10:15:45 - __main__ - INFO - Saved 87/87 posts to database
```

### Second Test - Analyze Sentiment
```bash
python main.py --mode analyze
```

Expected output:
```
2025-11-05 10:16:22 - __main__ - INFO - Starting Reddit content analysis...
2025-11-05 10:16:23 - __main__ - INFO - Found 87 unanalyzed posts
2025-11-05 10:17:45 - __main__ - INFO - Analysis complete. Stats: {'posts_analyzed': 45, 'comments_analyzed': 0, 'sentiments_created': 85}
```

### Full Pipeline
```bash
python main.py --mode full
```

This will:
1. ✅ Fetch posts from Reddit
2. ✅ Extract stock symbols
3. ✅ Analyze sentiment
4. ✅ Fetch stock prices
5. ✅ Identify patterns
6. ✅ Generate trading signals

## Step 5: View Results

### Check Logs
```bash
tail -f logs/trading_bot.log
```

### View Data with MongoDB

```bash
# Connect to MongoDB
mongosh  # or mongo (older versions)

# Use the database
use reddit_trading

# View recent posts
db.reddit_posts.find().limit(5).pretty()

# View sentiment data
db.sentiment_analysis.find().limit(5).pretty()

# View trading patterns
db.trading_patterns.find().limit(5).pretty()
```

### Generate Report
```python
from utils import DataAnalyzer, print_top_stocks, print_sentiment_summary

# Print top mentioned stocks
print_top_stocks(limit=10, days=30)

# Print sentiment for specific stock
print_sentiment_summary('TSLA', days=30)

# Generate comprehensive report
analyzer = DataAnalyzer()
report = analyzer.generate_report(days=30)
analyzer.export_report_json(report, 'trading_report.json')
analyzer.export_report_csv(report, 'trading_report.csv')
analyzer.close()
```

## Common Commands

```bash
# Fetch from multiple subreddits
python main.py --mode fetch --subreddits wallstreetbets stocks investing options

# Analyze patterns for specific stocks
python main.py --mode patterns --stocks AAPL MSFT TSLA AMZN

# Generate trading signals
python main.py --mode signals --stocks GME AMC PLTR

# Full pipeline with custom subreddits
python main.py --mode full --subreddits wallstreetbets stocks
```

## Troubleshooting

### "Invalid Reddit credentials"
- ❌ Check your Reddit API keys are correct
- ✅ Verify client_id and client_secret in config.json
- ✅ Ensure you created the app at https://reddit.com/prefs/apps

### "MongoDB connection failed"
- ❌ Is MongoDB running? Check with: `docker ps` or `sudo systemctl status mongodb`
- ✅ Start Docker: `docker run -d -p 27017:27017 mongo`
- ✅ Update connection string in config.json if using MongoDB Atlas

### "LLM API error 401"
- ❌ Check your Deepseek API key
- ✅ Verify api_key in config.json
- ✅ Ensure your account has API access enabled

### "No stock symbols found"
- ✅ This is normal for some posts
- ✅ Try with r/wallstreetbets as it has more stock mentions
- ✅ Add more symbols to LLMProcessor if needed

## Next Steps

1. **Run Full Pipeline**: `python main.py --mode full`
2. **Monitor Progress**: `tail -f logs/trading_bot.log`
3. **Check MongoDB**: View data with MongoDB client
4. **Generate Reports**: Use utils.py to create reports
5. **Customize Config**: Adjust parameters in config.json as needed

## Performance Tips

- First run takes longer (fetching data)
- Subsequent runs are faster (only new data)
- Use MongoDB Atlas for better performance
- Increase `sleep_between_requests` if hitting rate limits
- Process less data: reduce `limit_per_request`

## What Happens Next?

After running the bot:

1. **Reddit Data**: Posts and comments stored in MongoDB
2. **Stock Symbols**: Extracted from text using pattern matching + LLM
3. **Sentiment**: Analyzed as BULLISH, NEUTRAL, BEARISH with scores
4. **Price Data**: Historical prices fetched for each mentioned stock
5. **Patterns**: Correlations found between sentiment and price
6. **Signals**: Buy/sell recommendations generated

All results are saved in MongoDB for further analysis!

---

**That's it! You now have a fully functional Reddit trading sentiment analysis bot. 🚀**

For detailed documentation, see `README.md`.

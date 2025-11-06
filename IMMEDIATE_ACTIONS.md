# Immediate Actions - Get Started Now

## What Was Fixed For You

✓ **PRAW Exception Error** - reddit_fetcher.py (FIXED)
✓ **MongoDB Collection Error** - database.py (FIXED)
✓ **Yfinance Retry Logic** - stock_data_fetcher.py (IMPROVED)

---

## Step 1: Test Your Setup (5 minutes)

```bash
# Run comprehensive test
python test_setup.py
```

**Expected output:**
```
✓ PASS: Configuration
✓ PASS: MongoDB
✓ PASS: Database Module
✓ PASS: Reddit API
✓ PASS: LLM Processor
✓ PASS: Stock Fetcher

Total: 6/6 tests passed 🎉
```

---

## Step 2: If Tests Fail

### If Configuration fails:
```bash
# Edit config.json with your API keys
nano config.json
```

Required:
- `reddit.client_id` - From https://www.reddit.com/prefs/apps
- `reddit.client_secret` - From https://www.reddit.com/prefs/apps
- `llm.api_key` - From https://deepseek.ai

### If MongoDB fails:
```bash
# Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or Linux
sudo systemctl start mongodb

# Or macOS
brew services start mongodb-community
```

### If Reddit API fails:
```bash
# Test with specific script
python test_reddit_api.py

# Check credentials in config.json
cat config.json | grep -A 3 '"reddit"'
```

### If Stock Data fails:
```bash
# Test with specific script
python test_yfinance.py

# This is usually temporary (rate limiting)
# Wait 5-10 minutes and try again
sleep 300 && python test_yfinance.py
```

### If LLM Processor fails:
```bash
# Check Deepseek API key in config.json
cat config.json | grep -A 3 '"llm"'

# Verify key is correct
# Visit https://deepseek.ai and check API settings
```

---

## Step 3: Run the Bot

Once `test_setup.py` shows all 6 tests passing:

```bash
# Run full pipeline
python main.py --mode full
```

**This will:**
1. Fetch Reddit posts from r/wallstreetbets, r/stocks, r/investing
2. Extract stock symbols
3. Analyze sentiment (BULLISH/BEARISH/NEUTRAL)
4. Fetch historical stock prices
5. Correlate sentiment with price movements
6. Identify trading patterns
7. Generate trading signals
8. Save everything to MongoDB

**Time:** 5-15 minutes depending on data volume

---

## Step 4: Monitor Progress

In another terminal, watch the logs:

```bash
tail -f logs/trading_bot.log
```

**Look for:**
- `INFO - Fetching posts from r/wallstreetbets`
- `INFO - Successfully fetched X posts`
- `INFO - Analysis complete`
- `INFO - Fetching AAPL data`
- `INFO - Retrieved X records`
- `INFO - Patterns found`

---

## Step 5: Check Results

```bash
# Connect to MongoDB
mongosh

# Use the database
use reddit_trading

# Count posts
db.reddit_posts.count()

# Count sentiments
db.sentiment_analysis.count()

# Count patterns
db.trading_patterns.count()

# View sample post
db.reddit_posts.findOne()

# View sample sentiment
db.sentiment_analysis.findOne()

# Exit
exit
```

---

## Alternative: Test Individual Components

If you only want to test specific parts:

```bash
# Test Reddit API only
python test_reddit_api.py

# Test MongoDB only
python test_mongodb.py

# Test Stock Data only
python test_yfinance.py

# Test specific commands
python main.py --mode fetch --subreddits wallstreetbets
python main.py --mode analyze
python main.py --mode patterns --stocks AAPL MSFT TSLA
```

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| "YOUR_REDDIT_CLIENT_ID" in error | Edit config.json, add real API keys |
| "MongoDB connection failed" | Run `docker run -d -p 27017:27017 mongo:latest` |
| "Expecting value: line 1" (yfinance) | Wait 5-10 minutes, try again |
| "ImportError: PrawException" | ✓ Already fixed in reddit_fetcher.py |
| "Collection objects do not implement truth" | ✓ Already fixed in database.py |
| "LLM API error 401" | Check Deepseek API key in config.json |

---

## Files You Need to Know About

**Core:**
- `main.py` - Run this to execute the bot
- `config.json` - Edit this with your API keys

**Testing:**
- `test_setup.py` - Run this first
- `test_reddit_api.py` - Test Reddit only
- `test_mongodb.py` - Test MongoDB only
- `test_yfinance.py` - Test stock data only

**Documentation:**
- `SOLUTIONS_QUICK_REFERENCE.md` - Quick fixes
- `YFINANCE_TROUBLESHOOTING.md` - Yfinance help
- `FIXES_SUMMARY.txt` - What was fixed

**Already Fixed:**
- `database.py` - Collection boolean check
- `reddit_fetcher.py` - PRAW exception class
- `stock_data_fetcher.py` - Automatic retries

---

## Success Checklist

- [ ] `python test_setup.py` shows 6/6 tests passing
- [ ] MongoDB is running
- [ ] config.json has real API credentials
- [ ] Can fetch Reddit posts: `python main.py --mode fetch`
- [ ] Can analyze sentiment: `python main.py --mode analyze`
- [ ] Can analyze patterns: `python main.py --mode patterns`
- [ ] MongoDB has data: `mongosh` → `db.reddit_posts.count()`
- [ ] Logs look good: `tail -f logs/trading_bot.log`

---

## What's Next After Running

1. **Monitor the logs** while bot is running
2. **Check MongoDB** for data collection
3. **View reports** - Generate JSON/CSV
4. **Analyze patterns** - See what works
5. **Schedule runs** - Set up daily execution (optional)

---

## Quick Command Reference

```bash
# Test everything
python test_setup.py

# Test Reddit
python test_reddit_api.py

# Test MongoDB
python test_mongodb.py

# Test Stock Data
python test_yfinance.py

# Run bot (full pipeline)
python main.py --mode full

# Run bot (fetch only)
python main.py --mode fetch --subreddits wallstreetbets

# Run bot (analyze only)
python main.py --mode analyze

# Run bot (patterns only)
python main.py --mode patterns --stocks AAPL MSFT TSLA

# View logs
tail -f logs/trading_bot.log

# Connect to MongoDB
mongosh
```

---

## 🚀 TL;DR (Too Long; Didn't Read)

```bash
1. python test_setup.py           # Test everything
2. # Fix any failures using guides above
3. python main.py --mode full     # Run the bot
4. tail -f logs/trading_bot.log   # Watch progress
5. mongosh → db.reddit_posts.count()  # Check results
```

---

## Getting Help

- **Quick fixes:** `SOLUTIONS_QUICK_REFERENCE.md`
- **Yfinance issues:** `YFINANCE_TROUBLESHOOTING.md`
- **Setup help:** `SETUP_CHECKLIST.md`
- **Complete guide:** `README.md`
- **What's fixed:** `FIXES_SUMMARY.txt`

---

**You're ready to go! Start with `python test_setup.py` 🎯**

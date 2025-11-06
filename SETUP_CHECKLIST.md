# Setup Checklist

Complete checklist to ensure everything is properly configured before running the bot.

## Prerequisites (Before Starting)

- [ ] Python 3.8+ installed
- [ ] MongoDB 4.0+ available (local or cloud)
- [ ] Internet connection for API calls
- [ ] API credentials ready (see below)

## Step 1: Get API Credentials (15 minutes)

### Reddit API

- [ ] Go to https://www.reddit.com/prefs/apps
- [ ] Click "Create App" or "Create Another App"
- [ ] Fill form:
  - [ ] Name: `RedditStockBot`
  - [ ] App type: Select "script"
  - [ ] Description: Optional
- [ ] Copy and save:
  - [ ] **Client ID** (under app name)
  - [ ] **Client Secret**

### Deepseek API

- [ ] Go to https://deepseek.ai/
- [ ] Sign up for free account
- [ ] Go to API/Account section
- [ ] Generate API key
- [ ] Copy and save: **API Key**

### Optional: MongoDB Atlas (Cloud Database)

- [ ] Go to https://www.mongodb.com/cloud/atlas
- [ ] Create free account
- [ ] Create new cluster
- [ ] Create database user with password
- [ ] Get connection string
- [ ] Copy and save: **Connection String**

## Step 2: Install Dependencies (5 minutes)

- [ ] Open terminal in project directory
- [ ] Create virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```
- [ ] Install packages:
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verify installation:
  ```bash
  python -c "import praw, pymongo, yfinance; print('All dependencies installed!')"
  ```

## Step 3: Setup MongoDB (5 minutes)

### Option A: Local MongoDB

- [ ] Install MongoDB:
  - [ ] **Mac**: `brew install mongodb-community`
  - [ ] **Linux**: `sudo apt-get install -y mongodb`
  - [ ] **Windows**: Download from mongodb.com
  - [ ] **Docker**: `docker run -d -p 27017:27017 --name mongodb mongo:latest`

- [ ] Start MongoDB:
  - [ ] **Mac**: `brew services start mongodb-community`
  - [ ] **Linux**: `sudo systemctl start mongodb`
  - [ ] **Docker**: Already started above

- [ ] Verify connection:
  ```bash
  mongosh  # or mongo
  > use test
  > db.test.insertOne({test: 1})
  > db.test.findOne()
  ```

### Option B: MongoDB Atlas (Cloud)

- [ ] Create cluster at https://www.mongodb.com/cloud/atlas
- [ ] Add IP address to whitelist
- [ ] Create database user
- [ ] Get connection string
- [ ] Copy to clipboard

## Step 4: Configure Application (5 minutes)

### Edit config.json

- [ ] Open `config.json` in text editor
- [ ] Fill in Reddit credentials:
  - [ ] Replace `YOUR_REDDIT_CLIENT_ID`
  - [ ] Replace `YOUR_REDDIT_CLIENT_SECRET`
- [ ] Fill in Deepseek API key:
  - [ ] Replace `YOUR_DEEPSEEK_API_KEY`
- [ ] Configure MongoDB:
  - [ ] **Local**: Keep `mongodb://localhost:27017`
  - [ ] **Atlas**: Replace with your connection string
- [ ] Verify subreddits (already set to good defaults):
  - [ ] `wallstreetbets`
  - [ ] `stocks`
  - [ ] `investing`

### Verify Configuration

```bash
python -c "from config_loader import get_config; c = get_config(); print('Config loaded:', c.get('reddit.subreddits'))"
```

## Step 5: Test Components (10 minutes)

Run the test suite to verify everything works:

```bash
python test_example.py
```

Expected output:
```
✓ PASS: Configuration
✓ PASS: Database Connection
✓ PASS: LLM Stock Extraction
✓ PASS: Sentiment Analysis
✓ PASS: Stock Data Fetching
✓ PASS: Database Queries
✓ PASS: Data Analysis

Total: 7/7 tests passed
🎉 All tests passed! Bot is ready to use.
```

## Troubleshooting Tests

### Configuration Test Fails
- [ ] Check config.json is in correct directory
- [ ] Verify JSON syntax (use https://jsonlint.com/)
- [ ] Ensure all required fields present

### Database Connection Fails
- [ ] Verify MongoDB is running:
  - [ ] Local: `sudo systemctl status mongodb`
  - [ ] Docker: `docker ps | grep mongodb`
  - [ ] Atlas: Check cluster status at mongodb.com
- [ ] Check connection string in config.json
- [ ] For Atlas: Verify IP is whitelisted

### LLM Tests Fail
- [ ] Verify Deepseek API key is correct
- [ ] Check account has API access enabled
- [ ] Verify api_key field in config.json
- [ ] Check internet connection

### Stock Data Test Fails
- [ ] Verify internet connection
- [ ] Check if yfinance is working:
  ```bash
  python -c "import yfinance as yf; print(yf.Ticker('AAPL').info['currentPrice'])"
  ```

## Step 6: First Run (5-10 minutes)

### Fetch Reddit Data

```bash
python main.py --mode fetch --subreddits wallstreetbets
```

- [ ] Command executes without errors
- [ ] See output: "Successfully fetched X posts"
- [ ] Check logs: `tail -f logs/trading_bot.log`

### Check MongoDB

```bash
mongosh
> use reddit_trading
> db.reddit_posts.count()  # Should see number > 0
> db.reddit_posts.findOne()  # View sample post
```

- [ ] Post count > 0
- [ ] Can view sample data

### Analyze Content

```bash
python main.py --mode analyze
```

- [ ] Command executes
- [ ] See sentiment creation messages
- [ ] Check: `db.sentiment_analysis.count()`

### Fetch Stock Prices

```bash
python main.py --mode fetch --stocks AAPL MSFT TSLA
```

- [ ] Command executes
- [ ] See price fetch messages
- [ ] Check: `db.stock_prices.count()`

### Analyze Patterns

```bash
python main.py --mode patterns --stocks AAPL MSFT
```

- [ ] Command executes
- [ ] See pattern analysis messages
- [ ] Check: `db.trading_patterns.count()`

## Step 7: Run Full Pipeline (5-15 minutes)

```bash
python main.py --mode full --subreddits wallstreetbets
```

- [ ] Fetches Reddit data
- [ ] Analyzes sentiment
- [ ] Fetches stock prices
- [ ] Analyzes patterns
- [ ] Completes without errors

## Step 8: Generate Reports (2 minutes)

Create and view analysis reports:

```python
from utils import DataAnalyzer, print_top_stocks, print_sentiment_summary

# Print to console
print_top_stocks(limit=10, days=30)
print_sentiment_summary('AAPL', days=30)

# Generate files
analyzer = DataAnalyzer()
report = analyzer.generate_report(days=30)
analyzer.export_report_json(report, 'report.json')
analyzer.export_report_csv(report, 'report.csv')
analyzer.close()
```

- [ ] JSON report created
- [ ] CSV report created
- [ ] Console output displays correctly

## Post-Setup Configuration (Optional)

### Customize Parameters

Edit `config.json` to customize:

- [ ] **reddit.limit_per_request**: Number of posts per fetch (default: 100)
- [ ] **reddit.subreddits**: Which communities to monitor
- [ ] **data_collection.start_date**: Historical data start date
- [ ] **pattern_analysis.min_mentions**: Minimum mentions for pattern
- [ ] **pattern_analysis.correlation_threshold**: Correlation sensitivity

### Add More Stock Symbols

Edit `llm_processor.py`:

- [ ] Find `COMMON_SYMBOLS` set
- [ ] Add your symbols: `'YOUR_SYMBOL'`
- [ ] Save and restart bot

### Setup Scheduled Execution

Create cron job (Linux/Mac):

```bash
crontab -e
# Add line to run daily at 9 AM:
0 9 * * * cd /path/to/rddt_info && /path/to/venv/bin/python main.py --mode full
```

Or Windows Task Scheduler:

- [ ] Open Task Scheduler
- [ ] Create Basic Task
- [ ] Set trigger: Daily at 9 AM
- [ ] Set action: Run `python main.py --mode full`

## Security Setup

- [ ] Do NOT commit `config.json` to git
- [ ] Verify `.gitignore` includes `config.json`
- [ ] Create backup of API keys in secure location
- [ ] Rotate API keys periodically
- [ ] Use MongoDB Atlas IP whitelist
- [ ] For production: Use environment variables instead of config.json

## Performance Optimization

- [ ] For large datasets: Use MongoDB Atlas (faster)
- [ ] Increase `sleep_between_requests` if hitting rate limits
- [ ] Decrease `limit_per_request` to reduce API calls
- [ ] Run pattern analysis separately from data collection
- [ ] Use MongoDB indexes (auto-created)

## Monitoring Setup

- [ ] Create alerts on MongoDB for disk space
- [ ] Monitor API usage (Reddit, Deepseek)
- [ ] Watch `logs/trading_bot.log` for errors
- [ ] Set up log rotation (configured in logger_setup.py)

## Final Verification

- [ ] All tests pass: `python test_example.py`
- [ ] config.json has all API keys filled in
- [ ] MongoDB is accessible
- [ ] First fetch works: `python main.py --mode fetch`
- [ ] Data appears in MongoDB
- [ ] Full pipeline completes: `python main.py --mode full`
- [ ] Reports can be generated
- [ ] Logs are being written to `logs/trading_bot.log`

## Quick Command Reference

```bash
# Test all components
python test_example.py

# Run full pipeline
python main.py --mode full

# Just fetch data
python main.py --mode fetch --subreddits wallstreetbets

# Analyze existing data
python main.py --mode analyze

# Pattern analysis
python main.py --mode patterns --stocks AAPL MSFT TSLA

# View logs
tail -f logs/trading_bot.log

# Connect to MongoDB
mongosh
use reddit_trading
db.reddit_posts.count()
```

## Support Resources

- **Documentation**: README.md (comprehensive guide)
- **Quick Start**: QUICKSTART.md (5-minute setup)
- **Project Structure**: PROJECT_STRUCTURE.md (architecture)
- **Examples**: test_example.py (component testing)
- **Utilities**: utils.py (analysis and reporting)

## Next Steps After Setup

1. ✅ Run full pipeline to collect baseline data
2. ✅ Generate initial reports
3. ✅ Review patterns and signals
4. ✅ Customize parameters for your needs
5. ✅ Setup scheduled execution (optional)
6. ✅ Monitor logs and performance
7. ✅ Iterate and improve

---

**Congratulations! You're all set up! 🚀**

For questions or issues, check README.md or review logs/trading_bot.log for detailed error messages.

Good luck with your sentiment-driven trading analysis!

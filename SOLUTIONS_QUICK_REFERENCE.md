# Quick Solutions Reference

## Most Common Errors & Fixes

### 1. Yfinance Error: "Expecting value: line 1 column 1"

**What it means:** Yahoo Finance returned empty data

**Quick fixes (in order):**
```bash
# 1. Wait 5-10 minutes, then try again
sleep 300 && python test_yfinance.py

# 2. Check internet
ping yahoo.com

# 3. Restart Python
exit()
python test_yfinance.py

# 4. Upgrade yfinance
pip install --upgrade yfinance

# 5. Test diagnostic
python test_yfinance.py
```

**If still failing:**
- See: `YFINANCE_TROUBLESHOOTING.md`
- This is usually temporary (rate limiting)

---

### 2. MongoDB Error: "Collection objects do not implement truth value testing"

**What it means:** Database collection check failed

**Fix (already applied):**
- Changed `if collection:` to `if collection is not None:`
- File: `database.py` ✓ Fixed

**Verify MongoDB is running:**
```bash
# Docker
docker ps | grep mongodb
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Linux
sudo systemctl start mongodb

# macOS
brew services start mongodb-community
```

**Test:**
```bash
python test_mongodb.py
```

---

### 3. Reddit API Error: "ImportError: cannot import name 'PrawException'"

**What it means:** Wrong exception class name in PRAW

**Fix (already applied):**
- Changed `PrawException` to `PRAWException`
- File: `reddit_fetcher.py` ✓ Fixed

**Test:**
```bash
python test_reddit_api.py
```

---

### 4. Config Error: "YOUR_REDDIT_CLIENT_ID" or "YOUR_DEEPSEEK_API_KEY"

**What it means:** API credentials not filled in config.json

**Fix:**
```bash
# Edit config.json
nano config.json  # or use your editor

# Add your actual credentials:
# - Reddit: client_id and client_secret from https://reddit.com/prefs/apps
# - Deepseek: api_key from https://deepseek.ai
# - MongoDB: connection string (optional, default is localhost)
```

---

## Diagnostic Scripts

Run these to diagnose issues:

```bash
# Test configuration
python test_setup.py          # Tests all 6 components

# Test individual components
python test_reddit_api.py     # Reddit API only
python test_mongodb.py        # MongoDB only
python test_yfinance.py       # Stock data only

# Get detailed output
python test_setup.py 2>&1 | tee test_output.log
```

---

## Environment Setup

### First Time Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Edit config.json with API keys
nano config.json

# 4. Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# 5. Test everything
python test_setup.py

# 6. Run bot
python main.py --mode full
```

### Troubleshooting Setup

```bash
# Check Python version (need 3.8+)
python --version

# Check installed packages
pip list | grep -E "praw|pymongo|yfinance"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check MongoDB status
docker ps | grep mongodb
# or
sudo systemctl status mongodb

# Check logs
tail -f logs/trading_bot.log
```

---

## Common Commands

```bash
# Run full pipeline
python main.py --mode full

# Fetch Reddit data only
python main.py --mode fetch --subreddits wallstreetbets

# Analyze existing data
python main.py --mode analyze

# Analyze patterns
python main.py --mode patterns --stocks AAPL MSFT TSLA

# View logs
tail -f logs/trading_bot.log

# MongoDB query
mongosh
use reddit_trading
db.reddit_posts.count()
db.sentiment_analysis.count()
```

---

## Network Troubleshooting

```bash
# Check internet
ping 8.8.8.8

# Check Yahoo Finance
ping query1.finance.yahoo.com
curl -I https://query1.finance.yahoo.com

# Check Reddit
ping reddit.com

# Check Deepseek
curl -I https://api.deepseek.ai

# DNS test
nslookup reddit.com
```

---

## Performance Tips

1. **Rate Limiting:**
   - Add `sleep_between_requests: 3` in config.json
   - Don't fetch 1000s of symbols at once

2. **MongoDB:**
   - Use Atlas (cloud) for better performance
   - Indexes are auto-created
   - Queries are logged

3. **yfinance:**
   - Increase delays between requests
   - Cache results
   - Avoid fetching same symbol twice

4. **LLM Queries:**
   - Batch process posts/comments
   - Use shorter texts when possible

---

## File Structure Quick Reference

```
rddt_info/
├── config.json                    ← Edit API keys here
├── main.py                        ← Run this
├── test_setup.py                  ← Comprehensive test
├── test_reddit_api.py            ← Test Reddit
├── test_mongodb.py               ← Test MongoDB
├── test_yfinance.py              ← Test Stock data
│
├── Core Modules
├── database.py                    ← MongoDB [FIXED: line 67+]
├── reddit_fetcher.py              ← Reddit API [FIXED: PRAWException]
├── llm_processor.py              ← LLM analysis
├── stock_data_fetcher.py         ← Stock data [IMPROVED: Retries]
├── pattern_analyzer.py           ← Pattern detection
│
├── Documentation
├── YFINANCE_TROUBLESHOOTING.md   ← Yfinance solutions
├── SOLUTIONS_QUICK_REFERENCE.md  ← This file
├── README.md                     ← Full documentation
├── QUICKSTART.md                 ← 5-minute setup
└── ...
```

---

## Status Check Checklist

- [ ] Python 3.8+ installed: `python --version`
- [ ] praw installed: `pip list | grep praw`
- [ ] pymongo installed: `pip list | grep pymongo`
- [ ] yfinance installed: `pip list | grep yfinance`
- [ ] config.json filled with API keys
- [ ] MongoDB running: `docker ps | grep mongodb`
- [ ] `python test_setup.py` passes all 6 tests
- [ ] Can fetch Reddit data: `python main.py --mode fetch`
- [ ] Can analyze data: `python main.py --mode analyze`
- [ ] Can get stock prices: `python test_yfinance.py` passes
- [ ] Can generate reports: Works without errors

---

## Getting More Help

**For specific errors:**
1. Read the error message carefully
2. Check relevant troubleshooting file:
   - Yfinance: `YFINANCE_TROUBLESHOOTING.md`
   - MongoDB: `README.md` → Troubleshooting
   - Reddit: `QUICKSTART.md`
   - Setup: `SETUP_CHECKLIST.md`

3. Run relevant test:
   - `python test_yfinance.py`
   - `python test_mongodb.py`
   - `python test_reddit_api.py`
   - `python test_setup.py`

4. Check logs:
   - `tail -f logs/trading_bot.log`
   - Look for ERROR and WARNING lines

5. Check internet:
   - Ensure you're online
   - Try pinging external sites
   - Check firewall settings

---

## Recent Fixes

✓ **database.py (line 67+)**
- Changed `if collection:` → `if collection is not None:`
- Prevents "truth value testing" error

✓ **reddit_fetcher.py (line 11, 50, 106, 163)**
- Changed `PrawException` → `PRAWException`
- Correct PRAW exception class name

✓ **stock_data_fetcher.py (line 27-80)**
- Added automatic retries (3 attempts)
- Exponential backoff (1, 2, 4 seconds)
- Better error handling

---

## Next Steps

1. **Run diagnostic test:**
   ```bash
   python test_setup.py
   ```

2. **Fix any issues** using this guide

3. **Run full pipeline:**
   ```bash
   python main.py --mode full
   ```

4. **Monitor progress:**
   ```bash
   tail -f logs/trading_bot.log
   ```

5. **Check results:**
   ```bash
   mongosh
   use reddit_trading
   db.reddit_posts.count()
   ```

---

**Still having issues?**
- Check YFINANCE_TROUBLESHOOTING.md for detailed solutions
- Review README.md for complete documentation
- Check logs/trading_bot.log for exact errors
- Run test_setup.py to identify which component fails

# Yfinance Troubleshooting Guide

## Error: "Expecting value: line 1 column 1 (char 0)"

This error means yfinance is getting an empty or invalid response from Yahoo Finance.

### Quick Solutions (Try These First)

**1. Wait and Retry (Most Common)**
- yfinance sometimes rate-limits requests
- Solution: Wait 5-10 minutes and try again
- The bot now includes automatic retries with exponential backoff

**2. Restart Python Environment**
```bash
# Exit Python and restart
exit()

# Or create a new terminal session
python test_yfinance.py
```

**3. Check Internet Connection**
```bash
ping yahoo.com
ping 8.8.8.8  # Google DNS
```

**4. Upgrade yfinance**
```bash
pip install --upgrade yfinance
```

### Detailed Solutions

#### Solution 1: Network/Firewall Issues

**Problem:** Your network blocks Yahoo Finance

**Test:**
```bash
curl -I https://query1.finance.yahoo.com
# Should return HTTP 200
```

**Solutions:**
- Check corporate firewall/proxy settings
- Try from a different network
- Use a VPN to bypass firewall
- Contact your IT department

#### Solution 2: Rate Limiting

**Problem:** Too many requests to Yahoo Finance in short time

**Symptoms:**
- Empty responses
- HTTP 429 errors
- Random timeouts

**Solutions:**
```python
# Bot automatically retries with delays
# Default: 3 retries with exponential backoff
# 1st try: immediate
# 2nd try: wait 1 second
# 3rd try: wait 2 seconds
```

Manual fix - Add delays between requests:
```python
import time
from stock_data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()

symbols = ['AAPL', 'MSFT', 'TSLA']
for symbol in symbols:
    df = fetcher.fetch_stock_data(symbol)
    time.sleep(5)  # Wait 5 seconds between requests
```

#### Solution 3: Yahoo Finance API Changes

**Problem:** yfinance library outdated or API changed

**Solutions:**
```bash
# Force reinstall
pip uninstall yfinance
pip install yfinance

# Or with specific version
pip install yfinance==0.2.32
```

#### Solution 4: Data/Cache Issues

**Problem:** Corrupted cache or stale data

**Solutions:**
```bash
# Clear pip cache
pip cache purge

# Reinstall clean
pip install --force-reinstall yfinance
pip install --force-reinstall pandas numpy

# Or create fresh virtual environment
python -m venv venv_fresh
source venv_fresh/bin/activate  # or venv_fresh\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Solution 5: Use Alternative Data Source

If yfinance continues to fail, use alternatives:

**Option A: Alpha Vantage** (Free tier available)
```python
# Install: pip install alpha_vantage
from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
data, meta = ts.get_daily(symbol='AAPL', outputsize='full')
```

**Option B: IEX Cloud** (Free tier available)
```python
# Install: pip install iexfinance
from iexfinance.stocks import Stock

s = Stock('AAPL', token='YOUR_TOKEN')
df = s.get_historical_data(start='20250101', end='20251105')
```

**Option C: Finnhub** (Free tier available)
```python
# Install: pip install finnhub-python
import finnhub

finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
candles = finnhub_client.stock_candles('AAPL', 'D', 1609459200, 1735689600)
```

### Testing Tools

Run these diagnostic scripts:

```bash
# Test basic yfinance
python test_yfinance.py

# This will:
# 1. Check internet connection
# 2. Test yfinance import
# 3. Fetch sample data (AAPL)
# 4. Test multiple symbols
# 5. Test StockDataFetcher module
# 6. Show alternative sources
```

### Common Scenarios & Solutions

#### Scenario 1: First Time Setup
**Problem:** Never worked, getting errors immediately

**Solution:**
```bash
1. Check internet: ping yahoo.com
2. Upgrade yfinance: pip install --upgrade yfinance
3. Test: python test_yfinance.py
4. If still fails: Restart Python/terminal
5. Try again after 5 minutes
```

#### Scenario 2: Worked Before, Now Broken
**Problem:** Used to work, suddenly failing

**Solution:**
```bash
1. Wait 5 minutes (rate limiting)
2. Restart Python: exit() then python test_yfinance.py
3. Check firewall: curl -I https://query1.finance.yahoo.com
4. Upgrade yfinance: pip install --upgrade yfinance
5. Check logs: tail -f logs/trading_bot.log
```

#### Scenario 3: Intermittent Failures
**Problem:** Works sometimes, fails randomly

**Solution:**
```bash
1. This is normal for yfinance (public free API)
2. Bot automatically retries with delays
3. Add longer delays in your code:
   - time.sleep(10) between symbol fetches
4. Consider using paid API for reliability
5. Monitor logs for patterns
```

#### Scenario 4: Only Some Symbols Fail
**Problem:** AAPL works, TSLA fails

**Solution:**
1. Some symbols might not exist or have no recent data
2. Check symbol spelling
3. Test with known symbols (AAPL, MSFT, GOOG)
4. Some symbols need different formats (BRK.B instead of BRKB)

### Prevention

**Best Practices:**

1. **Add delays between requests:**
```python
import time
symbols = ['AAPL', 'MSFT', 'TSLA']
for symbol in symbols:
    df = fetcher.fetch_stock_data(symbol)
    time.sleep(3)  # 3 second delay
```

2. **Use exponential backoff (automatic in bot):**
- Automatic in updated `stock_data_fetcher.py`
- Retries 3 times with 1, 2, 4 second delays

3. **Cache results:**
```python
# Don't fetch same symbol multiple times per run
cache = {}
for symbol in symbols:
    if symbol not in cache:
        cache[symbol] = fetcher.fetch_stock_data(symbol)
    df = cache[symbol]
```

4. **Monitor rate limiting:**
```python
import logging
logging.basicConfig(level=logging.INFO)
# Check logs for "Retrying in X seconds"
```

5. **Use reliable symbols:**
- Stick to major US stocks (AAPL, MSFT, GOOG, AMZN, TSLA)
- Avoid delisted or very new symbols
- Test with yfinance directly first

### Getting Help

1. **Check yfinance issues:**
   - GitHub: https://github.com/ranaroussi/yfinance/issues
   - Search error message

2. **Test yfinance directly:**
```python
import yfinance as yf
df = yf.Ticker("AAPL").history(start="2025-01-01", end="2025-11-05")
print(df)
```

3. **Check Yahoo Finance:**
   - Visit: https://finance.yahoo.com
   - See if AAPL data is accessible
   - If not, Yahoo Finance might be down

4. **Check your network:**
```bash
# Detailed network test
curl -v https://query1.finance.yahoo.com
# Should show successful connection
```

### Expected Success

After fixes, you should see:
```
✓ yfinance: Data retrieved: 252 records
✓ Latest close: $227.41
✓ Date range: 2024-11-05 to 2025-11-05
```

### If All Else Fails

1. Use alternative data source (see Solution 5)
2. Use cached historical data (if available)
3. Manually add stock prices to MongoDB
4. Contact yfinance support

---

**Summary:**
- Most errors are temporary (wait 5-10 min)
- Bot auto-retries with exponential backoff
- Check internet connection first
- Upgrade yfinance if old
- Use alternative APIs if yfinance consistently fails
- Monitor logs for detailed error info

Run `python test_yfinance.py` to diagnose your specific issue!

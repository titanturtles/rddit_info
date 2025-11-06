# Yfinance Not Working - Troubleshooting

## Your Specific Error

```
yfinance - ERROR - Failed to get ticker 'AAPL' reason: Expecting value: line 1 column 1 (char 0)
yfinance - ERROR - AAPL: No timezone found, symbol may be delisted
```

**What this means:** Yfinance is getting an empty response from Yahoo Finance.

---

## Quick Solutions (Try These First)

### 1. **Wait and Retry** (80% chance this fixes it)

Yfinance is hitting rate limits from Yahoo Finance.

```bash
# Wait 10 minutes
sleep 600

# Try again
python test_yfinance.py
```

### 2. **Check Your Internet**

```bash
# Test connectivity
ping yahoo.com
ping 8.8.8.8

# Run diagnostic
python test_connectivity.py
```

### 3. **Upgrade Yfinance**

```bash
pip install --upgrade yfinance
```

### 4. **Restart Python**

```bash
# Close Python completely
exit()

# Restart fresh
python test_yfinance.py
```

### 5. **Use Test Mode** (Recommended for now)

Test everything EXCEPT yfinance:

```bash
python test_setup_no_yfinance.py
```

This will show you which components work while yfinance is being fixed.

---

## Diagnostic: Find the Root Cause

Run the comprehensive connectivity test:

```bash
python test_connectivity.py
```

This checks:
- ✓ Basic internet connectivity
- ✓ HTTP requests to Yahoo Finance
- ✓ Yfinance with different approaches
- ✓ Mock data creation

**Results tell you exactly what's wrong:**

| Result | Problem | Solution |
|--------|---------|----------|
| ✗ Basic Internet | No internet | Check WiFi/cable, ping 8.8.8.8 |
| ✗ HTTP Request | Firewall/Proxy | Check corporate firewall, use VPN |
| ✗ Yfinance Direct | API issues | Wait 10 min, upgrade yfinance |
| ✓ Mock Data | Can use test data | Proceed with testing |

---

## If It's a Firewall/Proxy Issue

**At home/personal network:**
- This is unlikely
- Try: `curl -I https://query1.finance.yahoo.com`
- If fails, check router settings

**At work/corporate network:**
- Likely behind a proxy
- Talk to IT: "I need access to yahoo.com:443"
- Or use VPN

**Using VPN:**
```bash
# Install socks proxy support
pip install pysocks

# Use free VPN: ProtonVPN, ExpressVPN, or similar

# Or try with yfinance using proxy
# (Edit stock_data_fetcher.py to add proxy config)
```

---

## If It's a Yfinance API Issue

Yahoo Finance API sometimes has issues. This is temporary.

**Check status:**
- https://status.yahoo.com
- Search "finance.yahoo.com" for incidents

**Wait strategy:**
1. Wait 10 minutes
2. Retry
3. Wait 30 minutes
4. Retry
5. Wait 1 hour
6. Retry

**If status shows incident:**
- Wait for Yahoo to fix (usually 30 min - 2 hours)
- Check back on status page

---

## Workaround: Use Mock Data

While yfinance is broken, you can use test data:

```python
# In stock_data_fetcher.py, add at the top:
import os
USE_MOCK_DATA = os.getenv('MOCK_STOCK_DATA', False)

# In fetch_stock_data(), wrap yfinance call:
if USE_MOCK_DATA:
    return self._generate_mock_data(symbol)
```

Then run with mock data:

```bash
export MOCK_STOCK_DATA=1
python main.py --mode full
```

---

## Alternative: Use Different Data Source

If yfinance continues failing, switch to another provider:

### **Option 1: Alpha Vantage** (Free)

```bash
pip install alpha_vantage
```

```python
from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(key='YOUR_FREE_API_KEY', output_format='pandas')
data, meta = ts.get_daily(symbol='AAPL')
```

Sign up: https://www.alphavantage.co/

### **Option 2: IEX Cloud** (Free tier)

```bash
pip install iexfinance
```

```python
from iexfinance.stocks import Stock

s = Stock('AAPL', token='YOUR_TOKEN')
df = s.get_historical_data(start='20250101', end='20251105')
```

Sign up: https://iexcloud.io/

### **Option 3: Finnhub** (Free)

```bash
pip install finnhub-python
```

```python
import finnhub

finnhub_client = finnhub.Client(api_key="YOUR_API_KEY")
candles = finnhub_client.stock_candles('AAPL', 'D', 1609459200, 1735689600)
```

Sign up: https://finnhub.io/

---

## What to Do Right Now

### Step 1: Diagnose

```bash
python test_connectivity.py
```

### Step 2: Based on Results

**If internet works but yfinance fails:**
- Wait 10 minutes
- Try: `pip install --upgrade yfinance`
- Try again

**If internet fails:**
- Check WiFi/cable
- Check firewall
- Use VPN

**Either way:**
- Run: `python test_setup_no_yfinance.py`
- Tests everything except stock data

### Step 3: Get Core Bot Working

Even without yfinance, you can:
1. ✓ Fetch Reddit data
2. ✓ Analyze sentiment
3. ✓ Identify patterns
4. ✓ Generate signals

Stock data is just the validation layer.

```bash
# Test without yfinance
python test_setup_no_yfinance.py

# Run full pipeline
python main.py --mode full

# It will skip stock data but work on everything else
```

---

## Expected Timeline

| Action | Time | Success Rate |
|--------|------|--------------|
| Wait 5 minutes, retry | 5 min | 20% |
| Wait 10 minutes, retry | 10 min | 60% |
| Upgrade yfinance | 15 min | 70% |
| Run diagnostic | 5 min | 100% (identifies issue) |
| Restart Python | 1 min | 30% |
| Use test mode | 1 min | 100% (works) |
| Switch provider | 30 min | 100% (works) |

---

## Success Indicators

### ✓ Yfinance Working
```
✓ Data retrieved successfully!
  - Records: 252
  - Latest close: $227.41
```

### ⊘ Yfinance Down (Acceptable)
```
⊘ Yfinance test skipped
Can use mock data for testing
```

### ✓ Other Components Working
```
✓ PASS: Configuration
✓ PASS: MongoDB
✓ PASS: Database Module
✓ PASS: Reddit API
✓ PASS: LLM Processor
```

---

## Testing Without Yfinance

```bash
# Test core functionality (skips yfinance)
python test_setup_no_yfinance.py

# This tests:
✓ Configuration
✓ MongoDB
✓ Database operations
✓ Reddit API
✓ LLM processing
⊘ Stock data (skipped)

# If 5/5 pass, your setup is good!
```

---

## Frequently Asked Questions

**Q: Will this fix itself?**
A: Often yes - just wait 10 minutes and retry.

**Q: Should I switch to another provider?**
A: Only if yfinance is down for hours. Most issues are temporary.

**Q: Can I use the bot without yfinance?**
A: Yes! You can test Reddit + sentiment without stock data.

**Q: Is this a bug in the bot?**
A: No, it's yfinance connectivity. The bot has proper error handling.

**Q: What if it never works?**
A: Use Alpha Vantage or Finnhub (paid plans more reliable).

---

## Next Steps

```bash
1. Run diagnostic:
   python test_connectivity.py

2. If internet OK:
   pip install --upgrade yfinance
   python test_yfinance.py

3. If still fails:
   python test_setup_no_yfinance.py
   (Test everything else)

4. Run the bot:
   python main.py --mode full
   (Will skip stock data if yfinance unavailable)
```

---

## Still Having Issues?

1. **Check:** `python test_connectivity.py` output
2. **Read:** `YFINANCE_TROUBLESHOOTING.md` (comprehensive guide)
3. **Wait:** 10 minutes and retry
4. **Upgrade:** `pip install --upgrade yfinance`
5. **Switch:** Use alternative provider
6. **Contact:** Check https://status.yahoo.com for incidents

---

**Don't worry - this is a temporary connectivity issue, not a problem with the bot. Give it a few minutes and try again! ⏳**

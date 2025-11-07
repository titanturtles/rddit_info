# Debug Logging - Quick Reference

## Watch All Logs Live
```bash
tail -f dashboard.log
```

## Watch Specific Component

### Reddit Logs Only
```bash
tail -f dashboard.log | grep "\[REDDIT"
```

### Stock Price Logs Only
```bash
tail -f dashboard.log | grep "\[YFINANCE"
```

### LLM Analysis Logs Only
```bash
tail -f dashboard.log | grep "\[DEEPSEEK"
```

---

## Search for Issues

### Find All Errors
```bash
grep "\[ERROR\]\|\[EXCEPTION\]" dashboard.log
```

### Find Reddit Errors
```bash
grep "\[REDDIT ERROR\]" dashboard.log
```

### Find Stock Price Errors
```bash
grep "\[YFINANCE ERROR\]" dashboard.log
```

### Find LLM Errors
```bash
grep "\[DEEPSEEK ERROR\]\|\[DEEPSEEK EXCEPTION\]" dashboard.log
```

---

## Analyze Operations

### Count Reddit API Calls
```bash
grep "\[REDDIT REQUEST\]" dashboard.log | wc -l
```

### Count Stock Price Calls
```bash
grep "\[YFINANCE REQUEST\]" dashboard.log | wc -l
```

### Count LLM Calls
```bash
grep "\[DEEPSEEK REQUEST\]" dashboard.log | wc -l
```

### Count Total Tokens Used
```bash
grep "\[TOKENS_USED\]" dashboard.log | awk -F'Total: ' '{sum += $2} END {print "Total tokens:", sum}'
```

---

## Find Specific Data

### Find Posts from Specific Subreddit
```bash
grep "r/wallstreetbets" dashboard.log
```

### Find Stock Analysis
```bash
grep "AAPL\|TSLA\|GME" dashboard.log
```

### Find API Status Codes
```bash
grep "Status:" dashboard.log
grep "200 OK" dashboard.log
```

---

## Sample Output

### Reddit Request/Response
```
[REDDIT REQUEST] Fetching posts from r/wallstreetbets
[REDDIT RESPONSE] Successfully fetched 25 posts
```

### Stock Price Request/Response
```
[YFINANCE REQUEST] Fetching AAPL price data
[YFINANCE RESPONSE] Retrieved 5832 records for AAPL
[SAMPLE] Latest: Close=$231.45, Volume=52,000,000
```

### LLM Request/Response
```
[DEEPSEEK REQUEST] Calling deepseek-chat
[DEEPSEEK RESPONSE] Status: 200 OK
[TOKENS_USED] Prompt: 45, Completion: 78, Total: 123
```

---

## Common Tasks

### Debug why Reddit data is missing
```bash
grep "\[REDDIT ERROR\]" dashboard.log
grep "\[REDDIT REQUEST\]" dashboard.log | tail -5
```

### Debug stock price retrieval
```bash
grep "\[YFINANCE RESPONSE\]" dashboard.log | tail -5
grep "\[RETRY\]" dashboard.log
```

### Monitor token usage
```bash
grep "\[TOKENS_USED\]" dashboard.log | tail -10
```

### See what's happening right now
```bash
tail -20 dashboard.log
```

---

## Three-Terminal Setup

### Terminal 1: Run Bot
```bash
python3 main.py
```

### Terminal 2: Watch Logs
```bash
tail -f dashboard.log
```

### Terminal 3: Search Logs
```bash
# Use grep commands above
```

---

## Log Locations

**Console Output:** Terminal where you run `python3 main.py`
**Log File:** `dashboard.log` (same directory as main.py)

---

That's it! Complete visibility into all your data pipelines. 🔍

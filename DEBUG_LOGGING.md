# Debug Logging for Reddit, yfinance, and Deepseek

**Date:** 2025-11-07
**Status:** ✅ COMPLETE
**Coverage:** Reddit API, Yahoo Finance, Deepseek LLM

---

## Overview

Comprehensive debug logging has been added to all three critical data sources:

1. **Reddit API (reddit_fetcher.py)** - Track post fetching
2. **Yahoo Finance (stock_data_fetcher.py)** - Track price data retrieval
3. **Deepseek LLM (llm_processor.py)** - Track sentiment analysis calls

---

## What Gets Logged

### Reddit API Requests

When fetching Reddit posts:

```
================================================================================
[REDDIT REQUEST] Fetching posts from r/wallstreetbets
[PARAMS] time_filter=month, limit=100
================================================================================
[REDDIT POST] ID=abc123, Title=GME going to the moon..., Score=5432, Comments=234
[REDDIT POST] ID=def456, Title=TSLA earnings beat..., Score=3210, Comments=156
...
================================================================================
[REDDIT RESPONSE] Successfully fetched 25 posts from r/wallstreetbets
[STATS] Total posts: 25, First post: GME going to the moon...
================================================================================
```

### Yahoo Finance Requests

When fetching stock prices:

```
================================================================================
[YFINANCE REQUEST] Fetching AAPL price data
[PARAMS] start_date=2024-01-01, end_date=2025-11-07, interval=1h
[ATTEMPT] 1/3
================================================================================
================================================================================
[YFINANCE RESPONSE] Retrieved 5832 records for AAPL
[DATA] Date range: 2024-01-01 to 2025-11-07
[COLUMNS] ['Open', 'High', 'Low', 'Close', 'Volume']
[SAMPLE] Latest: Close=$231.45, Volume=52,000,000
================================================================================
```

### Deepseek LLM Requests

When analyzing sentiment:

```
================================================================================
[DEEPSEEK REQUEST] Calling deepseek-chat
[ENDPOINT] https://api.deepseek.com/v1/chat/completions
[PARAMS] temperature=0.3, max_tokens=500, timeout=30s
[PROMPT] Analyze the sentiment of: "AAPL stock is performing well..."
[PROMPT_LENGTH] 127 characters
================================================================================
================================================================================
[DEEPSEEK RESPONSE] Status: 200 OK
[MODEL] deepseek-chat
[TOKENS_USED] Prompt: 45, Completion: 78, Total: 123
[FINISH_REASON] stop
[RESPONSE] The sentiment is BULLISH. AAPL shows positive momentum...
[RESPONSE_LENGTH] 156 characters
================================================================================
```

---

## Log Format Reference

### Reddit API Format

```
[REDDIT REQUEST] - Indicates Reddit API call starting
[PARAMS] - Shows parameters (time_filter, limit)
[REDDIT POST] - Individual post details (ID, Title, Score, Comments)
[REDDIT RESPONSE] - Final results summary
[STATS] - Statistics about fetched posts
[REDDIT ERROR] - Any errors during fetching
```

### Yahoo Finance Format

```
[YFINANCE REQUEST] - Indicates yfinance API call starting
[PARAMS] - Shows parameters (date range, interval)
[ATTEMPT] - Current attempt number
[YFINANCE] - Debug info about ticker/history
[YFINANCE RESPONSE] - Successful response with data details
[DATA] - Date range and columns in response
[SAMPLE] - Example data point
[YFINANCE ERROR] - Any errors during fetch
[RETRY] - Retry information (exponential backoff)
```

### Deepseek LLM Format

```
[DEEPSEEK REQUEST] - Indicates LLM API call starting
[ENDPOINT] - API endpoint URL
[PARAMS] - Temperature, max_tokens, timeout
[PROMPT] - The prompt being sent
[PROMPT_LENGTH] - Length of prompt
[DEEPSEEK] - Debug info about request/response
[DEEPSEEK RESPONSE] - Successful response
[MODEL] - Model name used
[TOKENS_USED] - Token usage breakdown
[FINISH_REASON] - Why LLM stopped (usually "stop")
[RESPONSE] - LLM's response text
[RESPONSE_LENGTH] - Length of response
[DEEPSEEK ERROR] - Any errors during API call
[DEEPSEEK EXCEPTION] - Unhandled exceptions
[EXCEPTION_TYPE] - Type of exception
[TRACEBACK] - Full Python traceback
```

---

## Viewing Debug Logs

### Real-Time Monitoring

```bash
# Watch all logs in real-time
tail -f dashboard.log

# Watch only Reddit logs
tail -f dashboard.log | grep "\[REDDIT"

# Watch only yfinance logs
tail -f dashboard.log | grep "\[YFINANCE"

# Watch only Deepseek logs
tail -f dashboard.log | grep "\[DEEPSEEK"
```

### Search Logs

```bash
# Find all Reddit requests
grep "\[REDDIT REQUEST\]" dashboard.log

# Find all yfinance errors
grep "\[YFINANCE ERROR\]" dashboard.log

# Find all Deepseek API calls
grep "\[DEEPSEEK REQUEST\]" dashboard.log

# Find all exceptions
grep "\[EXCEPTION" dashboard.log
```

### Count Operations

```bash
# Count Reddit API calls
grep "\[REDDIT REQUEST\]" dashboard.log | wc -l

# Count yfinance calls
grep "\[YFINANCE REQUEST\]" dashboard.log | wc -l

# Count Deepseek API calls
grep "\[DEEPSEEK REQUEST\]" dashboard.log | wc -l

# Count errors
grep "\[ERROR\]\|\[EXCEPTION\]" dashboard.log | wc -l
```

---

## Example: Tracking a Complete Analysis

### Step 1: Reddit fetching
```
[REDDIT REQUEST] Fetching posts from r/wallstreetbets
[REDDIT POST] ID=xyz123, Title=AAPL analysis, Score=1234, Comments=45
[REDDIT RESPONSE] Successfully fetched 10 posts
```

### Step 2: Stock price fetching
```
[YFINANCE REQUEST] Fetching AAPL price data
[YFINANCE RESPONSE] Retrieved 5832 records for AAPL
[SAMPLE] Latest: Close=$231.45, Volume=52,000,000
```

### Step 3: LLM analysis
```
[DEEPSEEK REQUEST] Calling deepseek-chat
[PROMPT] Analyze sentiment of post: "AAPL stock is going up..."
[DEEPSEEK RESPONSE] Status: 200 OK
[RESPONSE] The sentiment is BULLISH...
[TOKENS_USED] Prompt: 45, Completion: 78, Total: 123
```

All three operations are logged, allowing complete tracing of data flow!

---

## Debugging Examples

### Example 1: Reddit data not loading

```bash
# Check for Reddit errors
grep "\[REDDIT ERROR\]" dashboard.log

# If error found:
[REDDIT ERROR] API error while fetching posts: Rate limited by Reddit API

# Solution: Check credentials and rate limits
```

### Example 2: Stock price missing

```bash
# Check yfinance requests
grep "\[YFINANCE REQUEST\]" dashboard.log | grep "TSLA"

# Check if response was empty
grep "\[YFINANCE\]" dashboard.log | grep "No data found"

# Check retries
grep "\[RETRY\]" dashboard.log
```

### Example 3: LLM analysis failing

```bash
# Check Deepseek requests
grep "\[DEEPSEEK REQUEST\]" dashboard.log

# Check for errors
grep "\[DEEPSEEK ERROR\]\|\[DEEPSEEK EXCEPTION\]" dashboard.log

# View full error details
grep -A 5 "\[DEEPSEEK ERROR\]" dashboard.log
```

---

## Performance Analysis with Logs

### Timing Analysis

Each section is clearly marked with `=` separators. Timestamps at the start and end let you calculate duration:

```bash
# Extract timestamps for a specific operation
grep -A 10 "\[REDDIT REQUEST\]" dashboard.log | head -20

# Manual: Note timestamp of [REQUEST] and [RESPONSE]
# Difference = API call duration
```

### Data Volume

The logs show exactly how much data was retrieved:

```bash
# See how many Reddit posts fetched
grep "\[REDDIT RESPONSE\]" dashboard.log | head -1
# Output: [REDDIT RESPONSE] Successfully fetched 100 posts

# See how many stock records
grep "\[YFINANCE RESPONSE\]" dashboard.log | head -1
# Output: [YFINANCE RESPONSE] Retrieved 5832 records for AAPL
```

### Token Usage

For Deepseek, see exactly how many tokens were used:

```bash
# Extract token usage
grep "\[TOKENS_USED\]" dashboard.log

# Count total tokens across all calls
grep "\[TOKENS_USED\]" dashboard.log | awk -F'Total: ' '{sum += $2} END {print "Total tokens:", sum}'
```

---

## Integration with Main Logging

These debug logs integrate with the existing HTTP request/response logging:

```
[HTTP REQUEST] GET /api/dashboard/stats
  └── Triggers internal processing
  ├── [REDDIT REQUEST] Fetching posts...
  ├── [YFINANCE REQUEST] Fetching prices...
  └── [DEEPSEEK REQUEST] Analyzing sentiment...
[HTTP RESPONSE] 200 OK with combined results
```

Complete end-to-end tracing is possible!

---

## Useful Grep Patterns

### Find successful operations
```bash
grep "\[REQUEST\]" dashboard.log | grep -v "ERROR"
```

### Find failed operations
```bash
grep "\[ERROR\]\|\[EXCEPTION\]" dashboard.log
```

### Find by timestamp (hour)
```bash
grep "14:3[0-9]" dashboard.log  # All logs from 2:30-2:39 PM
```

### Find specific stock
```bash
grep "AAPL\|TSLA\|GME" dashboard.log
```

### Find specific subreddit
```bash
grep "wallstreetbets\|stocks\|investing" dashboard.log
```

### Find API errors
```bash
grep "status.*4[0-9][0-9]\|status.*5[0-9][0-9]" dashboard.log
```

---

## Log Fields Explained

| Field | Meaning | Example |
|-------|---------|---------|
| [REDDIT REQUEST] | Reddit API call starting | Marks start of fetch_posts() |
| [PARAMS] | Function parameters | time_filter=month, limit=100 |
| [REDDIT POST] | Individual post | ID=xyz, Title=..., Score=1234 |
| [STATS] | Summary statistics | Total posts: 25 |
| [YFINANCE REQUEST] | yfinance API call | Fetching AAPL from 2024-01-01 |
| [ATTEMPT] | Retry attempt number | 1/3 (first of three retries) |
| [DATA] | Data details | Date range, column names |
| [SAMPLE] | Example data point | Latest: Close=$231.45 |
| [DEEPSEEK REQUEST] | Deepseek API call | Calling deepseek-chat |
| [ENDPOINT] | API endpoint URL | https://api.deepseek.com/v1/... |
| [PROMPT] | Input to LLM | First 100 chars of prompt |
| [TOKENS_USED] | Token consumption | Prompt: 45, Completion: 78 |
| [RESPONSE] | LLM output | First 150 chars of response |

---

## Files Modified

### Code Changes
1. **reddit_fetcher.py** (Lines 73-120)
   - Request logging at fetch start
   - Post details logging
   - Response summary logging
   - Error logging with context

2. **stock_data_fetcher.py** (Lines 50-92)
   - Request logging with parameters
   - Attempt tracking
   - Response details (date range, columns)
   - Sample data logging
   - Error and retry logging

3. **llm_processor.py** (Lines 64-144)
   - Request logging with endpoint and parameters
   - Prompt logging (first 100 chars)
   - Request payload logging (debug level)
   - Response logging with token usage
   - Finish reason logging
   - Full exception traceback logging

---

## Summary

### What You Get
✅ Complete visibility into Reddit API calls
✅ Detailed stock price data retrieval tracking
✅ Full Deepseek API request/response logging
✅ Token usage tracking for cost monitoring
✅ Retry attempt logging with exponential backoff
✅ Full exception tracebacks for debugging

### How to Use

**Watch real-time logs:**
```bash
tail -f dashboard.log
```

**Monitor specific operation:**
```bash
tail -f dashboard.log | grep "\[REDDIT\|YFINANCE\|DEEPSEEK\]"
```

**Search for specific issues:**
```bash
grep "\[ERROR\]\|\[EXCEPTION\]" dashboard.log
```

**Analyze performance:**
```bash
grep "\[TOKENS_USED\]" dashboard.log
grep "\[YFINANCE RESPONSE\]" dashboard.log
```

---

## Next Steps

1. **Run your bot with enhanced logging:**
   ```bash
   python3 main.py
   ```

2. **Watch the logs:**
   ```bash
   tail -f dashboard.log
   ```

3. **See detailed request/response data in real-time!**

Your data pipelines now have complete visibility! 🔍📊

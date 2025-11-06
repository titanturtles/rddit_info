# LLM Audit Trail - Quick Start Guide

## Overview

All LLM API calls (requests and responses) are automatically stored in MongoDB for debugging, auditing, and analysis. This provides complete transparency into:
- What prompts were sent to the LLM
- What responses were received
- Any errors that occurred
- When each call was made
- Performance metrics (token counts, temperature settings)

---

## Getting Started (2 minutes)

### 1. Run the Bot

```bash
# This will start generating LLM calls that get logged automatically
python main.py --mode analyze
```

### 2. Connect to MongoDB

```bash
# In a new terminal
mongosh
use reddit_trading
```

### 3. View Your First Logs

```javascript
// See the 5 most recent LLM calls
db.llm_responses.find()
  .sort({ timestamp: -1 })
  .limit(5)
  .pretty()
```

You should see output like:
```javascript
{
  "_id": ObjectId("..."),
  "timestamp": ISODate("2025-11-06T12:30:45.123Z"),
  "model": "deepseek-chat",
  "provider": "deepseek",
  "prompt": "Extract all stock ticker symbols from...",
  "response": "AAPL, TSLA, MSFT",
  "raw_response": "{\"id\": \"...\", \"choices\": [...]}",
  "status": "success",
  "error": null,
  "prompt_length": 245,
  "response_length": 18,
  "temperature": 0.3,
  "max_tokens": 500
}
```

---

## Common Queries

### Check Total Calls Made

```javascript
db.llm_responses.countDocuments({})
```

### See Success Rate

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: null,
      total: { $sum: 1 },
      success: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } },
      errors: { $sum: { $cond: [{ $eq: ["$status", "error"] }, 1, 0] } },
      exceptions: { $sum: { $cond: [{ $eq: ["$status", "exception"] }, 1, 0] } }
    }
  },
  {
    $project: {
      _id: 0,
      total: 1,
      success: 1,
      errors: 1,
      exceptions: 1,
      success_rate: { $round: [{ $multiply: [{ $divide: ["$success", "$total"] }, 100] }, 2] }
    }
  }
])
```

Expected output:
```javascript
{
  "total": 42,
  "success": 40,
  "errors": 2,
  "exceptions": 0,
  "success_rate": 95.24
}
```

### Find Failed Calls

```javascript
// See what went wrong
db.llm_responses.find({ status: { $in: ["error", "exception"] } })
  .pretty()
```

### Look at Prompts for a Specific Symbol

```javascript
// Find all LLM calls that mentioned "AAPL"
db.llm_responses.find({ prompt: /AAPL/i })
  .projection({ timestamp: 1, prompt: 1, response: 1, status: 1 })
  .pretty()
```

### Get Statistics on Response Sizes

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: "$status",
      avg_prompt_length: { $avg: "$prompt_length" },
      avg_response_length: { $avg: "$response_length" },
      min_response: { $min: "$response_length" },
      max_response: { $max: "$response_length" }
    }
  }
])
```

---

## Debugging: When Things Go Wrong

### Find a Specific Error

```javascript
// If you saw an error in the logs, find the details
db.llm_responses.findOne({ status: "error" }, { prompt: 1, error: 1, timestamp: 1 })
```

### See Raw Response from API

```javascript
// When you need to see exactly what the API returned
db.llm_responses.findOne({ status: "success" }, { raw_response: 1 })
```

### Track Error Frequency

```javascript
// Which types of errors are most common?
db.llm_responses.aggregate([
  { $match: { status: { $in: ["error", "exception"] } } },
  { $group: { _id: "$error", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 5 }
])
```

---

## Understanding the Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `_id` | MongoDB document ID | `ObjectId("...")` |
| `timestamp` | When the call was made | `2025-11-06T12:30:45.123Z` |
| `model` | Which LLM model was used | `"deepseek-chat"` |
| `provider` | LLM provider | `"deepseek"` |
| `prompt` | The question sent to LLM (first 1000 chars) | `"Extract stocks from..."` |
| `response` | The answer from LLM | `"AAPL, TSLA"` |
| `raw_response` | Full API response (first 5000 chars) | JSON string from API |
| `status` | Result status | `"success"`, `"error"`, or `"exception"` |
| `error` | Error message (if failed) | `"Status 429: Rate limited"` |
| `prompt_length` | Total chars in prompt | `245` |
| `response_length` | Total chars in response | `18` |
| `temperature` | LLM creativity setting (0=deterministic, 1=creative) | `0.3` |
| `max_tokens` | Max response length allowed | `500` |

---

## Real-World Examples

### Example 1: Audit a Sentiment Analysis

**Scenario:** You want to verify what sentiment was assigned to a post about Tesla.

```javascript
// Find all sentiment analysis calls for TSLA
db.llm_responses.find({
  prompt: /TSLA/i,
  status: "success"
}).projection({
  timestamp: 1,
  prompt: 1,
  response: 1
}).pretty()
```

### Example 2: Troubleshoot High Latency

**Scenario:** The bot is running slowly. You want to see if LLM calls are the bottleneck.

```javascript
// Find calls with long responses (usually indicates processing time)
db.llm_responses.find({ response_length: { $gt: 1000 } })
  .projection({ timestamp: 1, response_length: 1 })
  .sort({ response_length: -1 })
  .limit(10)
```

### Example 3: Monitor API Cost

**Scenario:** Count how many tokens are being used (useful for billing).

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: null,
      total_prompt_tokens: { $sum: "$prompt_length" },
      total_response_tokens: { $sum: "$response_length" }
    }
  }
])
```

### Example 4: Find Oldest Successful Call

```javascript
db.llm_responses.findOne(
  { status: "success" },
  { timestamp: 1 }
).sort({ timestamp: 1 })
```

### Example 5: Backup Your LLM Logs

```bash
# Export to CSV for analysis in Excel
mongoexport --db reddit_trading --collection llm_responses \
  --fields timestamp,model,status,prompt_length,response_length \
  --out llm_responses_backup.csv
```

---

## Maintenance

### Keep Database Clean (Optional)

Delete logs older than 30 days to save space:

```javascript
db.llm_responses.deleteMany({
  timestamp: {
    $lt: new Date(new Date().setDate(new Date().getDate() - 30))
  }
})
```

### Check Collection Size

```javascript
db.llm_responses.stats()
```

Look for `"size"` and `"count"` fields. Typical sizes:
- 100 calls: ~0.1-0.3 MB
- 1000 calls: ~1-3 MB
- 10000 calls: ~10-30 MB

### Create Indexes for Faster Queries

```javascript
// Speed up common searches
db.llm_responses.createIndex({ timestamp: -1 })
db.llm_responses.createIndex({ status: 1 })
db.llm_responses.createIndex({ model: 1 })
```

---

## Integration with Your Code

The LLM response logging happens **automatically**. You don't need to do anything special!

### How It Works:

1. When your code calls `llm_processor.analyze_sentiment()` or `extract_stock_symbols()`
2. The `_call_llm()` method sends the request to Deepseek
3. Whether it succeeds or fails, `_store_llm_response()` saves it to MongoDB
4. All data (prompt, response, error) is stored for auditing

### View in Your Code:

```python
from llm_processor import LLMProcessor

processor = LLMProcessor()

# This automatically gets logged to MongoDB
result = processor.analyze_sentiment("AAPL is great!")

# The database now has a record of:
# - The exact prompt sent
# - The exact response received
# - When it happened
# - Whether it succeeded
```

---

## What Gets Stored vs What Doesn't

### ✅ Stored (Useful for Debugging)
- Prompts (first 1000 characters)
- Responses (full text)
- Error messages
- Request timestamps
- Model name and provider
- Temperature and token settings

### ❌ Not Stored (For Security/Privacy)
- API keys
- Authorization headers
- Full raw JSON responses (truncated to 5000 chars)
- System messages

---

## Summary

Your bot now has complete audit trail capabilities:

✅ Every LLM call is logged
✅ Both successes and failures are recorded
✅ Full debugging information available
✅ Easy MongoDB queries for analysis
✅ Automatic - no code changes needed

To get started right now:

```bash
# 1. Run the bot
python main.py --mode analyze

# 2. Open MongoDB in another terminal
mongosh

# 3. Check the logs
use reddit_trading
db.llm_responses.find().limit(5).pretty()
```

That's it! You now have complete visibility into all LLM operations.

---

**See Also:**
- `LLM_RESPONSES_STORAGE.md` - Comprehensive MongoDB query guide
- `PROJECT_STATUS.md` - Overall project status
- `SOLUTIONS_QUICK_REFERENCE.md` - Common issues and fixes

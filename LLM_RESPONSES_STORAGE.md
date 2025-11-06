# LLM Responses Storage

## Overview

All raw LLM requests and responses are now automatically stored in MongoDB for:
- Debugging
- Auditing
- Analysis
- Troubleshooting

## Database Collection

**Collection Name:** `llm_responses`
**Location:** `reddit_trading.llm_responses`

## Document Structure

Each LLM call is stored with the following fields:

```json
{
  "_id": ObjectId("..."),
  "timestamp": "2025-11-05T12:00:00.000Z",
  "model": "deepseek-chat",
  "provider": "deepseek",
  "prompt": "Extract all stock ticker symbols...",
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

### Fields Explained

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | MongoDB auto-generated ID |
| `timestamp` | DateTime | When the request was made |
| `model` | String | Which LLM model (e.g., "deepseek-chat") |
| `provider` | String | Provider name (e.g., "deepseek") |
| `prompt` | String | The prompt sent to LLM (first 1000 chars) |
| `response` | String | The parsed response from LLM |
| `raw_response` | String | Full raw JSON response (first 5000 chars) |
| `status` | String | "success", "error", or "exception" |
| `error` | String | Error message if failed (null on success) |
| `prompt_length` | Int | Total length of prompt |
| `response_length` | Int | Total length of response |
| `temperature` | Float | Temperature setting used |
| `max_tokens` | Int | Max tokens setting used |

## Status Values

- **success** - LLM call succeeded and response was parsed
- **error** - HTTP error or API error (see `error` field)
- **exception** - Exception during request (network error, timeout, etc.)

## Querying Examples

### Connect to MongoDB

```bash
mongosh
use reddit_trading
```

### View Recent LLM Calls

```javascript
db.llm_responses.find()
  .sort({ timestamp: -1 })
  .limit(10)
  .pretty()
```

### Find Failed Calls

```javascript
db.llm_responses.find({ status: { $in: ["error", "exception"] } })
  .pretty()
```

### Find Successful Calls

```javascript
db.llm_responses.find({ status: "success" })
  .pretty()
```

### Search by Prompt Content

```javascript
db.llm_responses.find({ prompt: /AAPL/i })
  .pretty()
```

### Count by Status

```javascript
db.llm_responses.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

### Find Slow Calls

```javascript
db.llm_responses.find({ response_length: { $gt: 2000 } })
  .pretty()
```

### View Error Details

```javascript
db.llm_responses.find({ status: "error" }, { prompt: 1, error: 1, timestamp: 1 })
  .pretty()
```

## Analysis Scripts

### Get LLM Statistics

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: null,
      total_calls: { $sum: 1 },
      success: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } },
      errors: { $sum: { $cond: [{ $ne: ["$status", "success"] }, 1, 0] } },
      avg_response_length: { $avg: "$response_length" },
      avg_prompt_length: { $avg: "$prompt_length" }
    }
  }
])
```

### Success Rate

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: null,
      total: { $sum: 1 },
      success: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } }
    }
  },
  {
    $project: {
      success_rate: { $divide: ["$success", "$total"] },
      _id: 0
    }
  }
])
```

### Calls by Hour

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: { $hour: "$timestamp" },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])
```

## Monitoring

### Watch Live Requests

```bash
# Terminal 1 - Start watching
mongosh
use reddit_trading
db.llm_responses.watch()
```

```bash
# Terminal 2 - Run your bot
python main.py --mode analyze
```

## Storage Size

Monitor collection size:

```javascript
db.llm_responses.stats()
```

Expected sizes:
- Each document: ~1-3 KB
- 1000 calls: ~1-3 MB
- 10000 calls: ~10-30 MB

## Maintenance

### Delete Old Responses

```javascript
// Delete responses older than 30 days
db.llm_responses.deleteMany({
  timestamp: {
    $lt: new Date(new Date().setDate(new Date().getDate() - 30))
  }
})
```

### Export to CSV

```bash
mongoexport --db reddit_trading --collection llm_responses \
  --fields timestamp,model,status,prompt_length,response_length \
  --out llm_responses.csv
```

### Backup Collection

```bash
mongodump --db reddit_trading --collection llm_responses \
  --out ./backup/
```

## Troubleshooting

### Check if Collection Exists

```javascript
db.getCollectionNames().includes('llm_responses')
```

### Create Indexes

```javascript
// For faster queries
db.llm_responses.createIndex({ timestamp: -1 })
db.llm_responses.createIndex({ status: 1 })
db.llm_responses.createIndex({ provider: 1 })
```

### View Raw Response Details

```javascript
db.llm_responses.findOne({ status: "error" }, { raw_response: 1 })
```

## Integration with Monitoring

### Monitor Failed Calls

```javascript
// Alert on error rate
var errorRate = db.llm_responses.aggregate([
  { $match: { timestamp: { $gte: new Date(new Date() - 3600000) } } },
  { $group: {
      _id: null,
      total: { $sum: 1 },
      errors: { $sum: { $cond: [{ $ne: ["$status", "success"] }, 1, 0] } }
    }
  }
])
```

### Track Response Times

The `timestamp` field can be used to calculate response times by comparing
consecutive entries.

## What's Stored vs Not Stored

### Stored
✓ Prompts (truncated to 1000 chars)
✓ Responses (full text)
✓ Raw JSON responses (truncated to 5000 chars)
✓ Error messages
✓ Request metadata (model, temperature, tokens)
✓ Status and timestamps

### Not Stored (for Privacy/Security)
✗ API Key
✗ Authorization headers
✗ Full raw JSON (truncated to 5000 chars)
✗ System message

## Best Practices

1. **Regular Cleanup**: Delete old responses regularly to save space
2. **Monitoring**: Set up alerts for error spikes
3. **Analysis**: Regularly review failures to improve prompts
4. **Privacy**: Be aware that prompts are stored in the database
5. **Backups**: Back up the collection periodically

## Example Analysis

### Find Most Common Errors

```javascript
db.llm_responses.aggregate([
  { $match: { status: "error" } },
  { $group: { _id: "$error", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

### Success Rate Over Time

```javascript
db.llm_responses.aggregate([
  {
    $group: {
      _id: {
        $dateToString: { format: "%Y-%m-%d", date: "$timestamp" }
      },
      total: { $sum: 1 },
      success: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } }
    }
  },
  {
    $project: {
      success_rate: { $divide: ["$success", "$total"] },
      _id: 1
    }
  },
  { $sort: { _id: 1 } }
])
```

---

## Summary

All LLM API calls are now fully logged and stored in MongoDB. This enables:

✓ Complete audit trail of all LLM operations
✓ Easy debugging of failed requests
✓ Performance monitoring
✓ Analysis of LLM behavior
✓ Compliance and record-keeping

Access the data anytime via MongoDB queries or export for analysis.

# Database Cleaning Guide

**Status:** ✅ Complete
**File:** clean_database.py
**Type:** Interactive CLI utility

---

## Overview

The database cleaning script provides safe, interactive options to maintain and optimize your MongoDB database.

**Features:**
- View collection statistics
- Delete old posts
- Remove duplicates
- Clean failed LLM responses
- Clear collections (with confirmation)
- Rebuild indexes
- Export collections to JSON

---

## Running the Script

```bash
cd /home/biajee/Documents/code/ai_trading3/rddt_info
python3 clean_database.py
```

You'll see an interactive menu with options.

---

## Menu Options

### 1. Show Database Statistics

Displays statistics for all collections:

```
[POSTS]
  Collection: reddit_posts
  Documents: 364
  Size: 2.45 MB
  Avg Doc Size: 6,923 bytes

[COMMENTS]
  Collection: reddit_comments
  Documents: 569
  Size: 3.12 MB
  Avg Doc Size: 5,480 bytes

[SENTIMENT_ANALYSIS]
  Collection: sentiment_analysis
  Documents: 1,422
  Size: 5.67 MB
  Avg Doc Size: 4,001 bytes

TOTAL: 2,355 documents, 11.24 MB
```

**Use when:** You want to understand current database size and document counts.

---

### 2. Delete Posts Older Than X Days

Removes posts older than specified number of days.

**Example:**
```
Enter number of days to keep (default 90): 30
[CLEANUP] Deleting posts older than 30 days
Found 125 posts older than 30 days
Delete 125 posts? (yes/no): yes
[DELETED] 125 old posts
```

**Use when:**
- Archiving old data
- Reducing database size
- Cleaning up test data
- Keeping only recent posts

**Default:** 90 days
**Safety:** Requires confirmation before deletion

---

### 3. Delete Duplicate Posts

Finds and removes duplicate posts (same reddit_id).

**Example:**
```
[CLEANUP] Detecting duplicate posts
Found 5 duplicate groups (8 total duplicates)
Delete 8 duplicate posts? (yes/no): yes
[DELETED] 8 duplicate posts
```

**Use when:**
- Fixing data from re-runs
- Removing accidental duplicates
- Cleaning up imports

**Safety:** 
- Keeps first occurrence
- Deletes newer duplicates
- Requires confirmation

---

### 4. Delete Posts Without Sentiment Analysis

Removes posts that don't have corresponding sentiment analysis.

**Example:**
```
[CLEANUP] Finding posts without sentiment analysis
Found 45 posts without sentiment analysis
Delete 45 posts? (yes/no): yes
[DELETED] 45 posts without sentiment
```

**Use when:**
- Cleaning incomplete data
- Ensuring data consistency
- Removing failed analyses

**Safety:** Requires confirmation

---

### 5. Delete Failed LLM Responses

Removes failed Deepseek API responses.

**Example:**
```
[CLEANUP] Deleting failed LLM responses
Found 12 failed LLM responses
Delete 12 failed responses? (yes/no): yes
[DELETED] 12 failed LLM responses
```

**What gets deleted:**
- Timeout errors
- API failures
- Exception responses

**What's kept:**
- Successful responses
- Partial responses

**Use when:**
- Cleaning error logs
- Retrying analyses

**Safety:** Requires confirmation

---

### 6. Clear Entire Collection

WARNING: Deletes ALL documents from a collection!

**Example:**
```
Available collections:
  1. posts
  2. comments
  3. sentiment_analysis
  4. stock_prices
  5. patterns
  6. llm_responses

Enter collection number: 5
[WARNING] CLEARING COLLECTION: PATTERNS
This will DELETE ALL 247 documents in patterns
Type 'DELETE PATTERNS' to confirm: DELETE PATTERNS
[DELETED] 247 documents from patterns
```

**Use when:**
- Starting fresh with specific collection
- Removing test data
- Resetting analysis

**Safety:**
- ⚠️ EXTREMELY DESTRUCTIVE
- Requires full typed confirmation
- Cannot be undone!

---

### 7. Rebuild Indexes

Rebuilds all MongoDB indexes for performance.

```
[MAINTENANCE] Rebuilding database indexes
Indexes rebuilt successfully
```

**Use when:**
- After large deletions
- Performance degradation
- Data corruption recovery

**What it rebuilds:**
- Posts indexes (created_utc, subreddit, author, reddit_id)
- Comments indexes (created_utc, author, reddit_id)
- Sentiment indexes (reddit_id, stock_symbol, analyzed_date)
- Stock prices indexes (symbol, date)
- Patterns indexes (stock_symbol, correlation_score)

---

### 8. Export Collection to JSON

Backs up a collection to JSON file.

**Example:**
```
Available collections:
  1. posts
  2. comments
  3. sentiment_analysis
  4. stock_prices
  5. patterns
  6. llm_responses

Enter collection number: 1
Enter filepath for export (e.g., ./posts_backup.json): ./posts_backup.json
[EXPORT] Exporting posts to ./posts_backup.json
[EXPORTED] 364 documents to ./posts_backup.json
```

**Use when:**
- Backup before major cleanup
- Data analysis outside MongoDB
- Sharing data
- Historical records

**Output:**
- Valid JSON format
- ObjectIds converted to strings
- Indented for readability

---

### 9. Exit

Exits the cleaning utility.

---

## Common Workflows

### Workflow 1: Full Database Maintenance

1. **Check statistics** (Option 1)
2. **Backup collections** (Option 8) - Backup all important collections
3. **Remove duplicates** (Option 3)
4. **Delete old data** (Option 2) - Keep last 90 days
5. **Remove failed responses** (Option 5)
6. **Rebuild indexes** (Option 7)
7. **Check statistics again** (Option 1) - Verify cleanup

### Workflow 2: Clean Up After Testing

1. **Check statistics** (Option 1)
2. **Delete posts without sentiment** (Option 4)
3. **Delete old posts** (Option 2) - Remove test data
4. **Delete failed LLM responses** (Option 5)
5. **Check statistics** (Option 1)

### Workflow 3: Archive Old Data

1. **Export collection** (Option 8) - Save before delete
2. **Delete old posts** (Option 2) - Keep specific timeframe
3. **Rebuild indexes** (Option 7)
4. **Verify** with Option 1

### Workflow 4: Fresh Start (Dangerous!)

1. **Export all collections** (Option 8) - BACKUP EVERYTHING
2. **Clear each collection** (Option 6) - With confirmations
3. **Rebuild indexes** (Option 7)

---

## Safety Features

### Confirmation Prompts

Most operations require confirmation:
```
Delete 125 posts? (yes/no): 
```

Type exactly `yes` to proceed, anything else cancels.

### Full Confirmations

Destructive operations require full typed confirmation:
```
Type 'DELETE PATTERNS' to confirm:
```

Not just `yes`, but the full collection name.

### No Batch Operations

Script processes one operation at a time, preventing accidents.

---

## Understanding Collection Names

| Key | Collection | Purpose |
|-----|-----------|---------|
| posts | reddit_posts | Reddit posts |
| comments | reddit_comments | Reddit comments |
| sentiment_analysis | sentiment_analysis | Sentiment analysis results |
| stock_prices | stock_prices | Stock price data |
| patterns | trading_patterns | Pattern detection results |
| llm_responses | llm_responses | Deepseek API responses |

---

## Log Output

All operations are logged with timestamps:

```
2025-11-07 14:30:45,123 - INFO - ================================================================================
2025-11-07 14:30:45,123 - INFO - [CLEANUP] Deleting posts older than 30 days
2025-11-07 14:30:45,123 - INFO - ================================================================================
2025-11-07 14:30:45,234 - WARNING - Found 125 posts older than 30 days
2025-11-07 14:30:50,567 - INFO - [DELETED] 125 old posts
```

Logs appear in both console and `dashboard.log`.

---

## Recovery

### Before Major Cleanup

Always backup first:

```bash
# Export critical collections
python3 clean_database.py
# Choose option 8 (Export)
```

This creates JSON files with all your data.

### If Something Goes Wrong

Contact MongoDB administrator or restore from backup:

```bash
# MongoDB has backup features
# Check your database backups
mongodump --db reddit_trading --out ./backup
```

---

## Performance Impact

### During Cleaning

- Database may be slower during deletion
- Index rebuilding can take time
- No data loss (read-only operations don't affect)

### After Cleaning

- ✅ Smaller database size
- ✅ Faster queries
- ✅ Better performance
- ✅ More free disk space

---

## Examples

### Remove Test Data

```
# Option 2: Delete old posts (keep last 1 day)
Enter number of days to keep: 1
Delete 300 posts? yes
```

### Backup Before Major Cleanup

```
# Option 8: Export
# Choose option 1 (posts)
# Enter filename: posts_backup_2025-11-07.json
```

### Clear Pattern Collection After Testing

```
# Option 6: Clear collection
# Choose option 5 (patterns)
# Type: DELETE PATTERNS
```

### Fix Corrupted Sentiment Data

```
# Option 4: Delete posts without sentiment
Delete 50 posts? yes
```

---

## Statistics Reference

When you run Option 1, you'll see:

- **Documents:** Number of records in collection
- **Size:** Total size in MB
- **Avg Doc Size:** Average size of one document (bytes)
- **Collection:** MongoDB collection name (internal)

### What Size Means

- Small sizes (< 100 MB): Typical for trading data
- Large sizes (> 1 GB): Needs optimization
- Growing rapidly: Check for duplicates or errors

---

## Tips

1. **Regular Maintenance:** Run cleanup weekly
2. **Monitor Size:** Check statistics monthly
3. **Backup Before Clean:** Always export critical data first
4. **Test First:** Try on test database before production
5. **Off-Peak Hours:** Run during low traffic
6. **Document Deletions:** Note what you deleted and why

---

## Troubleshooting

### "Collection not found"
- Database not connected
- Collection name misspelled
- MongoDB not running

**Solution:** Check database connection and collection names

### "Permission denied" on export
- Cannot write to filepath
- Directory doesn't exist
- Permission issues

**Solution:** Use absolute path with write permissions

### "Confirmation failed"
- Typed confirmation wrong
- Case sensitivity matters
- Must match exactly

**Solution:** Type exactly as shown, including capitalization

---

## Safe Practices

✅ **DO:**
- Backup before major operations
- Use Option 1 to check size first
- Confirm deletions carefully
- Run during off-peak hours

❌ **DON'T:**
- Skip backups for safety
- Use Option 6 (clear) casually
- Rush confirmations
- Delete during active processing

---

## Summary

The database cleaning script provides:

✅ Safe deletion with confirmations
✅ Statistics and monitoring
✅ Backup and export capabilities
✅ Index maintenance
✅ Duplicate detection
✅ Error cleanup

Start with **Option 1** to see what you have, then plan your cleaning strategy.

---

## Next Steps

1. **Run the script:** `python3 clean_database.py`
2. **Check statistics:** Choose Option 1
3. **Plan cleanup:** Review what needs cleaning
4. **Backup data:** Choose Option 8 for critical collections
5. **Execute cleanup:** Start with safest options (delete old/duplicates)
6. **Verify:** Check statistics again with Option 1

Your database is now maintainable! 🧹

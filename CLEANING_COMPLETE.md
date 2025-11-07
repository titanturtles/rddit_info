# ✅ Database Cleaning Script Complete

**Status:** Production Ready
**File:** clean_database.py
**Type:** Interactive CLI Utility
**Date Created:** 2025-11-07

---

## What's Been Created

A comprehensive, safe database cleaning utility with:

✅ Database statistics and monitoring
✅ Delete old posts (configurable days)
✅ Remove duplicate posts
✅ Clean incomplete data
✅ Delete failed API responses
✅ Clear entire collections (with extreme confirmation)
✅ Rebuild database indexes
✅ Export collections to JSON backup
✅ Full logging of all operations
✅ Safety confirmations on all destructive operations

---

## Current Database Status

From test run:

| Collection | Documents | Size |
|------------|-----------|------|
| Posts | 364 | 0.43 MB |
| Comments | 569 | 0.21 MB |
| Sentiment Analysis | 1,422 | 2.81 MB |
| Stock Prices | 371,307 | 110.09 MB |
| Patterns | 0 | 0.0 MB |
| LLM Responses | 1,291 | 1.86 MB |
| **TOTAL** | **374,953** | **115.4 MB** |

Most space is used by stock price data (110 MB).

---

## How to Use

### Start the Script
```bash
cd /home/biajee/Documents/code/ai_trading3/rddt_info
python3 clean_database.py
```

### Interactive Menu
```
================================================================================
DATABASE CLEANING UTILITY
================================================================================

1. Show database statistics
2. Delete posts older than X days
3. Delete duplicate posts
4. Delete posts without sentiment analysis
5. Delete failed LLM responses
6. Clear entire collection
7. Rebuild indexes
8. Export collection to JSON
9. Exit

================================================================================
Select option (1-9):
```

---

## Menu Options

### 1. Show Statistics (Safe - Read Only)
Displays:
- Document count per collection
- Size in MB
- Average document size
- Total database size

**Use:** Monitor database growth, identify what needs cleaning

### 2. Delete Old Posts (Medium - Confirmation)
Deletes posts older than specified days
- Default: 90 days
- Requires confirmation

**Use:** Archive old data, reduce size

### 3. Delete Duplicates (Medium - Confirmation)
Removes duplicate posts (same reddit_id)
- Keeps first occurrence
- Deletes newer copies
- Requires confirmation

**Use:** Fix data from re-runs

### 4. Delete Posts Without Sentiment (Medium - Confirmation)
Removes posts without sentiment analysis
- Ensures data consistency
- Cleans incomplete records
- Requires confirmation

**Use:** Clean up failed analyses

### 5. Delete Failed LLM Responses (Medium - Confirmation)
Removes failed API calls
- Keeps successful responses
- Deletes errors/timeouts/exceptions
- Requires confirmation

**Use:** Clean error logs

### 6. Clear Collection (Dangerous - Extreme Confirmation)
**WARNING: Deletes ALL documents from a collection!**
- Requires typing exact collection name
- Example: `Type 'DELETE POSTS' to confirm:`
- Cannot be undone!

**Use:** Start fresh with specific collection, reset testing

### 7. Rebuild Indexes (Safe)
Optimizes database performance
- Rebuilds all indexes
- No data loss
- Safe to run anytime

**Use:** After large deletions, performance issues

### 8. Export Collection to JSON (Safe)
Backs up collection to JSON file
- Creates readable JSON
- Converts ObjectIds to strings
- For backup or analysis

**Use:** Before major cleanup, data sharing

### 9. Exit
Closes the utility

---

## Documentation Created

1. **clean_database.py** (370+ lines)
   - Interactive menu system
   - 8 cleaning operations
   - Full error handling
   - Safety confirmations
   - Logging throughout

2. **DATABASE_CLEANING_GUIDE.md** (400+ lines)
   - Comprehensive guide
   - Each option explained
   - Common workflows
   - Safety features
   - Recovery procedures

3. **CLEAN_DB_QUICK.md** (Quick reference)
   - Quick task list
   - Safety levels
   - Common issues
   - Example outputs

4. **CLEANING_COMPLETE.md** (This file)
   - Summary
   - Current status
   - Usage overview

---

## Safety Features

### Confirmation Prompts
```
Delete 125 posts? (yes/no): 
```
Type exactly `yes` to proceed

### Full Confirmations (Destructive)
```
Type 'DELETE PATTERNS' to confirm:
```
Must type exact collection name in capitals

### No Batch Operations
One operation at a time, prevents accidents

### Logging
All operations logged with timestamps to `dashboard.log`

---

## Recommended Cleanup Schedule

### Weekly
```python
# Option 5: Delete failed LLM responses
```
Keep logs clean, minimal impact

### Monthly
```python
# Option 1: Check statistics
# Option 3: Remove duplicates
# Option 2: Delete posts older than 90 days
```
Regular maintenance

### Quarterly
```python
# Full maintenance workflow:
# 1. Statistics
# 2. Backup important collections
# 3. Delete duplicates
# 4. Delete old posts
# 5. Delete failed LLM responses
# 6. Rebuild indexes
# 7. Verify with statistics
```
Comprehensive optimization

---

## Common Workflows

### Quick Size Check
```
Option 1 → View current size
```
Takes 5 seconds

### Remove Error Logs
```
Option 5 → Delete failed LLM responses
```
Clean error logs safely

### Full Maintenance
```
1. Option 1 (check what we have)
2. Option 8 (backup critical collections)
3. Option 3 (remove duplicates)
4. Option 2 (delete old posts - 90 days)
5. Option 5 (delete failed LLM)
6. Option 7 (rebuild indexes)
7. Option 1 (verify results)
```
Takes 10-15 minutes depending on data

### Start Fresh
```
1. Option 8 (BACKUP EVERYTHING first!)
2. Option 6 (clear collection) - repeat for each
3. Option 7 (rebuild indexes)
```
**ONLY after complete backup!**

---

## Safety Checklist

Before major cleanup:
- [ ] Run Option 1 to see current size
- [ ] Export critical collections (Option 8)
- [ ] Save export files to safe location
- [ ] Document what you're deleting and why

During cleanup:
- [ ] Read confirmations carefully
- [ ] Type confirmations exactly
- [ ] Do one operation at a time
- [ ] Check logs for any errors

After cleanup:
- [ ] Run Option 1 to verify changes
- [ ] Check that data still looks correct
- [ ] Rebuild indexes (Option 7)

---

## Example Session

```
$ python3 clean_database.py

DATABASE CLEANING UTILITY
================================================================================

1. Show database statistics
...
Select option (1-9): 1

[POSTS]
  Collection: reddit_posts
  Documents: 364
  Size: 0.43 MB
  ...

TOTAL: 374,953 documents, 115.4 MB

================================================================================
Press Enter to continue...

1. Show database statistics
...
Select option (1-9): 5

[CLEANUP] Deleting failed LLM responses
Found 45 failed LLM responses
Delete 45 failed responses? (yes/no): yes
[DELETED] 45 failed LLM responses

================================================================================
Press Enter to continue...

1. Show database statistics
...
Select option (1-9): 9

Exiting database cleaner
```

---

## Performance Impact

### Before Cleanup
- Total: 115.4 MB
- 374,953 documents
- Largest: stock_prices (110 MB)

### After Typical Cleanup
- **Stock prices unchanged** (necessary data)
- Duplicates removed
- Old posts archived/deleted
- Failed responses cleaned
- **Expected reduction:** 5-15% depending on age/errors

### Benefits
- ✅ Faster queries
- ✅ Smaller backups
- ✅ Less disk usage
- ✅ Better performance
- ✅ Cleaner logs

---

## Collection Reference

| Name | Size | Can Clean? | Keep |
|------|------|-----------|------|
| posts | 0.43 MB | YES | Essential |
| comments | 0.21 MB | MAYBE | Optional |
| sentiment | 2.81 MB | NO | Essential |
| prices | 110 MB | NO | Essential |
| patterns | 0 MB | YES | Testing only |
| llm_responses | 1.86 MB | YES | Error logs |

---

## Troubleshooting

### MongoDB not running
```bash
mongod
# Then try script again
```

### "Collection not found" error
- Check MongoDB is running
- Check collections exist
- Check connectivity

### Can't write export file
- Use absolute path: `/home/user/backups/file.json`
- Check directory exists
- Check write permissions

### Wrong confirmation format
- Type exactly as shown
- `yes` in lowercase for yes/no
- Capitals for DELETE confirmations

---

## Recovery

### If You Made a Mistake

**Before deleting anything:**
- Always export first (Option 8)
- Keep JSON backups
- Document what you delete

**If deletion was a mistake:**
```bash
# MongoDB can restore from backups
mongoimport --db reddit_trading --collection posts posts_backup.json
```

---

## Log Output Example

All operations logged to `dashboard.log`:

```
2025-11-07 15:04:53,891 - INFO - ================================================================================
2025-11-07 15:04:53,891 - INFO - [CLEANUP] Deleting failed LLM responses
2025-11-07 15:04:53,891 - INFO - ================================================================================
2025-11-07 15:04:53,903 - INFO - Found 45 failed LLM responses
2025-11-07 15:04:53,950 - INFO - [DELETED] 45 failed LLM responses
```

---

## Next Steps

### Immediate
```bash
# Test the script
python3 clean_database.py
# Choose Option 1 to see current size
```

### Weekly
```bash
# Clean error logs
python3 clean_database.py
# Choose Option 5
```

### Monthly
```bash
# Full check and maintenance
python3 clean_database.py
# Options: 1 → 3 → 2 → 5 → 7 → 1
```

---

## Summary

You now have a complete database maintenance tool that:

✅ Shows exactly what's in your database
✅ Safely removes old/duplicate/failed data
✅ Optimizes performance
✅ Backs up important data
✅ Logs all operations
✅ Prevents accidental data loss

**Start with Option 1 to see what you have, then decide what to clean!** 🧹

---

**Ready to clean your database? Run: `python3 clean_database.py`**

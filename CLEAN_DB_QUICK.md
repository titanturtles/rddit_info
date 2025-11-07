# Database Cleaning - Quick Reference

## Start the Cleaning Tool

```bash
python3 clean_database.py
```

---

## Menu Options at a Glance

| # | Option | Action | Safe? |
|---|--------|--------|-------|
| 1 | Statistics | View database size | ✅ Read-only |
| 2 | Delete Old Posts | Keep last N days | ✅ Confirmation |
| 3 | Delete Duplicates | Remove same reddit_id | ✅ Confirmation |
| 4 | Delete Posts Without Sentiment | Remove incomplete | ✅ Confirmation |
| 5 | Delete Failed LLM | Clean error logs | ✅ Confirmation |
| 6 | Clear Collection | DELETE ALL ⚠️ | ⚠️ Extreme |
| 7 | Rebuild Indexes | Optimize performance | ✅ Safe |
| 8 | Export to JSON | Backup collection | ✅ Safe |
| 9 | Exit | Leave tool | ✅ Safe |

---

## Common Quick Tasks

### Check Database Size
```
Run: python3 clean_database.py
Choose: 1
Shows: Collection sizes in MB, document counts
```

### Remove Old Posts
```
Run: python3 clean_database.py
Choose: 2
Enter: 90 (keep posts from last 90 days)
Confirm: yes
```

### Backup Before Major Cleanup
```
Run: python3 clean_database.py
Choose: 8
Select: 1 (posts collection)
Enter: ./posts_backup.json
Result: JSON file with all posts
```

### Remove Duplicates
```
Run: python3 clean_database.py
Choose: 3
Confirm: yes (after seeing count)
```

### Delete Failed LLM Calls
```
Run: python3 clean_database.py
Choose: 5
Confirm: yes
```

### Rebuild Indexes (After Cleanup)
```
Run: python3 clean_database.py
Choose: 7
Result: Optimized database
```

---

## Safety Levels

### 🟢 Safe (Read-Only)
- Option 1: Statistics
- Option 7: Rebuild indexes
- Option 8: Export to JSON

### 🟡 Medium (Confirmation Required)
- Option 2: Delete old posts
- Option 3: Delete duplicates
- Option 4: Delete incomplete
- Option 5: Delete failed LLM

### 🔴 Dangerous (Extreme Confirmation)
- Option 6: Clear collection (DELETE ALL)

---

## Typical Cleanup Flow

```
1. Choose Option 1 → Check what you have
2. Choose Option 8 → Backup critical collections
3. Choose Option 3 → Delete duplicates
4. Choose Option 2 → Delete old posts (90 days)
5. Choose Option 5 → Delete failed responses
6. Choose Option 7 → Rebuild indexes
7. Choose Option 1 → Verify cleanup
8. Choose Option 9 → Exit
```

---

## Collections Reference

| Name | Contains | Keep Important? |
|------|----------|-----------------|
| posts | Reddit posts | YES |
| comments | Reddit comments | MAYBE |
| sentiment_analysis | Sentiment results | YES |
| stock_prices | Price data | YES |
| patterns | Pattern detection | MAYBE |
| llm_responses | API calls/errors | NO (can delete) |

---

## Example Outputs

### Statistics Output
```
[POSTS]
  Collection: reddit_posts
  Documents: 364
  Size: 2.45 MB
  Avg Doc Size: 6,923 bytes
```

### Deletion Output
```
Found 125 posts older than 30 days
Delete 125 posts? (yes/no): yes
[DELETED] 125 old posts
```

### Export Output
```
[EXPORTED] 364 documents to ./posts_backup.json
```

---

## Tips

1. **Always check size first** → Option 1
2. **Backup before deleting** → Option 8
3. **Start with safest options** → Options 3, 5, 2
4. **Optimize after cleanup** → Option 7
5. **Verify results** → Option 1 again

---

## Common Issues

### "MongoDB not running"
```bash
# Start MongoDB
mongod
# Then run script again
```

### "Can't write export file"
```
Use full path: /home/user/backups/export.json
Or current directory: ./export.json
```

### "Wrong confirmation"
```
Type exactly as shown
Examples:
- For yes/no: type 'yes' (lowercase)
- For DELETE: type 'DELETE POSTS' (uppercase)
```

---

## Emergency Commands

### Backup Everything
```
python3 clean_database.py
→ Option 8 for each collection
→ Keep all JSONfiles
```

### Clear One Collection
```
python3 clean_database.py
→ Option 6
→ Select collection number
→ Type exact confirmation
```

### Restore from Backup
```
# mongoimport --db reddit_trading --collection posts posts_backup.json
(Restore from JSON if needed)
```

---

## When to Clean

- **Weekly:** Delete failed LLM responses (Option 5)
- **Monthly:** Delete old posts > 90 days (Option 2)
- **Monthly:** Check for duplicates (Option 3)
- **Quarterly:** Full maintenance (all steps)
- **Anytime:** Check statistics (Option 1)

---

**Start with Option 1 to see what you have! 🧹**

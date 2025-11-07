# Web App Quick Start - 5 Minutes

**Status:** ✅ Ready to Use
**Time:** 5 minutes
**Difficulty:** Beginner

---

## Step 1: Install Dependencies (1 minute)

```bash
pip install Flask==2.3.3 flask-cors==4.0.0
```

Or if using the main requirements:

```bash
pip install -r requirements.txt
```

---

## Step 2: Start the Web Server (30 seconds)

```bash
python web_app.py
```

You'll see:

```
Starting Reddit Trading Bot Web Dashboard
Dashboard available at http://localhost:5000
```

---

## Step 3: Open in Browser (30 seconds)

Go to:

```
http://localhost:5000
```

You should see the main dashboard with 4 navigation options:
- Dashboard (home)
- Stocks
- Patterns
- LLM Monitor

---

## Step 4: Run Your Bot (2 minutes)

In a **new terminal**, run:

```bash
python main.py --mode analyze
```

The dashboard will automatically start showing data as the bot collects it.

---

## That's It! 🎉

Your web dashboard is now running and monitoring your trading bot!

### Dashboard Pages

1. **Dashboard** (/)
   - Overall statistics
   - Sentiment distribution
   - Top stocks
   - Recent LLM calls

2. **Stocks** (/stocks)
   - Sentiment breakdown
   - Top mentioned stocks
   - Bullish/bearish breakdown

3. **Patterns** (/patterns)
   - Detected trading patterns
   - Pattern types and confidence

4. **LLM Monitor** (/llm-monitor)
   - LLM API call statistics
   - Success rates
   - Recent calls and errors

---

## Auto-Refresh Behavior

Pages automatically refresh every 15-60 seconds to show latest data.

- **Dashboard:** 30 seconds
- **Stocks:** 30 seconds
- **Patterns:** 60 seconds
- **LLM Monitor:** 15 seconds

---

## What to Look For

✅ **Dashboard Stats** - Should show increasing numbers as bot runs
✅ **Sentiment Chart** - Bullish/neutral/bearish distribution
✅ **Top Stocks** - List of most mentioned stocks
✅ **LLM Monitor** - API call success rate

If you see "Loading..." or dashes (--), the bot is still collecting data. Wait 1-2 minutes.

---

## Troubleshooting

**Port already in use?**
```bash
# Use a different port - edit web_app.py line ~380:
app.run(port=8000)  # Change 5000 to 8000
```

**No data showing?**
1. Make sure bot is running: `python main.py --mode analyze`
2. Wait for first refresh (30 seconds)
3. Check MongoDB is running: `mongosh`

**Getting connection errors?**
1. Check MongoDB is running
2. Check bot has data: `mongosh` → `use reddit_trading` → `db.posts.count()`

---

## Next Steps

- **Read full guide:** See `WEB_APP_GUIDE.md`
- **Customize:** Edit colors in `static/css/style.css`
- **Deploy:** See deployment section in `WEB_APP_GUIDE.md`

---

## Running Both Together

```bash
# Terminal 1: Web Dashboard
python web_app.py

# Terminal 2: Bot Data Collection
python main.py --mode full

# Terminal 3: MongoDB (if needed)
mongosh
```

Open browser to http://localhost:5000 and watch real-time updates!

---

**Enjoy monitoring your trading bot! 📊**

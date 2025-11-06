# Reddit Trading Bot - Stock Sentiment Analysis

A comprehensive bot that pulls data from Reddit (specifically r/wallstreetbets and other subreddits), analyzes sentiment using LLM models (Deepseek), correlates sentiment with actual stock price movements, and identifies profitable trading patterns.

## Features

- **Reddit Data Collection**: Fetches posts and comments from specified subreddits
- **Stock Symbol Extraction**: Uses LLM to identify stock mentions in text
- **Sentiment Analysis**: Analyzes bullish/bearish sentiment for each stock using Deepseek LLM
- **Price Correlation**: Compares sentiment trends with actual stock price movements
- **Pattern Recognition**: Identifies tradeable patterns based on sentiment-price correlation
- **Trading Signals**: Generates buy/sell signals with confidence scores
- **MongoDB Storage**: Persists all data for analysis and historical tracking
- **Configurable Pipeline**: All parameters stored in config.json for easy adjustment

## Architecture

```
reddit_fetcher.py      → Collects data from Reddit API
        ↓
llm_processor.py       → Extracts symbols and analyzes sentiment
        ↓
database.py            → Stores in MongoDB
        ↓
stock_data_fetcher.py  → Fetches historical price data
        ↓
pattern_analyzer.py    → Correlates sentiment with prices
        ↓
main.py                → Orchestrates the full pipeline
```

## Prerequisites

### System Requirements
- Python 3.8+
- MongoDB 4.0+ (or MongoDB Atlas)
- 2GB+ RAM for comfortable operation

### API Keys Required

1. **Reddit API**
   - Create application at https://www.reddit.com/prefs/apps
   - Get: Client ID, Client Secret, User Agent

2. **Deepseek LLM API**
   - Sign up at https://deepseek.ai/
   - Get: API Key

3. **Stock Data (Optional)**
   - yfinance is used (free, no API key required)
   - Alternative: Alpha Vantage (requires API key)

## Installation

### 1. Clone/Setup Project

```bash
cd /home/biajee/Documents/code/ai_trading3/rddt_info
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Settings

Edit `config.json` and add your API credentials:

```json
{
  "reddit": {
    "client_id": "YOUR_REDDIT_CLIENT_ID",
    "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
    "user_agent": "RedditStockBot/1.0"
  },
  "mongodb": {
    "host": "mongodb://localhost:27017",
    "database": "reddit_trading"
  },
  "llm": {
    "api_key": "YOUR_DEEPSEEK_API_KEY",
    "model": "deepseek-chat"
  }
}
```

### 5. Setup MongoDB

**Local MongoDB:**
```bash
# macOS with Homebrew
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install -y mongodb
sudo systemctl start mongodb

# Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**MongoDB Atlas (Cloud):**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create cluster and get connection string
3. Update config.json: `"host": "mongodb+srv://username:password@cluster.mongodb.net"`

## Usage

### 1. Full Pipeline Execution

Fetch → Analyze → Process patterns in one command:

```bash
python main.py --mode full --subreddits wallstreetbets stocks investing
```

### 2. Individual Pipeline Stages

**Fetch Reddit data only:**
```bash
python main.py --mode fetch --subreddits wallstreetbets
```

**Analyze existing data:**
```bash
python main.py --mode analyze
```

**Analyze patterns for specific stocks:**
```bash
python main.py --mode patterns --stocks AAPL MSFT TSLA
```

**Generate trading signals:**
```bash
python main.py --mode signals --stocks GME AMC
```

### 3. Monitoring Execution

Logs are saved to `logs/trading_bot.log`:

```bash
tail -f logs/trading_bot.log
```

## Configuration Guide

### config.json Parameters

#### Reddit Section
```json
"reddit": {
  "client_id": "...",              # Reddit app client ID
  "client_secret": "...",          # Reddit app secret
  "user_agent": "...",             # Custom user agent
  "subreddits": [...],             # Default subreddits
  "limit_per_request": 100,        # Max posts per request
  "max_retries": 3,                # API retry attempts
  "request_timeout": 30            # Request timeout in seconds
}
```

#### LLM Section
```json
"llm": {
  "provider": "deepseek",          # LLM provider
  "api_key": "...",                # API key
  "base_url": "https://...",       # API endpoint
  "model": "deepseek-chat",        # Model name
  "temperature": 0.3,              # Response creativity (0-1)
  "max_tokens": 500,               # Max response length
  "timeout": 30                    # Request timeout
}
```

#### Pattern Analysis Section
```json
"pattern_analysis": {
  "min_mentions": 5,               # Min mentions for pattern
  "correlation_threshold": 0.6,    # Correlation strength threshold
  "window_days": 7,                # Analysis window size
  "price_change_threshold": 0.05   # Min price change %
}
```

#### Data Collection Section
```json
"data_collection": {
  "start_date": "2023-01-01",      # Historical data start
  "end_date": "2025-11-05",        # Data end date
  "batch_size": 50,                # Batch processing size
  "sleep_between_requests": 2      # Rate limit delay (seconds)
}
```

## Database Schema

### Collections

**reddit_posts**
```
{
  reddit_id: String,
  title: String,
  content: String,
  author: String,
  subreddit: String,
  created_utc: DateTime,
  score: Number,
  stock_mentions: [String],
  sentiments: Object
}
```

**sentiment_analysis**
```
{
  reddit_id: String,
  content_type: String (post/comment),
  stock_symbol: String,
  created_utc: DateTime,
  sentiments: {
    sentiment: String (BULLISH/NEUTRAL/BEARISH),
    score: Number (-1 to +1),
    reasoning: String
  }
}
```

**stock_prices**
```
{
  symbol: String,
  date: DateTime,
  open: Number,
  high: Number,
  low: Number,
  close: Number,
  volume: Number,
  sma_20, sma_50, sma_200, rsi, macd, ...
}
```

**trading_patterns**
```
{
  symbol: String,
  bullish_patterns: [...],
  bearish_patterns: [...],
  correlation_score: Number,
  summary: { ... }
}
```

## Examples

### Example 1: Monitor Wall Street Bets for Sentiment

```bash
python main.py --mode full --subreddits wallstreetbets --time-filter week
```

This will:
1. Fetch latest posts from r/wallstreetbets
2. Extract stock symbols and analyze sentiment
3. Pull historical price data for mentioned stocks
4. Identify patterns and generate signals

### Example 2: Deep Analysis of Specific Stocks

```bash
python main.py --mode patterns --stocks GME PLTR TSLA
```

This analyzes existing data for these 3 stocks and generates signals.

### Example 3: Fetch Historical Data (2-Year)

Modify config.json:
```json
"data_collection": {
  "start_date": "2023-01-01",
  "end_date": "2025-11-05"
}
```

Then run:
```bash
python main.py --mode fetch --subreddits wallstreetbets stocks investing
```

## Output & Analysis

### Viewing Results

**MongoDB Queries:**

```javascript
// Find all bullish signals for a stock
db.trading_patterns.find(
  { "symbol": "AAPL", "bullish_patterns": { $exists: true } }
)

// Get sentiment over time
db.sentiment_analysis.find(
  { "stock_symbol": "TSLA" }
).sort({ "created_utc": -1 })

// Find high confidence patterns
db.trading_patterns.find(
  { "summary.bullish_avg_confidence": { $gt: 0.7 } }
)
```

## Troubleshooting

### Issue: "Invalid Reddit credentials"
- Check client_id and client_secret in config.json
- Regenerate at https://www.reddit.com/prefs/apps

### Issue: "MongoDB connection failed"
- Ensure MongoDB is running: `sudo systemctl status mongodb`
- Check connection string in config.json
- For Atlas: ensure IP is whitelisted

### Issue: "LLM API error 401"
- Verify Deepseek API key is correct
- Check account has available credits
- Ensure API endpoint URL is correct

### Issue: "Rate limit exceeded"
- Increase `sleep_between_requests` in config.json
- Reduce `limit_per_request` value
- Consider using MongoDB Atlas for better performance

### Issue: "No stock symbols extracted"
- The LLM might be failing; check logs
- Add more symbols to `COMMON_SYMBOLS` in llm_processor.py
- Try simpler test text first

## Performance Tips

1. **Use MongoDB Atlas**: Faster than local MongoDB
2. **Batch Processing**: Process 50-100 posts at a time
3. **Selective Analysis**: Focus on high-volume stocks
4. **Index Usage**: Database automatically creates indexes
5. **Rate Limiting**: Respect Reddit API rate limits (1000 requests/10 min)

## Advanced Features

### Custom Stock Symbols

Edit `llm_processor.py` and add to `COMMON_SYMBOLS`:

```python
COMMON_SYMBOLS = {
    'AAPL', 'MSFT', 'YOUR_SYMBOL'
}
```

### Alternative LLM Provider

To use OpenAI instead of Deepseek:

```json
"llm": {
  "provider": "openai",
  "api_key": "sk-...",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo"
}
```

Then modify `llm_processor.py` API call logic.

### Custom Pattern Rules

Edit `pattern_analyzer.py` to add custom pattern detection logic.

## Disclaimer

This bot is for educational and research purposes. Trading based on sentiment analysis involves significant risk. Always conduct your own due diligence and consult financial advisors before making trading decisions.

## Support

For issues:
1. Check logs: `tail -f logs/trading_bot.log`
2. Review config.json for correct settings
3. Test individual components separately
4. Check GitHub issues for similar problems

## License

Educational use only. Modify and distribute as needed.

## Contributors

Created for advanced sentiment-driven trading analysis.

---

**Happy Trading! Remember: Past performance ≠ Future results 📈**

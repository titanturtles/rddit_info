# Project Structure

Complete overview of the Reddit Trading Bot project structure and file descriptions.

## Directory Layout

```
rddt_info/
├── config.json                 # Configuration file (API keys, parameters)
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
├── QUICKSTART.md               # Quick start guide
├── PROJECT_STRUCTURE.md        # This file
│
├── Core Modules
├── ├── config_loader.py        # Configuration management (singleton pattern)
├── ├── logger_setup.py         # Logging configuration
├── ├── database.py             # MongoDB connection & operations
├── ├── reddit_fetcher.py       # Reddit API data collection
├── ├── llm_processor.py        # LLM stock symbol & sentiment analysis
├── ├── stock_data_fetcher.py   # yfinance stock price fetching
├── ├── pattern_analyzer.py     # Sentiment-price correlation analysis
│
├── Main Scripts
├── ├── main.py                 # Main orchestration & CLI
├── ├── utils.py                # Utility functions & reporting
├── ├── test_example.py         # Component testing
│
└── Data Storage
    └── logs/
        └── trading_bot.log     # Application logs
```

## File Descriptions

### Configuration & Setup

#### `config.json`
- **Purpose**: Central configuration for all parameters
- **Content**:
  - Reddit API credentials
  - MongoDB connection settings
  - LLM provider configuration
  - Analysis parameters (thresholds, windows, etc.)
  - Logging settings
- **Usage**: Modified by `config_loader.py` via singleton pattern
- **Example**: See README.md for detailed configuration

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Packages**:
  - `praw` - Reddit API
  - `pymongo` - MongoDB
  - `openai/httpx` - LLM integration
  - `yfinance` - Stock data
  - `pandas/numpy` - Data processing
  - `python-dotenv` - Environment variables
- **Install**: `pip install -r requirements.txt`

### Core Modules

#### `config_loader.py`
- **Purpose**: Load and manage configuration
- **Key Classes**:
  - `ConfigLoader` - Singleton pattern for global config
- **Key Methods**:
  - `load_config()` - Load from JSON file
  - `get()` - Get value by dot-notation key
  - `update_value()` - Update config at runtime
  - `save_config()` - Save back to file
- **Usage**: `from config_loader import get_config; config = get_config()`

#### `logger_setup.py`
- **Purpose**: Configure application logging
- **Key Functions**:
  - `setup_logging()` - Initialize logging with file & console handlers
- **Features**:
  - Rotating file handler (10MB max)
  - Console output
  - Custom formatting with timestamps
  - Log level configuration
- **Usage**: `from logger_setup import setup_logging; setup_logging()`

#### `database.py`
- **Purpose**: MongoDB connection and data operations
- **Key Classes**:
  - `MongoDBConnection` - Manages DB operations
- **Key Methods**:
  - `connect()` - Establish connection
  - `insert_post()` - Save Reddit post
  - `insert_comment()` - Save Reddit comment
  - `insert_sentiment()` - Save sentiment analysis
  - `insert_stock_price()` - Save price data
  - `insert_pattern()` - Save pattern analysis
  - `get_sentiments_by_stock()` - Query by stock
  - `get_stock_prices()` - Query historical prices
- **Collections Created**:
  - `reddit_posts` - Reddit posts
  - `reddit_comments` - Reddit comments
  - `sentiment_analysis` - Sentiment results
  - `stock_prices` - Price data
  - `trading_patterns` - Pattern analysis
- **Indexes**: Automatically created for performance

#### `reddit_fetcher.py`
- **Purpose**: Fetch data from Reddit using PRAW
- **Key Classes**:
  - `RedditFetcher` - Reddit API wrapper
- **Key Methods**:
  - `_initialize_reddit()` - Initialize PRAW connection
  - `fetch_posts()` - Get posts from subreddit
  - `fetch_comments()` - Get comments
  - `save_posts_to_db()` - Save to MongoDB
  - `fetch_and_save_subreddit_data()` - Complete workflow
- **Features**:
  - Duplicate detection
  - Rate limiting
  - Error handling
  - Batch processing
- **Usage**: See main.py for examples

#### `llm_processor.py`
- **Purpose**: LLM operations for stock symbols and sentiment
- **Key Classes**:
  - `LLMProcessor` - LLM integration wrapper
- **Key Methods**:
  - `extract_stock_symbols()` - Find ticker symbols in text
  - `analyze_sentiment()` - Get BULLISH/BEARISH/NEUTRAL
  - `batch_analyze_posts()` - Analyze multiple posts
  - `batch_analyze_comments()` - Analyze multiple comments
- **Features**:
  - Pattern matching + LLM hybrid approach
  - Sentiment scoring (-1 to +1)
  - Fallback keyword analysis
  - Batch processing
- **Stock Symbols**: 50+ common symbols hardcoded, extensible
- **LLM Provider**: Deepseek by default, easily switchable

#### `stock_data_fetcher.py`
- **Purpose**: Fetch and process stock price data
- **Key Classes**:
  - `StockDataFetcher` - yfinance wrapper
- **Key Methods**:
  - `fetch_stock_data()` - Get historical OHLCV
  - `calculate_indicators()` - Add technical indicators
  - `save_stock_data_to_db()` - Persist to MongoDB
  - `get_price_change()` - Calculate returns
  - `compare_prices_with_sentiment()` - Correlation analysis
- **Indicators Supported**:
  - SMA (20, 50, 200-day)
  - RSI (Relative Strength Index)
  - MACD
  - Bollinger Bands
- **Features**:
  - Configurable lookback period
  - Automatic indicator calculation
  - Correlation analysis
  - Error handling

#### `pattern_analyzer.py`
- **Purpose**: Identify profitable trading patterns
- **Key Classes**:
  - `PatternAnalyzer` - Pattern detection engine
- **Key Methods**:
  - `find_tradeable_patterns()` - Analyze single stock
  - `identify_correlated_stocks()` - Find best opportunities
  - `generate_trading_signals()` - Create buy/sell signals
  - `save_pattern_analysis()` - Store results
- **Pattern Types**:
  - Bullish patterns (high sentiment + rising price)
  - Bearish patterns (low sentiment + falling price)
  - Neutral patterns
- **Metrics**:
  - Correlation score
  - Confidence level
  - Expected return %
- **Thresholds**:
  - Min mentions: 5
  - Correlation: 0.6
  - Window: 7 days
  - Price change: 5%

### Main Scripts

#### `main.py`
- **Purpose**: Main orchestration and CLI
- **Key Classes**:
  - `RedditTradingBot` - Main bot logic
- **Modes**:
  - `full` - Complete pipeline
  - `fetch` - Get Reddit data only
  - `analyze` - Process content
  - `patterns` - Pattern analysis
  - `signals` - Generate signals
- **Key Methods**:
  - `initialize()` - Setup components
  - `fetch_reddit_data()` - Get posts/comments
  - `analyze_reddit_content()` - LLM analysis
  - `fetch_stock_data()` - Get prices
  - `analyze_patterns()` - Pattern detection
  - `run_full_pipeline()` - End-to-end
- **CLI Arguments**:
  - `--mode` - Execution mode
  - `--subreddits` - Reddit communities
  - `--stocks` - Stock symbols
  - `--time-filter` - Time range
- **Usage Examples**:
  ```bash
  python main.py --mode full
  python main.py --mode fetch --subreddits wallstreetbets
  python main.py --mode patterns --stocks AAPL MSFT
  ```

#### `utils.py`
- **Purpose**: Utility functions for analysis and reporting
- **Key Classes**:
  - `DataAnalyzer` - Analysis and reporting
- **Key Methods**:
  - `get_sentiment_summary()` - Stock sentiment stats
  - `get_top_mentioned_stocks()` - Most discussed stocks
  - `get_price_performance()` - Price metrics
  - `compare_sentiment_vs_price()` - Correlation analysis
  - `generate_report()` - Comprehensive analysis
  - `export_report_json()` - JSON export
  - `export_report_csv()` - CSV export
- **Convenience Functions**:
  - `print_sentiment_summary()` - Console output
  - `print_top_stocks()` - Console output

#### `test_example.py`
- **Purpose**: Component testing and examples
- **Key Functions**:
  - `test_config_loading()` - Config test
  - `test_database_connection()` - MongoDB test
  - `test_llm_stock_extraction()` - Symbol extraction test
  - `test_sentiment_analysis()` - Sentiment test
  - `test_stock_data_fetch()` - Price data test
  - `test_database_queries()` - Query test
  - `test_data_analysis()` - Analysis test
  - `test_all_components()` - Run all tests
- **Usage**: `python test_example.py`
- **Output**: Test summary with pass/fail status

## Data Flow

```
Reddit Posts/Comments
        ↓
    reddit_fetcher.py
        ↓
    MongoDB (posts/comments)
        ↓
    llm_processor.py
        ↓
    MongoDB (stock_mentions)
        ↓
    llm_processor.py (sentiment)
        ↓
    MongoDB (sentiment_analysis)
        ↓
    stock_data_fetcher.py
        ↓
    MongoDB (stock_prices)
        ↓
    pattern_analyzer.py
        ↓
    MongoDB (trading_patterns)
        ↓
    utils.py (reporting)
        ↓
    Reports/Signals
```

## Configuration Hierarchy

```
config.json (file)
    ↓
ConfigLoader (singleton)
    ↓
All modules (access via get_config())
```

## Database Schema Summary

### Collections & Indexes

**reddit_posts**
- Indexes: created_utc, subreddit, author, reddit_id (unique)
- Documents: ~100-1000 per run

**reddit_comments**
- Indexes: created_utc, author, reddit_id (unique)
- Documents: ~100-500 per run

**sentiment_analysis**
- Indexes: reddit_id, stock_symbol, analyzed_date
- Documents: ~500-5000 per run

**stock_prices**
- Indexes: symbol+date, symbol
- Documents: ~500-10000 (365 days × symbols)

**trading_patterns**
- Indexes: stock_symbol, correlation_score
- Documents: ~10-100 per run

## Execution Phases

### Phase 1: Data Collection
- `reddit_fetcher.py` collects posts/comments
- Stored in `reddit_posts` / `reddit_comments`

### Phase 2: Content Analysis
- `llm_processor.py` extracts stock symbols
- Analyzes sentiment for each stock mention
- Results in `sentiment_analysis` collection

### Phase 3: Price Data Fetch
- `stock_data_fetcher.py` gets historical prices
- Calculates technical indicators
- Stores in `stock_prices` collection

### Phase 4: Pattern Analysis
- `pattern_analyzer.py` correlates sentiment with prices
- Identifies profitable patterns
- Generates trading signals
- Results in `trading_patterns` collection

### Phase 5: Reporting
- `utils.py` generates comprehensive reports
- Exports to JSON/CSV
- Displays summary statistics

## Dependencies Between Modules

```
config_loader.py ← All modules depend on this
    ├── database.py
    ├── reddit_fetcher.py
    ├── llm_processor.py
    ├── stock_data_fetcher.py
    ├── pattern_analyzer.py
    └── logger_setup.py

reddit_fetcher.py → database.py
    └── main.py

llm_processor.py → database.py
    └── main.py

stock_data_fetcher.py → database.py
    └── main.py

pattern_analyzer.py → database.py
    └── main.py

database.py ← mongodb (external)

utils.py → database.py
```

## Error Handling

- Each module has try-catch blocks
- Errors logged with full context
- Graceful degradation (continue on partial failures)
- Duplicate detection prevents redundant storage
- Rate limiting prevents API blocks

## Logging Structure

```
logs/trading_bot.log (rotating, 10MB max, 5 backups)

Format: YYYY-MM-DD HH:MM:SS - MODULE - LEVEL - MESSAGE

Levels:
  - DEBUG: Detailed information
  - INFO: General information
  - WARNING: Warning messages
  - ERROR: Error messages
  - CRITICAL: Critical errors
```

## Security Considerations

- API keys stored in config.json (not in code)
- Reddit credentials never logged
- MongoDB credentials configurable
- No sensitive data printed to console
- Use environment variables for production

## Performance Characteristics

- Fetch 100 posts: ~30 seconds
- Analyze 100 posts: ~60 seconds (depends on LLM)
- Fetch 30-day prices (50 stocks): ~20 seconds
- Pattern analysis (50 stocks): ~10 seconds
- Full pipeline: ~5-10 minutes depending on volume

## Extension Points

1. **Add LLM Providers**: Modify `llm_processor.py` `_call_llm()`
2. **Add Stock Symbols**: Extend `COMMON_SYMBOLS` in `llm_processor.py`
3. **Custom Indicators**: Add to `stock_data_fetcher.py` `calculate_indicators()`
4. **Pattern Rules**: Modify `pattern_analyzer.py` logic
5. **Export Formats**: Add methods to `utils.py` DataAnalyzer

---

This structure provides a scalable, maintainable foundation for sentiment-driven trading analysis.

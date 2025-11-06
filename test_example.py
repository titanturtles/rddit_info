"""
Example script demonstrating bot functionality
Test different components without full pipeline
"""

import logging
from datetime import datetime
from config_loader import get_config
from logger_setup import setup_logging
from database import MongoDBConnection
from llm_processor import LLMProcessor
from stock_data_fetcher import StockDataFetcher
from utils import DataAnalyzer, print_top_stocks, print_sentiment_summary

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def test_config_loading():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("TEST 1: Configuration Loading")
    print("="*60)

    try:
        config = get_config()
        print("✓ Config loaded successfully")
        print(f"  - Reddit subreddits: {config.get('reddit.subreddits')}")
        print(f"  - MongoDB host: {config.get('mongodb.host')}")
        print(f"  - LLM provider: {config.get('llm.provider')}")
        return True
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return False


def test_database_connection():
    """Test MongoDB connection"""
    print("\n" + "="*60)
    print("TEST 2: Database Connection")
    print("="*60)

    try:
        db = MongoDBConnection()
        print("✓ MongoDB connection successful")
        print(f"  - Database: {db.db.name}")
        print(f"  - Collections: {list(db.collections.keys())}")
        db.close()
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("  Make sure MongoDB is running!")
        return False


def test_llm_stock_extraction():
    """Test stock symbol extraction"""
    print("\n" + "="*60)
    print("TEST 3: Stock Symbol Extraction")
    print("="*60)

    test_texts = [
        "I just bought 100 shares of AAPL at $150. Diamond hands! 💎",
        "TSLA is going to the moon! Much better than GME.",
        "Just sold my position in Microsoft (MSFT). Taking profits.",
        "PLTR, COIN, and NFLX are all looking bullish right now."
    ]

    try:
        llm = LLMProcessor()
        print("✓ LLM processor initialized")

        for i, text in enumerate(test_texts, 1):
            symbols = llm.extract_stock_symbols(text)
            print(f"\n  Text {i}: \"{text[:50]}...\"")
            print(f"  Symbols found: {symbols if symbols else 'None'}")

        return True
    except Exception as e:
        print(f"✗ Stock extraction failed: {e}")
        return False


def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("\n" + "="*60)
    print("TEST 4: Sentiment Analysis")
    print("="*60)

    test_cases = [
        ("AAPL", "Apple is overvalued and heading for a crash. Bad earnings expected."),
        ("TSLA", "Tesla is the future! Elon is a genius. TSLA to the moon! 🚀🚀🚀"),
        ("GME", "GameStop is a meme stock. Could go either way honestly."),
    ]

    try:
        llm = LLMProcessor()
        print("✓ LLM processor initialized")

        for symbol, text in test_cases:
            sentiment = llm.analyze_sentiment(text, [symbol])
            print(f"\n  Stock: {symbol}")
            print(f"  Text: \"{text[:60]}...\"")
            print(f"  Sentiment: {sentiment['sentiment']}")
            print(f"  Score: {sentiment['score']:.2f}")
            print(f"  Reasoning: {sentiment['reasoning'][:50]}...")

        return True
    except Exception as e:
        print(f"✗ Sentiment analysis failed: {e}")
        return False


def test_stock_data_fetch():
    """Test stock price data fetching"""
    print("\n" + "="*60)
    print("TEST 5: Stock Price Data Fetching")
    print("="*60)

    symbols = ['AAPL', 'MSFT', 'TSLA']

    try:
        fetcher = StockDataFetcher()
        print("✓ Stock data fetcher initialized")

        for symbol in symbols:
            print(f"\n  Fetching {symbol}...")
            data = fetcher.fetch_stock_data(symbol)

            if data is not None and not data.empty:
                print(f"  ✓ Retrieved {len(data)} records")
                print(f"    Current price: ${data['Close'].iloc[-1]:.2f}")
                print(f"    52-week high: ${data['High'].max():.2f}")
                print(f"    52-week low: ${data['Low'].min():.2f}")
            else:
                print(f"  ✗ No data found for {symbol}")

        fetcher.close()
        return True
    except Exception as e:
        print(f"✗ Stock data fetch failed: {e}")
        return False


def test_database_queries():
    """Test database queries"""
    print("\n" + "="*60)
    print("TEST 6: Database Queries")
    print("="*60)

    try:
        db = MongoDBConnection()

        # Check posts
        posts_col = db.collections.get('posts')
        if posts_col is not None:
            post_count = posts_col.count_documents({})
            print(f"✓ Posts in database: {post_count}")

        # Check sentiments
        sentiment_col = db.collections.get('sentiment_analysis')
        if sentiment_col is not None:
            sentiment_count = sentiment_col.count_documents({})
            print(f"✓ Sentiments in database: {sentiment_count}")

            if sentiment_count > 0:
                stocks = sentiment_col.distinct('stock_symbol')
                print(f"  - Stocks analyzed: {len(stocks)}")
                if stocks:
                    print(f"  - Examples: {stocks[:5]}")

        # Check prices
        prices_col = db.collections.get('stock_prices')
        if prices_col is not None:
            price_count = prices_col.count_documents({})
            print(f"✓ Price records in database: {price_count}")

        db.close()
        return True
    except Exception as e:
        print(f"✗ Database queries failed: {e}")
        return False


def test_data_analysis():
    """Test data analysis utilities"""
    print("\n" + "="*60)
    print("TEST 7: Data Analysis Utilities")
    print("="*60)

    try:
        analyzer = DataAnalyzer()

        # Get top stocks
        top_stocks = analyzer.get_top_mentioned_stocks(limit=5, days=30)
        if top_stocks:
            print("✓ Top mentioned stocks:")
            for stock in top_stocks:
                print(f"  - {stock['symbol']}: {stock['mentions']} mentions "
                      f"({stock['bullish_ratio']*100:.0f}% bullish)")
        else:
            print("⊘ No data available yet")

        analyzer.close()
        return True
    except Exception as e:
        print(f"✗ Data analysis failed: {e}")
        return False


def test_all_components():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# REDDIT TRADING BOT - COMPONENT TEST SUITE")
    print("#"*60)

    tests = [
        ("Configuration", test_config_loading),
        ("Database Connection", test_database_connection),
        ("LLM Stock Extraction", test_llm_stock_extraction),
        ("Sentiment Analysis", test_sentiment_analysis),
        ("Stock Data Fetching", test_stock_data_fetch),
        ("Database Queries", test_database_queries),
        ("Data Analysis", test_data_analysis),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Bot is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs for details.")

    print("#"*60 + "\n")


if __name__ == '__main__':
    test_all_components()

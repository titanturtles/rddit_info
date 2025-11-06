"""
Comprehensive setup test WITHOUT yfinance
Tests all components except stock data fetching
Useful when yfinance connectivity is problematic
"""

import sys
import logging
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def test_config():
    """Test configuration loading"""
    print("\n" + "="*70)
    print("TEST 1: Configuration Loading")
    print("="*70 + "\n")

    try:
        from config_loader import get_config
        config = get_config()

        print("✓ Config loaded successfully")
        print(f"  - Reddit subreddits: {config.get('reddit.subreddits')}")
        print(f"  - MongoDB host: {config.get('mongodb.host')}")
        print(f"  - LLM provider: {config.get('llm.provider')}")
        print()
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        print()
        return False


def test_mongodb():
    """Test MongoDB connection"""
    print("\n" + "="*70)
    print("TEST 2: MongoDB Connection")
    print("="*70 + "\n")

    try:
        from config_loader import get_config
        from pymongo import MongoClient

        config = get_config()
        mongo_config = config.get_section('mongodb')
        host = mongo_config.get('host', 'mongodb://localhost:27017')

        print(f"Connecting to: {host}")
        client = MongoClient(host, serverSelectionTimeoutMS=5000)

        # Test ping
        client.admin.command('ping')
        print("✓ MongoDB connection successful")

        # Get database
        db_name = mongo_config.get('database', 'reddit_trading')
        db = client[db_name]
        print(f"✓ Database accessed: {db_name}")

        # List collections
        collections = db.list_collection_names()
        print(f"✓ Collections available: {len(collections)}")
        if collections:
            for col in collections:
                print(f"  - {col}")

        client.close()
        print()
        return True
    except Exception as e:
        print(f"✗ MongoDB test failed: {e}")
        print()
        print("Make sure MongoDB is running:")
        print("  - Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        print("  - Local: sudo systemctl start mongodb")
        print("  - macOS: brew services start mongodb-community")
        print()
        return False


def test_database_module():
    """Test database module"""
    print("\n" + "="*70)
    print("TEST 3: Database Module")
    print("="*70 + "\n")

    try:
        from database import MongoDBConnection

        print("Initializing database connection...")
        db = MongoDBConnection()

        print("✓ Database connection successful")
        print(f"  - Database: {db.db.name}")
        print(f"  - Collections: {list(db.collections.keys())}")

        db.close()
        print()
        return True
    except Exception as e:
        print(f"✗ Database module test failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        return False


def test_reddit_api():
    """Test Reddit API"""
    print("\n" + "="*70)
    print("TEST 4: Reddit API Connection")
    print("="*70 + "\n")

    try:
        from config_loader import get_config
        import praw

        config = get_config()
        reddit_config = config.get_section('reddit')

        client_id = reddit_config.get('client_id')
        client_secret = reddit_config.get('client_secret')

        # Check if credentials are set
        if client_id == "YOUR_REDDIT_CLIENT_ID":
            print("✗ Reddit credentials not configured!")
            print("  Edit config.json and add your Reddit API credentials")
            print()
            return False

        print("Initializing Reddit connection...")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=reddit_config.get('user_agent', 'RedditStockBot/1.0')
        )

        print("Testing authentication...")
        user = reddit.user.me()
        print(f"✓ Reddit API connection successful")
        print(f"  - User: {user}")

        print()
        return True
    except Exception as e:
        print(f"✗ Reddit API test failed: {e}")
        print()
        print("Troubleshooting:")
        print("  - Check Reddit credentials in config.json")
        print("  - Verify PRAW is installed: pip install praw")
        print("  - Check internet connection")
        print()
        return False


def test_llm_processor():
    """Test LLM processor"""
    print("\n" + "="*70)
    print("TEST 5: LLM Processor")
    print("="*70 + "\n")

    try:
        from llm_processor import LLMProcessor

        print("Initializing LLM processor...")
        llm = LLMProcessor()

        print("✓ LLM processor initialized")
        print(f"  - Provider: {llm.llm_config.get('provider')}")
        print(f"  - Model: {llm.model}")

        # Test stock symbol extraction
        test_text = "I just bought $AAPL and $TSLA at $150 and $250 respectively"
        symbols = llm.extract_stock_symbols(test_text)
        print(f"✓ Stock symbol extraction works")
        print(f"  - Text: '{test_text}'")
        print(f"  - Symbols found: {symbols}")

        print()
        return True
    except Exception as e:
        print(f"✗ LLM processor test failed: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        return False


def test_yfinance_skipped():
    """Skip yfinance test"""
    print("\n" + "="*70)
    print("TEST 6: Stock Data (SKIPPED)")
    print("="*70 + "\n")

    print("⊘ Yfinance test skipped (connectivity issues)")
    print()
    print("If you need stock data:")
    print("  1. Run: python test_connectivity.py")
    print("  2. Follow the diagnostic steps")
    print("  3. Retry: python test_yfinance.py")
    print()
    print("Workaround: Use mock data for testing")
    print("  - Set environment variable: MOCK_STOCK_DATA=1")
    print("  - Or edit config.json to use alternative provider")
    print()

    return None  # Not counting as pass/fail


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("#"*70)
    print("# REDDIT TRADING BOT - SETUP TEST (WITHOUT YFINANCE)")
    print("#"*70)

    tests = [
        ("Configuration", test_config),
        ("MongoDB", test_mongodb),
        ("Database Module", test_database_module),
        ("Reddit API", test_reddit_api),
        ("LLM Processor", test_llm_processor),
        ("Stock Data", test_yfinance_skipped),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "#"*70)
    print("# TEST SUMMARY")
    print("#"*70 + "\n")

    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)

    for test_name, result in results.items():
        if result is None:
            status = "⊘ SKIP"
        elif result:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Your core setup is complete!")
        print("\nNext steps:")
        print("  1. Fix yfinance connectivity (see test_connectivity.py)")
        print("  2. python main.py --mode full")
        print("  3. Check logs/trading_bot.log for output")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        print("\nNote: Stock data fetching (yfinance) is currently unavailable.")
        print("You can still test the other components.")

    print("\n" + "#"*70 + "\n")

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

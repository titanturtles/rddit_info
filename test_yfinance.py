"""
Test script for yfinance stock data fetching
Diagnoses issues with fetching stock price data
"""

import logging
from datetime import datetime, timedelta
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def test_yfinance_basic():
    """Test basic yfinance functionality"""

    print("\n" + "="*70)
    print("TESTING YFINANCE - BASIC FUNCTIONALITY")
    print("="*70 + "\n")

    try:
        print("1. Importing yfinance...")
        import yfinance as yf
        print("   ✓ yfinance imported successfully")
        print(f"   - Version: {yf.__version__ if hasattr(yf, '__version__') else 'unknown'}")
        print()

        print("2. Testing internet connection...")
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            print("   ✓ Internet connection available")
        except OSError:
            print("   ✗ No internet connection detected!")
            return False

        print()

        print("3. Fetching AAPL data (1 day)...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            ticker = yf.Ticker("AAPL")
            print(f"   ✓ Ticker object created for AAPL")

            print(f"start_date: {start_date.date()}, end_date: {end_date.date()}")

            # print(ticker.history(period='1mo'))
            # print(ticker.history(start="2024-11-01", end="2024-11-03", interval="1d", repair=True))

            # Try to get historical data
            # df = ticker.history(start="2024-11-01", end="2024-11-03", repair=True)
            df = ticker.history(start="2025-11-01", end=end_date.date(), interval="1d", repair=True)

            print(f"df head:\n{df}")
            if df is not None and not df.empty:
                print(f"   ✓ Data retrieved successfully!")
                print(f"   - Records: {len(df)}")
                if len(df) > 0:
                    latest = df.iloc[-1]
                    print(f"   - Latest close: ${latest['Close']:.2f}")
                    print(f"   - Latest high: ${latest['High']:.2f}")
                    print(f"   - Latest low: ${latest['Low']:.2f}")
                    print(f"   - Volume: {int(latest['Volume'])}")
            else:
                print("   ✗ No data returned (DataFrame is empty)")
                return False

        except Exception as e:
            print(f"   ✗ Failed to fetch AAPL data: {e}")
            import traceback
            traceback.print_exc()
            return False

        print()

        print("4. Fetching multiple stocks...")
        symbols = ["AAPL", "MSFT", "TSLA"]

        for symbol in symbols:
            try:
                print(f"\n   Fetching {symbol}...")
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date)

                if df is not None and not df.empty and len(df) > 0:
                    print(f"   ✓ {symbol}: {len(df)} records, ${df['Close'].iloc[-1]:.2f}")
                else:
                    print(f"   ✗ {symbol}: No data")
            except Exception as e:
                print(f"   ✗ {symbol}: {e}")

        print()
        print("="*70)
        print("✅ YFINANCE TEST COMPLETED")
        print("="*70)
        print()

        return True

    except Exception as e:
        print("="*70)
        print("❌ YFINANCE TEST FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()

        import traceback
        traceback.print_exc()

        print()
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("     - ping yahoo.com")
        print()
        print("  2. Verify yfinance is installed:")
        print("     - pip install --upgrade yfinance")
        print()
        print("  3. Check if Yahoo Finance is accessible:")
        print("     - Try accessing: https://finance.yahoo.com")
        print()
        print("  4. Try clearing cache:")
        print("     - pip install --force-reinstall yfinance")
        print()
        print("  5. Network/Firewall issues:")
        print("     - Ensure no firewall blocking Yahoo Finance")
        print("     - Try using a VPN")
        print()

        return False


def test_yfinance_with_config():
    """Test yfinance with StockDataFetcher from the bot"""

    print("\n" + "="*70)
    print("TESTING STOCK DATA FETCHER MODULE")
    print("="*70 + "\n")

    try:
        from stock_data_fetcher import StockDataFetcher

        print("1. Initializing StockDataFetcher...")
        fetcher = StockDataFetcher()
        print("   ✓ StockDataFetcher initialized")
        print()

        print("2. Fetching historical data for AAPL...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        df = fetcher.fetch_stock_data("AAPL", start_date, end_date)

        if df is not None and not df.empty:
            print(f"   ✓ Data retrieved: {len(df)} records")
            print(f"   - Columns: {list(df.columns)}")
            print(f"   - Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"   - Current price: ${df['Close'].iloc[-1]:.2f}")
        else:
            print("   ✗ No data returned")
            fetcher.close()
            return False

        print()

        print("3. Calculating technical indicators...")
        df_with_indicators = fetcher.calculate_indicators(df)
        print(f"   ✓ Indicators calculated")
        print(f"   - New columns: {[c for c in df_with_indicators.columns if c not in df.columns]}")

        print()

        print("4. Testing price change calculation...")
        price_change = fetcher.get_price_change("AAPL", days=7)

        if price_change:
            print(f"   ✓ Price change calculated:")
            print(f"   - 7-day change: {price_change['percent_change']:.2f}%")
            print(f"   - Start price: ${price_change['start_price']:.2f}")
            print(f"   - End price: ${price_change['end_price']:.2f}")
        else:
            print("   ✗ Price change calculation failed")
            fetcher.close()
            return False

        fetcher.close()
        print()
        print("="*70)
        print("✅ STOCK DATA FETCHER TEST SUCCESSFUL")
        print("="*70)
        print()

        return True

    except Exception as e:
        print("="*70)
        print("❌ STOCK DATA FETCHER TEST FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()

        import traceback
        traceback.print_exc()

        print()
        return False


def test_alternative_data_sources():
    """Test alternative data sources"""

    print("\n" + "="*70)
    print("TESTING ALTERNATIVE DATA SOURCES")
    print("="*70 + "\n")

    print("Alternative stock data sources you can use:")
    print()

    print("1. Alpha Vantage (free tier available)")
    print("   - Website: https://www.alphavantage.co/")
    print("   - Pros: Free API key, reliable")
    print("   - Cons: Rate limited (5 calls/min free tier)")
    print()

    print("2. IEX Cloud (free tier available)")
    print("   - Website: https://iexcloud.io/")
    print("   - Pros: Good data quality")
    print("   - Cons: Limited free tier")
    print()

    print("3. Finnhub (free tier available)")
    print("   - Website: https://finnhub.io/")
    print("   - Pros: Comprehensive data, good free tier")
    print("   - Cons: Some features require paid plan")
    print()

    print("4. Polygon.io (free tier available)")
    print("   - Website: https://polygon.io/")
    print("   - Pros: Real-time data")
    print("   - Cons: Paid plans for most features")
    print()

    print("Note: yfinance is the easiest to use. Most issues are temporary")
    print("and resolve by retrying after a few minutes.")
    print()


def main():
    """Run all yfinance tests"""
    print("\n")
    print("#"*70)
    print("# YFINANCE DIAGNOSTIC TEST")
    print("#"*70)

    # Test basic yfinance
    basic_pass = test_yfinance_basic()

    # Test with module
    if basic_pass:
        module_pass = test_yfinance_with_config()
    else:
        print("\nSkipping module test due to basic test failure")
        module_pass = False

    # Show alternatives
    test_alternative_data_sources()

    # Summary
    print("\n" + "#"*70)
    print("# TEST SUMMARY")
    print("#"*70 + "\n")

    if basic_pass and module_pass:
        print("✓ All yfinance tests PASSED")
        print("\nYour stock data fetching is working correctly!")
        return True
    else:
        print("✗ Some tests FAILED")
        print("\nCommon solutions:")
        print("  1. Wait a few minutes and try again (rate limiting)")
        print("  2. Restart your Python environment")
        print("  3. Reinstall yfinance: pip install --upgrade yfinance")
        print("  4. Check your internet connection")
        print("  5. Try from a different network/VPN")
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

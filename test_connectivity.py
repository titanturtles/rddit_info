"""
Test internet connectivity and yfinance availability
"""

import sys
import logging
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def test_basic_internet():
    """Test basic internet connectivity"""

    print("\n" + "="*70)
    print("TEST 1: Basic Internet Connectivity")
    print("="*70 + "\n")

    try:
        import socket

        print("Testing DNS resolution...")
        try:
            socket.getaddrinfo("8.8.8.8", 53)
            print("✓ DNS resolution works")
        except Exception as e:
            print(f"✗ DNS failed: {e}")
            return False

        print("\nTesting connection to Google DNS...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.connect(("8.8.8.8", 53))
            sock.close()
            print("✓ Can reach Google DNS (8.8.8.8:53)")
        except Exception as e:
            print(f"✗ Cannot reach Google DNS: {e}")
            return False

        print("\nTesting connection to Yahoo Finance...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            sock.connect(("query1.finance.yahoo.com", 443))
            sock.close()
            print("✓ Can reach Yahoo Finance")
        except Exception as e:
            print(f"✗ Cannot reach Yahoo Finance: {e}")
            print("  → This is the problem!")
            return False

        print("\n✓ All basic connectivity tests passed")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_http_request():
    """Test HTTP requests to Yahoo Finance"""

    print("\n" + "="*70)
    print("TEST 2: HTTP Request to Yahoo Finance")
    print("="*70 + "\n")

    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        print("Creating session with retries...")
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        print("Testing connection to query1.finance.yahoo.com...")

        try:
            response = session.get(
                "https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            print(f"HTTP Status: {response.status_code}")

            if response.status_code == 200:
                print("✓ Got 200 response")
                data = response.json()
                if data and 'quoteResponse' in data:
                    print("✓ Got valid JSON response")
                    return True
            else:
                print(f"✗ Got status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"✗ Request failed: {e}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Install: pip install requests urllib3")
        return False


def test_yfinance_direct():
    """Test yfinance directly with different approaches"""

    print("\n" + "="*70)
    print("TEST 3: Yfinance Direct Test")
    print("="*70 + "\n")

    try:
        import yfinance as yf
        from datetime import datetime, timedelta

        print(f"Yfinance version: {yf.__version__ if hasattr(yf, '__version__') else 'unknown'}")
        print()

        # Try different approaches
        approaches = [
            ("Approach 1: Default (may be slow)", lambda: yf.Ticker("AAPL").history(period="1d")),
            ("Approach 2: Specify dates", lambda: yf.Ticker("AAPL").history(start="2025-11-04", end="2025-11-05")),
            ("Approach 3: Use yfinance.download", lambda: yf.download("AAPL", start="2025-11-04", end="2025-11-05", progress=False)),
        ]

        for approach_name, fetch_func in approaches:
            try:
                print(f"Trying: {approach_name}...")
                df = fetch_func()

                if df is not None and not df.empty:
                    print(f"  ✓ Success! Got {len(df)} records")
                    if len(df) > 0:
                        print(f"    Latest close: ${df['Close'].iloc[-1]:.2f}")
                    return True
                else:
                    print(f"  ✗ No data returned")

            except Exception as e:
                print(f"  ✗ Failed: {str(e)[:100]}")

        print("\n✗ All approaches failed")
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_with_mock_data():
    """Test with mock/cached data"""

    print("\n" + "="*70)
    print("TEST 4: Mock Data Fallback")
    print("="*70 + "\n")

    try:
        import pandas as pd
        from datetime import datetime, timedelta
        import numpy as np

        print("Creating mock historical data for AAPL...")

        dates = pd.date_range(end=datetime.now(), periods=30)
        prices = np.random.normal(150, 10, 30)

        df = pd.DataFrame({
            'Open': prices + np.random.normal(0, 2, 30),
            'High': prices + abs(np.random.normal(3, 1, 30)),
            'Low': prices - abs(np.random.normal(3, 1, 30)),
            'Close': prices,
            'Volume': np.random.randint(50000000, 100000000, 30),
        }, index=dates)

        if df is not None and not df.empty:
            print(f"✓ Mock data created: {len(df)} records")
            print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"  Sample close prices:")
            for i in [0, len(df)//2, -1]:
                print(f"    {df.index[i].date()}: ${df['Close'].iloc[i]:.2f}")
            return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def diagnose_firewall():
    """Diagnose firewall/network issues"""

    print("\n" + "="*70)
    print("FIREWALL/NETWORK DIAGNOSTICS")
    print("="*70 + "\n")

    print("If tests fail, check:")
    print()
    print("1. Corporate Firewall/Proxy:")
    print("   - Are you behind a corporate proxy?")
    print("   - Set proxy: pip install pysocks")
    print("   - Or check with IT department")
    print()

    print("2. DNS Issues:")
    print("   - Try: nslookup query1.finance.yahoo.com")
    print("   - Try: nslookup 8.8.8.8")
    print()

    print("3. ISP/Network:")
    print("   - Try: ping yahoo.com")
    print("   - Try different network (phone hotspot)")
    print("   - Try VPN")
    print()

    print("4. Firewall Rules:")
    print("   - Check if yahoo.com is blocked")
    print("   - Check if HTTPS is allowed")
    print("   - Try: curl -I https://query1.finance.yahoo.com")
    print()

    print("5. VPN Solution:")
    print("   - If behind firewall, use VPN:")
    print("   - pip install pysocks")
    print("   - Or use ProtonVPN, ExpressVPN, etc.")
    print()


def main():
    """Run all connectivity tests"""

    print("\n")
    print("#"*70)
    print("# YFINANCE CONNECTIVITY DIAGNOSTIC")
    print("#"*70)

    tests = [
        ("Basic Internet", test_basic_internet),
        ("HTTP Request", test_http_request),
        ("Yfinance Direct", test_yfinance_direct),
        ("Mock Data", test_with_mock_data),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results[test_name] = False

    # Diagnostics
    diagnose_firewall()

    # Summary
    print("\n" + "#"*70)
    print("# SUMMARY")
    print("#"*70 + "\n")

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print()

    if results["Mock Data"]:
        print("✓ Mock data works - you can use test data while fixing connectivity")

    if not results["Yfinance Direct"] and results["Basic Internet"]:
        print("\n⚠️  Internet works but yfinance fails:")
        print("  1. Yfinance API might be having issues")
        print("  2. Wait 5-10 minutes and try again")
        print("  3. Upgrade yfinance: pip install --upgrade yfinance")
        print("  4. Check: https://status.yahoo.com")

    if not results["Basic Internet"]:
        print("\n❌ Basic internet connectivity failed:")
        print("  1. Check your internet connection")
        print("  2. Try: ping 8.8.8.8")
        print("  3. Check firewall/proxy settings")
        print("  4. Contact IT if behind corporate firewall")

    print("\n" + "#"*70 + "\n")

    return all(results.values())


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

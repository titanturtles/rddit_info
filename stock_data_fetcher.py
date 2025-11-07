"""
Stock price data fetcher using yfinance
Retrieves historical price data and technical indicators
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from config_loader import get_config
from database import MongoDBConnection

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetches stock price data and technical indicators"""

    def __init__(self):
        """Initialize stock data fetcher"""
        self.config = get_config()
        self.stock_config = self.config.get_section('stock_data')
        self.db = MongoDBConnection()

    def fetch_stock_data(self, symbol: str, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None, max_retries: int = 3) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock price data

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_date: Start date for historical data
            end_date: End date for historical data
            max_retries: Maximum number of retry attempts

        Returns:
            DataFrame with OHLCV data or None if error
        """
        import time

        if not end_date:
            end_date = datetime.now()

        if not start_date:
            lookback_days = self.stock_config.get('lookback_days', 365)
            start_date = end_date - timedelta(days=lookback_days)

        for attempt in range(max_retries):
            try:
                logger.info("=" * 80)
                logger.info(f"[YFINANCE REQUEST] Fetching {symbol.upper()} price data")
                logger.info(f"[PARAMS] start_date={start_date.date()}, end_date={end_date.date()}, interval=1h")
                logger.info(f"[ATTEMPT] {attempt+1}/{max_retries}")
                logger.info("=" * 80)

                ticker = yf.Ticker(symbol.upper())
                logger.debug(f"[YFINANCE] Ticker object created for {symbol.upper()}")

                df = ticker.history(start=start_date.date(), end=end_date.date(), repair=True, interval="1h")
                logger.debug(f"[YFINANCE] History retrieved from Yahoo Finance API")

                if df is None or df.empty:
                    logger.warning(f"[YFINANCE] No data found for {symbol}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.info(f"[RETRY] Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    return None

                logger.info("=" * 80)
                logger.info(f"[YFINANCE RESPONSE] Retrieved {len(df)} records for {symbol.upper()}")
                logger.info(f"[DATA] Date range: {df.index.min().date()} to {df.index.max().date()}")
                logger.info(f"[COLUMNS] {list(df.columns)}")
                logger.info(f"[SAMPLE] Latest: Close=${df['Close'].iloc[-1]:.2f}, Volume={df['Volume'].iloc[-1]:,.0f}")
                logger.info("=" * 80)
                return df

            except Exception as e:
                logger.warning("=" * 80)
                logger.warning(f"[YFINANCE ERROR] Error fetching data for {symbol.upper()} (attempt {attempt+1}/{max_retries}): {e}")
                logger.warning("=" * 80)

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"[RETRY] Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[YFINANCE ERROR] Failed to fetch {symbol.upper()} after {max_retries} attempts")
                    return None

        return None

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        try:
            indicators = self.stock_config.get('include_indicators', [])

            if 'SMA' in indicators:
                df['SMA_20'] = df['Close'].rolling(window=20).mean()
                df['SMA_50'] = df['Close'].rolling(window=50).mean()
                df['SMA_200'] = df['Close'].rolling(window=200).mean()

            if 'RSI' in indicators:
                df['RSI'] = self._calculate_rsi(df['Close'])

            if 'MACD' in indicators:
                df['MACD'], df['Signal_Line'], df['MACD_Hist'] = self._calculate_macd(df['Close'])

            if 'Bollinger_Bands' in indicators:
                bb = self._calculate_bollinger_bands(df['Close'])
                df['BB_Upper'] = bb['upper']
                df['BB_Lower'] = bb['lower']
                df['BB_Middle'] = bb['middle']

            return df

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26,
                       signal: int = 9) -> tuple:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        macd_hist = macd - signal_line

        return macd, signal_line, macd_hist

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20,
                                   num_std: float = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        return {
            'upper': sma + (std * num_std),
            'middle': sma,
            'lower': sma - (std * num_std)
        }

    def save_stock_data_to_db(self, symbol: str, df: pd.DataFrame) -> int:
        """
        Save stock data to MongoDB

        Args:
            symbol: Stock symbol
            df: DataFrame with price data

        Returns:
            Number of records saved
        """
        saved_count = 0

        try:
            for date, row in df.iterrows():
                data = {
                    'symbol': symbol.upper(),
                    'date': date.to_pydatetime() if hasattr(date, 'to_pydatetime') else date,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
                }

                # Add indicators if available
                for col in df.columns:
                    if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']:
                        if not pd.isna(row[col]):
                            data[col.lower()] = float(row[col])

                self.db.insert_stock_price(data)
                saved_count += 1

            logger.info(f"Saved {saved_count} records for {symbol}")

        except Exception as e:
            logger.error(f"Error saving stock data: {e}")

        return saved_count

    def fetch_and_process_stock(self, symbol: str, save_to_db: bool = True) -> Optional[pd.DataFrame]:
        """
        Fetch stock data, calculate indicators, and optionally save to DB

        Args:
            symbol: Stock symbol
            save_to_db: Whether to save to database

        Returns:
            DataFrame with price data and indicators
        """
        try:
            df = self.fetch_stock_data(symbol)

            if df is None or df.empty:
                return None

            df = self.calculate_indicators(df)

            if save_to_db:
                self.save_stock_data_to_db(symbol, df)

            return df

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None

    def get_price_change(self, symbol: str, days: int = 7) -> Optional[Dict[str, float]]:
        """
        Calculate price change over specified period

        Args:
            symbol: Stock symbol
            days: Number of days to look back

        Returns:
            Dictionary with price change metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df = self.fetch_stock_data(symbol, start_date, end_date)

            if df is None or len(df) < 2:
                return None

            first_close = df['Close'].iloc[0]
            last_close = df['Close'].iloc[-1]
            price_change = last_close - first_close
            percent_change = (price_change / first_close) * 100

            return {
                'symbol': symbol.upper(),
                'period_days': days,
                'start_price': float(first_close),
                'end_price': float(last_close),
                'price_change': float(price_change),
                'percent_change': float(percent_change),
                'start_date': start_date,
                'end_date': end_date
            }

        except Exception as e:
            logger.error(f"Error calculating price change for {symbol}: {e}")
            return None

    def compare_prices_with_sentiment(self, symbol: str, sentiment_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare sentiment data with price movements

        Args:
            symbol: Stock symbol
            sentiment_data: List of sentiment analysis records

        Returns:
            Correlation analysis
        """
        try:
            if not sentiment_data:
                return None

            # Get date range from sentiment data
            dates = [s.get('analyzed_at') or s.get('created_utc') for s in sentiment_data if s.get('analyzed_at') or s.get('created_utc')]

            if not dates:
                return None

            min_date = min(dates)
            max_date = max(dates)

            # Fetch price data for the same period
            price_df = self.fetch_stock_data(symbol, min_date, max_date)

            if price_df is None or price_df.empty:
                return None

            # Calculate aggregate sentiment by date
            sentiment_by_date = {}
            for record in sentiment_data:
                date = (record.get('analyzed_at') or record.get('created_utc')).date()
                if date not in sentiment_by_date:
                    sentiment_by_date[date] = {'scores': [], 'count': 0}

                score = record.get('sentiments', {}).get(symbol, {}).get('score', 0)
                sentiment_by_date[date]['scores'].append(score)
                sentiment_by_date[date]['count'] += 1

            # Calculate average sentiment and price change for each date
            correlation_data = []
            for date, sentiment_info in sentiment_by_date.items():
                avg_sentiment = np.mean(sentiment_info['scores'])

                # Find price change for this date
                date_prices = price_df.loc[price_df.index.date == date]
                if len(date_prices) > 0:
                    if len(date_prices) > 1:
                        daily_change = ((date_prices['Close'].iloc[-1] - date_prices['Close'].iloc[0]) /
                                       date_prices['Close'].iloc[0])
                    else:
                        daily_change = 0

                    correlation_data.append({
                        'date': date,
                        'avg_sentiment': avg_sentiment,
                        'mention_count': sentiment_info['count'],
                        'price_change_percent': daily_change * 100
                    })

            # Calculate correlation
            if len(correlation_data) > 2:
                sentiments = [d['avg_sentiment'] for d in correlation_data]
                price_changes = [d['price_change_percent'] for d in correlation_data]

                correlation = np.corrcoef(sentiments, price_changes)[0, 1]

                return {
                    'symbol': symbol,
                    'correlation': float(correlation) if not np.isnan(correlation) else 0,
                    'data_points': len(correlation_data),
                    'period': f"{min_date.date()} to {max_date.date()}",
                    'details': correlation_data
                }

            return None

        except Exception as e:
            logger.error(f"Error comparing prices with sentiment for {symbol}: {e}")
            return None

    def close(self) -> None:
        """Close database connection"""
        if self.db:
            self.db.close()

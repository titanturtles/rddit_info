"""
Pattern analysis engine for identifying trading patterns
Correlates sentiment with price movements and identifies profitable patterns
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import pandas as pd
from config_loader import get_config
from database import MongoDBConnection

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes patterns in sentiment and price data"""

    def __init__(self):
        """Initialize pattern analyzer"""
        self.config = get_config()
        self.pattern_config = self.config.get_section('pattern_analysis')
        self.db = MongoDBConnection()

    def find_tradeable_patterns(self, stock_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Identify tradeable patterns for a stock

        Args:
            stock_symbol: Stock symbol to analyze

        Returns:
            Dictionary with identified patterns
        """
        try:
            # Get sentiment data
            sentiments = self.db.get_sentiments_by_stock(stock_symbol)

            if not sentiments:
                logger.warning(f"No sentiment data found for {stock_symbol}")
                return None

            # Get price data
            min_sentiment_date = min(s.get('analyzed_at', datetime.now()) for s in sentiments)
            prices = self.db.get_stock_prices(stock_symbol, min_sentiment_date)

            if not prices:
                logger.warning(f"No price data found for {stock_symbol}")
                return None

            # Analyze patterns
            patterns = self._analyze_sentiment_price_patterns(stock_symbol, sentiments, prices)

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing patterns for {stock_symbol}: {e}")
            return None

    def _analyze_sentiment_price_patterns(self, symbol: str, sentiments: List[Dict],
                                         prices: List[Dict]) -> Dict[str, Any]:
        """
        Analyze correlation between sentiment and price movements

        Args:
            symbol: Stock symbol
            sentiments: Sentiment data
            prices: Price data

        Returns:
            Pattern analysis results
        """
        try:
            window_days = self.pattern_config.get('window_days', 7)
            correlation_threshold = self.pattern_config.get('correlation_threshold', 0.6)

            # Group sentiments by date
            sentiment_by_date = self._group_sentiment_by_date(sentiments, symbol)

            # Convert prices to DataFrame for easier analysis
            price_df = pd.DataFrame(prices)
            if 'date' in price_df.columns:
                price_df['date'] = pd.to_datetime(price_df['date'])

            # Find patterns
            patterns = {
                'symbol': symbol,
                'analysis_date': datetime.now(),
                'window_days': window_days,
                'bullish_patterns': [],
                'bearish_patterns': [],
                'neutral_patterns': [],
                'summary': {}
            }

            # Analyze each window
            sentiment_dates = sorted(sentiment_by_date.keys())

            for i in range(len(sentiment_dates) - window_days):
                window_start = sentiment_dates[i]
                window_end = sentiment_dates[i + window_days]

                window_sentiments = []
                for j in range(i, min(i + window_days, len(sentiment_dates))):
                    window_sentiments.extend(sentiment_by_date[sentiment_dates[j]])

                if len(window_sentiments) < self.pattern_config.get('min_mentions', 5):
                    continue

                # Calculate average sentiment in window
                avg_sentiment = np.mean([s['score'] for s in window_sentiments])

                # Get price change after window
                price_at_start = self._get_price_at_date(price_df, window_start)
                price_at_end = self._get_price_at_date(price_df, window_end)

                if price_at_start and price_at_end:
                    price_change = ((price_at_end - price_at_start) / price_at_start) * 100

                    # Classify pattern
                    pattern = {
                        'window_start': window_start,
                        'window_end': window_end,
                        'avg_sentiment': float(avg_sentiment),
                        'mention_count': len(window_sentiments),
                        'price_change_percent': float(price_change),
                        'confidence': self._calculate_confidence(window_sentiments)
                    }

                    if avg_sentiment > 0.3 and price_change > self.pattern_config.get('price_change_threshold', 5):
                        patterns['bullish_patterns'].append(pattern)
                    elif avg_sentiment < -0.3 and price_change < -self.pattern_config.get('price_change_threshold', 5):
                        patterns['bearish_patterns'].append(pattern)
                    else:
                        patterns['neutral_patterns'].append(pattern)

            # Calculate summary statistics
            patterns['summary'] = self._calculate_summary_stats(patterns)

            return patterns

        except Exception as e:
            logger.error(f"Error in sentiment-price analysis: {e}")
            return None

    def _group_sentiment_by_date(self, sentiments: List[Dict], symbol: str) -> Dict[datetime, List[Dict]]:
        """Group sentiments by date"""
        grouped = defaultdict(list)

        for sentiment in sentiments:
            if symbol.upper() in sentiment.get('stock_symbol', symbol.upper()):
                date_key = sentiment.get('analyzed_at', datetime.now()).date()
                sentiment_data = sentiment.get('sentiments', {}).get(symbol.upper(), {})

                if 'score' in sentiment_data:
                    grouped[date_key].append({
                        'score': sentiment_data['score'],
                        'sentiment': sentiment_data.get('sentiment', 'NEUTRAL'),
                        'source': 'post' if 'post_id' in sentiment else 'comment'
                    })

        return grouped

    def _get_price_at_date(self, price_df: pd.DataFrame, target_date: datetime) -> Optional[float]:
        """Get closing price at or closest to target date"""
        try:
            if 'date' in price_df.columns:
                filtered = price_df[price_df['date'].dt.date == target_date]
                if not filtered.empty:
                    return float(filtered.iloc[-1]['close'])

                # Try to find nearest date
                price_df['date_diff'] = abs((price_df['date'].dt.date.astype(object) - target_date))
                nearest = price_df.loc[price_df['date_diff'].idxmin()]
                return float(nearest['close'])

        except Exception as e:
            logger.warning(f"Error getting price at date {target_date}: {e}")

        return None

    def _calculate_confidence(self, sentiments: List[Dict]) -> float:
        """Calculate confidence score for pattern"""
        try:
            if not sentiments:
                return 0.0

            # Higher confidence if sentiments are consistent
            scores = [s['score'] for s in sentiments]
            std_dev = np.std(scores)

            # Lower std dev = higher confidence
            confidence = max(0, 1 - (std_dev / 2))
            return float(confidence)

        except Exception as e:
            logger.warning(f"Error calculating confidence: {e}")
            return 0.5

    def _calculate_summary_stats(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics for all patterns"""
        summary = {
            'bullish_count': len(patterns['bullish_patterns']),
            'bearish_count': len(patterns['bearish_patterns']),
            'neutral_count': len(patterns['neutral_patterns']),
            'total_patterns': len(patterns['bullish_patterns']) + len(patterns['bearish_patterns']) + len(patterns['neutral_patterns'])
        }

        # Calculate average returns for each pattern type
        for pattern_type, pattern_list in [('bullish', patterns['bullish_patterns']),
                                            ('bearish', patterns['bearish_patterns'])]:
            if pattern_list:
                avg_return = np.mean([p['price_change_percent'] for p in pattern_list])
                avg_confidence = np.mean([p['confidence'] for p in pattern_list])
                summary[f'{pattern_type}_avg_return'] = float(avg_return)
                summary[f'{pattern_type}_avg_confidence'] = float(avg_confidence)

        return summary

    def identify_correlated_stocks(self) -> List[Dict[str, Any]]:
        """
        Identify stocks with strong sentiment-price correlation

        Returns:
            List of stocks sorted by correlation strength
        """
        try:
            # Get all stocks from sentiment analysis
            sentiment_col = self.db.collections.get('sentiment_analysis')
            stocks = sentiment_col.distinct('stock_symbol')

            correlations = []

            for symbol in stocks:
                patterns = self.find_tradeable_patterns(symbol)

                if patterns and patterns.get('summary'):
                    summary = patterns['summary']
                    correlation_score = (
                        abs(summary.get('bullish_avg_return', 0)) * summary.get('bullish_count', 0) +
                        abs(summary.get('bearish_avg_return', 0)) * summary.get('bearish_count', 0)
                    ) / max(1, summary.get('total_patterns', 1))

                    if correlation_score > self.pattern_config.get('correlation_threshold', 0.6):
                        correlations.append({
                            'symbol': symbol,
                            'correlation_score': float(correlation_score),
                            'patterns': summary,
                            'identified_at': datetime.now()
                        })

            # Sort by correlation score
            correlations.sort(key=lambda x: x['correlation_score'], reverse=True)

            return correlations

        except Exception as e:
            logger.error(f"Error identifying correlated stocks: {e}")
            return []

    def save_pattern_analysis(self, pattern_analysis: Dict[str, Any]) -> str:
        """
        Save pattern analysis to database

        Args:
            pattern_analysis: Pattern analysis results

        Returns:
            Insert ID
        """
        try:
            return self.db.insert_pattern(pattern_analysis)
        except Exception as e:
            logger.error(f"Error saving pattern analysis: {e}")
            return None

    def generate_trading_signals(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on patterns

        Args:
            symbol: Stock symbol

        Returns:
            List of trading signals
        """
        try:
            patterns = self.find_tradeable_patterns(symbol)

            if not patterns:
                return []

            signals = []

            # Generate buy signals
            for pattern in patterns.get('bullish_patterns', []):
                if pattern.get('confidence', 0) > 0.7:
                    signals.append({
                        'symbol': symbol,
                        'signal_type': 'BUY',
                        'confidence': pattern['confidence'],
                        'expected_return': pattern['price_change_percent'],
                        'pattern_date': pattern['window_end'],
                        'reason': f"Bullish sentiment pattern with {pattern['mention_count']} mentions"
                    })

            # Generate sell signals
            for pattern in patterns.get('bearish_patterns', []):
                if pattern.get('confidence', 0) > 0.7:
                    signals.append({
                        'symbol': symbol,
                        'signal_type': 'SELL',
                        'confidence': pattern['confidence'],
                        'expected_return': pattern['price_change_percent'],
                        'pattern_date': pattern['window_end'],
                        'reason': f"Bearish sentiment pattern with {pattern['mention_count']} mentions"
                    })

            return signals

        except Exception as e:
            logger.error(f"Error generating trading signals for {symbol}: {e}")
            return []

    def close(self) -> None:
        """Close database connection"""
        if self.db:
            self.db.close()

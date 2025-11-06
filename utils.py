"""
Utility functions for data analysis and reporting
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from database import MongoDBConnection

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Utility class for analyzing collected data"""

    def __init__(self):
        """Initialize analyzer"""
        self.db = MongoDBConnection()

    def get_sentiment_summary(self, stock_symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Get sentiment summary for a stock

        Args:
            stock_symbol: Stock symbol
            days: Number of days to analyze

        Returns:
            Summary dictionary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            sentiment_col = self.db.collections.get('sentiment_analysis')
            sentiments = list(sentiment_col.find({
                'stock_symbol': stock_symbol.upper(),
                'analyzed_at': {'$gte': cutoff_date}
            }))

            if not sentiments:
                return {'error': 'No sentiment data found'}

            bullish = bearish = neutral = 0
            total_score = 0
            sources = {'post': 0, 'comment': 0}

            for sentiment in sentiments:
                sent_data = sentiment.get('sentiments', {}).get(stock_symbol.upper(), {})
                sentiment_type = sent_data.get('sentiment', 'NEUTRAL')

                if sentiment_type == 'BULLISH':
                    bullish += 1
                elif sentiment_type == 'BEARISH':
                    bearish += 1
                else:
                    neutral += 1

                total_score += sent_data.get('score', 0)
                sources[sentiment.get('content_type', 'comment')] += 1

            total = len(sentiments)
            avg_score = total_score / total if total > 0 else 0

            return {
                'symbol': stock_symbol.upper(),
                'period_days': days,
                'total_mentions': total,
                'bullish_count': bullish,
                'bearish_count': bearish,
                'neutral_count': neutral,
                'bullish_percent': (bullish / total * 100) if total > 0 else 0,
                'bearish_percent': (bearish / total * 100) if total > 0 else 0,
                'neutral_percent': (neutral / total * 100) if total > 0 else 0,
                'average_score': avg_score,
                'dominant_sentiment': max(
                    [('BULLISH', bullish), ('BEARISH', bearish), ('NEUTRAL', neutral)],
                    key=lambda x: x[1]
                )[0],
                'sources': sources
            }

        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}")
            return {'error': str(e)}

    def get_top_mentioned_stocks(self, limit: int = 20, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get most mentioned stocks

        Args:
            limit: Number of stocks to return
            days: Period to analyze

        Returns:
            List of stocks sorted by mentions
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            sentiment_col = self.db.collections.get('sentiment_analysis')
            pipeline = [
                {'$match': {'analyzed_at': {'$gte': cutoff_date}}},
                {'$group': {
                    '_id': '$stock_symbol',
                    'mention_count': {'$sum': 1},
                    'avg_score': {'$avg': '$sentiments'},
                    'bullish': {'$sum': {
                        '$cond': [{'$eq': ['$sentiments.sentiment', 'BULLISH']}, 1, 0]
                    }},
                    'bearish': {'$sum': {
                        '$cond': [{'$eq': ['$sentiments.sentiment', 'BEARISH']}, 1, 0]
                    }}
                }},
                {'$sort': {'mention_count': -1}},
                {'$limit': limit}
            ]

            results = list(sentiment_col.aggregate(pipeline))

            return [{
                'symbol': r['_id'],
                'mentions': r['mention_count'],
                'bullish': r.get('bullish', 0),
                'bearish': r.get('bearish', 0),
                'bullish_ratio': r.get('bullish', 0) / r['mention_count'] if r['mention_count'] > 0 else 0
            } for r in results]

        except Exception as e:
            logger.error(f"Error getting top stocks: {e}")
            return []

    def get_price_performance(self, stock_symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get price performance metrics

        Args:
            stock_symbol: Stock symbol
            days: Period to analyze

        Returns:
            Performance metrics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            prices_col = self.db.collections.get('stock_prices')
            prices = list(prices_col.find({
                'symbol': stock_symbol.upper(),
                'date': {'$gte': cutoff_date}
            }).sort('date', 1))

            if len(prices) < 2:
                return None

            first_price = prices[0]['close']
            last_price = prices[-1]['close']
            highest = max(p['high'] for p in prices)
            lowest = min(p['low'] for p in prices)

            price_change = last_price - first_price
            percent_change = (price_change / first_price) * 100
            volatility = ((highest - lowest) / first_price) * 100

            return {
                'symbol': stock_symbol.upper(),
                'period_days': days,
                'start_price': first_price,
                'end_price': last_price,
                'price_change': price_change,
                'percent_change': percent_change,
                'high': highest,
                'low': lowest,
                'volatility': volatility,
                'data_points': len(prices)
            }

        except Exception as e:
            logger.error(f"Error getting price performance: {e}")
            return None

    def compare_sentiment_vs_price(self, stock_symbol: str,
                                   days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Compare sentiment trend with price trend

        Args:
            stock_symbol: Stock symbol
            days: Period to analyze

        Returns:
            Comparison analysis
        """
        try:
            sentiment_summary = self.get_sentiment_summary(stock_symbol, days)
            price_performance = self.get_price_performance(stock_symbol, days)

            if not sentiment_summary or 'error' in sentiment_summary or not price_performance:
                return None

            sentiment_direction = 'BULLISH' if sentiment_summary['average_score'] > 0.1 else (
                'BEARISH' if sentiment_summary['average_score'] < -0.1 else 'NEUTRAL'
            )

            price_direction = 'UP' if price_performance['percent_change'] > 1 else (
                'DOWN' if price_performance['percent_change'] < -1 else 'FLAT'
            )

            agreement = sentiment_direction == 'BULLISH' and price_direction == 'UP' or \
                       sentiment_direction == 'BEARISH' and price_direction == 'DOWN'

            return {
                'symbol': stock_symbol.upper(),
                'period_days': days,
                'sentiment_summary': sentiment_summary,
                'price_performance': price_performance,
                'sentiment_direction': sentiment_direction,
                'price_direction': price_direction,
                'sentiment_price_agreement': agreement,
                'effectiveness_score': sentiment_summary['bullish_percent'] if price_direction == 'UP' else (
                    100 - sentiment_summary['bullish_percent'] if price_direction == 'DOWN' else 50
                )
            }

        except Exception as e:
            logger.error(f"Error comparing sentiment vs price: {e}")
            return None

    def generate_report(self, stock_symbols: Optional[List[str]] = None,
                       days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive report

        Args:
            stock_symbols: Specific stocks to report on
            days: Period to analyze

        Returns:
            Comprehensive report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'stocks': [],
            'top_stocks': []
        }

        try:
            # Get top stocks if specific list not provided
            if not stock_symbols:
                report['top_stocks'] = self.get_top_mentioned_stocks(10, days)
                stock_symbols = [s['symbol'] for s in report['top_stocks'][:5]]

            # Analyze each stock
            for symbol in stock_symbols:
                analysis = self.compare_sentiment_vs_price(symbol, days)
                if analysis:
                    report['stocks'].append(analysis)

            return report

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            report['error'] = str(e)
            return report

    def export_report_json(self, report: Dict[str, Any], filename: str = 'report.json') -> bool:
        """
        Export report to JSON file

        Args:
            report: Report dictionary
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Report exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return False

    def export_report_csv(self, report: Dict[str, Any], filename: str = 'report.csv') -> bool:
        """
        Export report to CSV file

        Args:
            report: Report dictionary
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            import csv

            with open(filename, 'w', newline='') as f:
                if report.get('stocks'):
                    fieldnames = [
                        'Symbol', 'Mentions', 'Bullish %', 'Bearish %',
                        'Avg Score', 'Price Change %', 'Sentiment-Price Match'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for stock in report['stocks']:
                        writer.writerow({
                            'Symbol': stock['symbol'],
                            'Mentions': stock['sentiment_summary'].get('total_mentions', 0),
                            'Bullish %': f"{stock['sentiment_summary'].get('bullish_percent', 0):.1f}",
                            'Bearish %': f"{stock['sentiment_summary'].get('bearish_percent', 0):.1f}",
                            'Avg Score': f"{stock['sentiment_summary'].get('average_score', 0):.2f}",
                            'Price Change %': f"{stock['price_performance'].get('percent_change', 0):.2f}",
                            'Sentiment-Price Match': 'YES' if stock.get('sentiment_price_agreement') else 'NO'
                        })

            logger.info(f"CSV report exported to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()


def print_sentiment_summary(symbol: str, days: int = 30):
    """Print sentiment summary to console"""
    analyzer = DataAnalyzer()
    summary = analyzer.get_sentiment_summary(symbol, days)

    if 'error' not in summary:
        print(f"\n{'='*60}")
        print(f"Sentiment Summary: {symbol}")
        print(f"{'='*60}")
        print(f"Period: Last {days} days")
        print(f"Total Mentions: {summary['total_mentions']}")
        print(f"\nSentiment Breakdown:")
        print(f"  Bullish:  {summary['bullish_count']} ({summary['bullish_percent']:.1f}%)")
        print(f"  Bearish:  {summary['bearish_count']} ({summary['bearish_percent']:.1f}%)")
        print(f"  Neutral:  {summary['neutral_count']} ({summary['neutral_percent']:.1f}%)")
        print(f"\nAverage Sentiment Score: {summary['average_score']:.2f}")
        print(f"Dominant Sentiment: {summary['dominant_sentiment']}")
        print(f"Sources: {summary['sources']['post']} posts, {summary['sources']['comment']} comments")
        print(f"{'='*60}\n")

    analyzer.close()


def print_top_stocks(limit: int = 10, days: int = 30):
    """Print top mentioned stocks"""
    analyzer = DataAnalyzer()
    stocks = analyzer.get_top_mentioned_stocks(limit, days)

    print(f"\n{'='*80}")
    print(f"Top {limit} Most Mentioned Stocks (Last {days} days)")
    print(f"{'='*80}")
    print(f"{'Symbol':<10} {'Mentions':<12} {'Bullish':<10} {'Bearish':<10} {'Ratio':<10}")
    print(f"{'-'*80}")

    for stock in stocks:
        print(f"{stock['symbol']:<10} {stock['mentions']:<12} {stock['bullish']:<10} {stock['bearish']:<10} {stock['bullish_ratio']:.2f}")

    print(f"{'='*80}\n")
    analyzer.close()

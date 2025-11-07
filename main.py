"""
Main orchestration script for Reddit Trading Bot
Coordinates data collection, analysis, and pattern identification
"""

import logging
import time
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

from config_loader import get_config
from logger_setup import setup_logging
from reddit_fetcher import RedditFetcher
from llm_processor import LLMProcessor
from stock_data_fetcher import StockDataFetcher
from pattern_analyzer import PatternAnalyzer
from database import MongoDBConnection

logger = logging.getLogger(__name__)


class RedditTradingBot:
    """Main orchestration class for the trading bot"""

    def __init__(self):
        """Initialize the bot"""
        self.config = get_config()
        self.reddit_fetcher = None
        self.llm_processor = None
        self.stock_fetcher = None
        self.pattern_analyzer = None
        self.db = None

    def initialize(self) -> bool:
        """
        Initialize all components

        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing Reddit Trading Bot...")

            self.db = MongoDBConnection()
            self.reddit_fetcher = RedditFetcher()
            self.llm_processor = LLMProcessor()
            self.stock_fetcher = StockDataFetcher()
            self.pattern_analyzer = PatternAnalyzer()

            if not self.reddit_fetcher.reddit:
                logger.error("Failed to initialize Reddit API")
                return False

            logger.info("All components initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False

    def fetch_reddit_data(self, subreddits: List[str] = None) -> Dict[str, int]:
        """
        Fetch data from specified subreddits

        Args:
            subreddits: List of subreddit names

        Returns:
            Statistics dictionary
        """
        if not subreddits:
            subreddits = self.config.get('reddit.subreddits', ['wallstreetbets'])

        total_stats = {'posts': 0, 'comments': 0, 'errors': 0}

        for subreddit in subreddits:
            try:
                logger.info(f"Fetching data from r/{subreddit}")
                stats = self.reddit_fetcher.fetch_and_save_subreddit_data(
                    subreddit,
                    time_filter='week',  # Can be adjusted
                    posts_limit=100,
                    comments_per_post=10
                )

                total_stats['posts'] += stats.get('posts', 0)
                total_stats['comments'] += stats.get('comments', 0)

                # Rate limiting
                time.sleep(self.config.get('data_collection.sleep_between_requests', 2))

            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit}: {e}")
                total_stats['errors'] += 1

        return total_stats

    def analyze_reddit_content(self) -> Dict[str, int]:
        """
        Analyze all Reddit content in database for sentiment and stock mentions

        Returns:
            Statistics dictionary
        """
        logger.info("Starting Reddit content analysis...")

        try:
            posts_col = self.db.collections.get('posts')
            comments_col = self.db.collections.get('comments')

            stats = {'posts_analyzed': 0, 'comments_analyzed': 0, 'sentiments_created': 0}

            # Process posts
            if posts_col is not None:
                posts = list(posts_col.find({'stock_mentions': {'$exists': False}}))
                logger.info(f"Found {len(posts)} unanalyzed posts")

                if posts:
                    analyzed_posts = self.llm_processor.batch_analyze_posts(posts)

                    for post in analyzed_posts:
                        if post.get('stock_mentions'):
                            # Save sentiment for each stock
                            for symbol in post['stock_mentions']:
                                sentiment_data = {
                                    'reddit_id': post['reddit_id'],
                                    'content_type': 'post',
                                    'stock_symbol': symbol,
                                    'created_utc': post.get('created_utc'),
                                    'author': post.get('author'),
                                    'subreddit': post.get('subreddit'),
                                    'text': post.get('title', ''),
                                    'sentiments': post.get('sentiments', {})
                                }

                                self.db.insert_sentiment(sentiment_data)
                                stats['sentiments_created'] += 1

                            # Update post with sentiment
                            posts_col.update_one(
                                {'reddit_id': post['reddit_id']},
                                {'$set': {'stock_mentions': post['stock_mentions']}}
                            )

                            stats['posts_analyzed'] += 1

            # Process comments
            if comments_col is not None:
                comments = list(comments_col.find({'stock_mentions': {'$exists': False}}).limit(100))
                logger.info(f"Found {len(comments)} unanalyzed comments")

                if comments:
                    analyzed_comments = self.llm_processor.batch_analyze_comments(comments)

                    for comment in analyzed_comments:
                        if comment.get('stock_mentions'):
                            # Save sentiment for each stock
                            for symbol in comment['stock_mentions']:
                                sentiment_data = {
                                    'reddit_id': comment['reddit_id'],
                                    'content_type': 'comment',
                                    'stock_symbol': symbol,
                                    'created_utc': comment.get('created_utc'),
                                    'author': comment.get('author'),
                                    'subreddit': comment.get('subreddit'),
                                    'text': comment.get('content', ''),
                                    'sentiments': comment.get('sentiments', {})
                                }

                                self.db.insert_sentiment(sentiment_data)
                                stats['sentiments_created'] += 1

                            # Update comment
                            comments_col.update_one(
                                {'reddit_id': comment['reddit_id']},
                                {'$set': {'stock_mentions': comment['stock_mentions']}}
                            )

                            stats['comments_analyzed'] += 1

            logger.info(f"Analysis complete. Stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error during content analysis: {e}")
            return {'error': str(e)}

    def fetch_stock_data(self, symbols: List[str] = None) -> Dict[str, int]:
        """
        Fetch and process stock price data

        Args:
            symbols: List of stock symbols to fetch

        Returns:
            Statistics dictionary
        """
        if not symbols:
            # Get symbols from sentiment analysis
            sentiment_col = self.db.collections.get('sentiment_analysis')
            symbols = sentiment_col.distinct('stock_symbol') if sentiment_col is not None else []

        logger.info(f"Fetching stock data for {len(symbols)} symbols")

        stats = {'success': 0, 'failed': 0}

        for symbol in symbols:
            try:
                logger.info(f"Processing {symbol}")
                self.stock_fetcher.fetch_and_process_stock(symbol, save_to_db=True)
                stats['success'] += 1

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                stats['failed'] += 1

        return stats

    def analyze_patterns(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze patterns for specified stocks

        Args:
            symbols: List of stock symbols to analyze

        Returns:
            List of pattern analysis results
        """
        if not symbols:
            sentiment_col = self.db.collections.get('sentiment_analysis')
            symbols = sentiment_col.distinct('stock_symbol') if sentiment_col is not None else []

        logger.info(f"Analyzing patterns for {len(symbols)} symbols")

        results = []

        for symbol in symbols:
            try:
                logger.info(f"Analyzing patterns for {symbol}")

                patterns = self.pattern_analyzer.find_tradeable_patterns(symbol)

                if patterns:
                    # Save to database
                    result_id = self.pattern_analyzer.save_pattern_analysis(patterns)
                    if result_id:
                        results.append({
                            'symbol': symbol,
                            'result_id': result_id,
                            'summary': patterns.get('summary', {})
                        })

                        # Generate signals
                        signals = self.pattern_analyzer.generate_trading_signals(symbol)
                        if signals:
                            logger.info(f"Generated {len(signals)} trading signals for {symbol}")
                            for signal in signals:
                                logger.info(f"Signal: {signal}")

            except Exception as e:
                logger.error(f"Error analyzing patterns for {symbol}: {e}")

        return results

    def run_full_pipeline(self, subreddits: List[str] = None, time_filter: str = 'week') -> Dict[str, Any]:
        """
        Run the complete pipeline: fetch -> analyze -> patterns

        Args:
            subreddits: List of subreddits to process
            time_filter: Time filter for Reddit data

        Returns:
            Execution summary
        """
        logger.info("=" * 80)
        logger.info("Starting full pipeline execution")
        logger.info("=" * 80)

        summary = {
            'start_time': datetime.now(),
            'stages': {}
        }

        try:
            # Stage 1: Fetch Reddit data
            logger.info("\n--- Stage 1: Fetching Reddit Data ---")
            reddit_stats = self.fetch_reddit_data(subreddits)
            summary['stages']['reddit_fetch'] = reddit_stats
            logger.info(f"Reddit fetch stats: {reddit_stats}")

            # Stage 2: Analyze content
            logger.info("\n--- Stage 2: Analyzing Content ---")
            analysis_stats = self.analyze_reddit_content()
            summary['stages']['content_analysis'] = analysis_stats
            logger.info(f"Content analysis stats: {analysis_stats}")

            # Stage 3: Fetch stock data
            logger.info("\n--- Stage 3: Fetching Stock Data ---")
            stock_stats = self.fetch_stock_data()
            summary['stages']['stock_data'] = stock_stats
            logger.info(f"Stock data stats: {stock_stats}")

            # Stage 4: Pattern analysis
            logger.info("\n--- Stage 4: Analyzing Patterns ---")
            pattern_results = self.analyze_patterns()
            summary['stages']['pattern_analysis'] = {
                'analyzed_symbols': len(pattern_results),
                'results': pattern_results
            }
            logger.info(f"Pattern analysis: {len(pattern_results)} symbols analyzed")

            summary['end_time'] = datetime.now()
            summary['duration'] = (summary['end_time'] - summary['start_time']).total_seconds()

            logger.info("\n" + "=" * 80)
            logger.info("Pipeline execution completed successfully")
            logger.info(f"Total duration: {summary['duration']:.2f} seconds")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Fatal error in pipeline: {e}")
            summary['error'] = str(e)

        return summary

    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")

        if self.reddit_fetcher:
            self.reddit_fetcher.close()

        if self.stock_fetcher:
            self.stock_fetcher.close()

        if self.pattern_analyzer:
            self.pattern_analyzer.close()

        if self.db:
            self.db.close()

        logger.info("Cleanup completed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Reddit Trading Bot')

    parser.add_argument(
        '--mode',
        choices=['full', 'fetch', 'analyze', 'patterns', 'signals'],
        default='full',
        help='Execution mode'
    )

    parser.add_argument(
        '--subreddits',
        nargs='+',
        help='Subreddits to process'
    )

    parser.add_argument(
        '--stocks',
        nargs='+',
        help='Stock symbols to analyze'
    )

    parser.add_argument(
        '--time-filter',
        default='week',
        help='Time filter for Reddit data'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Create and initialize bot
    bot = RedditTradingBot()

    if not bot.initialize():
        logger.error("Failed to initialize bot")
        return

    try:
        if args.mode == 'full':
            summary = bot.run_full_pipeline(args.subreddits, args.time_filter)

        elif args.mode == 'fetch':
            stats = bot.fetch_reddit_data(args.subreddits)
            logger.info(f"Fetch completed: {stats}")

        elif args.mode == 'analyze':
            stats = bot.analyze_reddit_content()
            logger.info(f"Analysis completed: {stats}")

        elif args.mode == 'patterns':
            results = bot.analyze_patterns(args.stocks)
            logger.info(f"Pattern analysis completed: {len(results)} stocks analyzed")

        elif args.mode == 'signals':
            results = bot.analyze_patterns(args.stocks)
            logger.info(f"Trading signals generated for {len(results)} stocks")

    except Exception as e:
        logger.error(f"Error during execution: {e}")

    finally:
        bot.cleanup()


if __name__ == '__main__':
    main()

"""
MongoDB database connection and schema management
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config_loader import get_config

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """Manages MongoDB connection and operations"""

    def __init__(self):
        """Initialize MongoDB connection"""
        self.config = get_config()
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collections = {}
        self.connect()

    def connect(self) -> bool:
        """
        Establish MongoDB connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            mongo_config = self.config.get_section('mongodb')
            host = mongo_config.get('host', 'mongodb://localhost:27017')

            self.client = MongoClient(host, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')

            db_name = mongo_config.get('database', 'reddit_trading')
            self.db = self.client[db_name]

            logger.info(f"Connected to MongoDB: {host}")
            self._setup_collections()
            self._create_indexes()
            return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def _setup_collections(self) -> None:
        """Initialize collection references"""
        mongo_config = self.config.get_section('mongodb')
        collections_config = mongo_config.get('collections', {})

        for key, collection_name in collections_config.items():
            self.collections[key] = self.db[collection_name]
            logger.info(f"Collection '{key}' -> '{collection_name}'")

    def _create_indexes(self) -> None:
        """Create indexes for optimal query performance"""
        try:
            # Indexes for posts collection
            posts_col = self.collections.get('posts')
            if posts_col is not None:
                posts_col.create_index([('created_utc', DESCENDING)])
                posts_col.create_index([('subreddit', ASCENDING)])
                posts_col.create_index([('author', ASCENDING)])
                posts_col.create_index([('reddit_id', ASCENDING)], unique=True)

            # Indexes for comments collection
            comments_col = self.collections.get('comments')
            if comments_col is not None:
                comments_col.create_index([('created_utc', DESCENDING)])
                comments_col.create_index([('author', ASCENDING)])
                comments_col.create_index([('reddit_id', ASCENDING)], unique=True)

            # Indexes for sentiment analysis
            sentiment_col = self.collections.get('sentiment_analysis')
            if sentiment_col is not None:
                sentiment_col.create_index([('reddit_id', ASCENDING)])
                sentiment_col.create_index([('stock_symbol', ASCENDING)])
                sentiment_col.create_index([('analyzed_date', DESCENDING)])

            # Indexes for stock prices
            prices_col = self.collections.get('stock_prices')
            if prices_col is not None:
                prices_col.create_index([('symbol', ASCENDING), ('date', DESCENDING)])
                prices_col.create_index([('symbol', ASCENDING)])

            # Indexes for patterns
            patterns_col = self.collections.get('patterns')
            if patterns_col is not None:
                patterns_col.create_index([('stock_symbol', ASCENDING)])
                patterns_col.create_index([('correlation_score', DESCENDING)])

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    def insert_post(self, post_data: Dict[str, Any]) -> str:
        """
        Insert a Reddit post into database

        Args:
            post_data: Post data dictionary

        Returns:
            Insert ID
        """
        try:
            post_data['inserted_at'] = datetime.utcnow()
            result = self.collections['posts'].insert_one(post_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert post: {e}")
            return None

    def insert_comment(self, comment_data: Dict[str, Any]) -> str:
        """
        Insert a Reddit comment into database

        Args:
            comment_data: Comment data dictionary

        Returns:
            Insert ID
        """
        try:
            comment_data['inserted_at'] = datetime.utcnow()
            result = self.collections['comments'].insert_one(comment_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert comment: {e}")
            return None

    def insert_sentiment(self, sentiment_data: Dict[str, Any]) -> str:
        """Insert sentiment analysis result"""
        try:
            sentiment_data['analyzed_at'] = datetime.utcnow()
            result = self.collections['sentiment_analysis'].insert_one(sentiment_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert sentiment: {e}")
            return None

    def insert_stock_price(self, price_data: Dict[str, Any]) -> str:
        """Insert stock price data"""
        try:
            result = self.collections['stock_prices'].insert_one(price_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert stock price: {e}")
            return None

    def insert_pattern(self, pattern_data: Dict[str, Any]) -> str:
        """Insert pattern analysis result"""
        try:
            pattern_data['created_at'] = datetime.utcnow()
            result = self.collections['patterns'].insert_one(pattern_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to insert pattern: {e}")
            return None

    def get_sentiments_by_stock(self, stock_symbol: str, limit: int = 100) -> List[Dict]:
        """Get all sentiments for a specific stock"""
        try:
            return list(self.collections['sentiment_analysis'].find(
                {'stock_symbol': stock_symbol.upper()}
            ).sort('analyzed_at', DESCENDING).limit(limit))
        except Exception as e:
            logger.error(f"Failed to get sentiments for {stock_symbol}: {e}")
            return []

    def get_posts_by_stock(self, stock_symbol: str, limit: int = 100) -> List[Dict]:
        """Get all posts mentioning a stock"""
        try:
            return list(self.collections['posts'].find(
                {'stock_mentions': stock_symbol.upper()}
            ).sort('created_utc', DESCENDING).limit(limit))
        except Exception as e:
            logger.error(f"Failed to get posts for {stock_symbol}: {e}")
            return []

    def get_stock_prices(self, symbol: str, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict]:
        """Get historical stock prices"""
        try:
            query = {'symbol': symbol.upper()}
            if start_date:
                query['date'] = {'$gte': start_date}
            if end_date:
                if 'date' in query:
                    query['date']['$lte'] = end_date
                else:
                    query['date'] = {'$lte': end_date}

            return list(self.collections['stock_prices'].find(query).sort('date', ASCENDING))
        except Exception as e:
            logger.error(f"Failed to get stock prices for {symbol}: {e}")
            return []

    def get_patterns_by_stock(self, stock_symbol: str) -> List[Dict]:
        """Get all patterns for a stock"""
        try:
            return list(self.collections['patterns'].find(
                {'stock_symbol': stock_symbol.upper()}
            ).sort('correlation_score', DESCENDING))
        except Exception as e:
            logger.error(f"Failed to get patterns for {stock_symbol}: {e}")
            return []

    def post_exists(self, reddit_id: str) -> bool:
        """Check if post already exists in database"""
        return self.collections['posts'].find_one({'reddit_id': reddit_id}) is not None

    def comment_exists(self, reddit_id: str) -> bool:
        """Check if comment already exists in database"""
        return self.collections['comments'].find_one({'reddit_id': reddit_id}) is not None

    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

"""
Reddit API data fetcher using PRAW
Pulls posts and comments from specified subreddits
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import praw
from praw.exceptions import PRAWException
from config_loader import get_config
from database import MongoDBConnection

logger = logging.getLogger(__name__)


class RedditFetcher:
    """Fetches data from Reddit using PRAW"""

    def __init__(self):
        """Initialize Reddit API connection"""
        self.config = get_config()
        self.reddit = None
        self.db = None
        self._initialize_reddit()

    def _initialize_reddit(self) -> bool:
        """
        Initialize Reddit API connection

        Returns:
            True if successful, False otherwise
        """
        try:
            reddit_config = self.config.get_section('reddit')

            self.reddit = praw.Reddit(
                client_id=reddit_config.get('client_id'),
                client_secret=reddit_config.get('client_secret'),
                user_agent=reddit_config.get('user_agent', 'RedditStockBot/1.0')
            )

            # Test connection
            self.reddit.user.me()
            logger.info("Reddit API connection successful")
            self.db = MongoDBConnection()
            return True

        except PRAWException as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            logger.error("Please check your Reddit API credentials in config.json")
            return False

    def fetch_posts(self, subreddit_name: str, time_filter: str = 'month',
                   limit: int = None) -> List[Dict[str, Any]]:
        """
        Fetch posts from a subreddit

        Args:
            subreddit_name: Name of subreddit (without r/)
            time_filter: 'all', 'year', 'month', 'week', 'day', 'hour'
            limit: Maximum number of posts to fetch

        Returns:
            List of post dictionaries
        """
        posts = []
        try:
            reddit_config = self.config.get_section('reddit')
            limit = limit or reddit_config.get('limit_per_request', 100)

            subreddit = self.reddit.subreddit(subreddit_name)
            logger.info(f"Fetching posts from r/{subreddit_name} (limit: {limit})")

            for post in subreddit.top(time_filter=time_filter, limit=limit):
                try:
                    # Skip if already in database
                    if self.db.post_exists(post.id):
                        logger.debug(f"Post {post.id} already exists, skipping")
                        continue

                    post_data = {
                        'reddit_id': post.id,
                        'title': post.title,
                        'content': post.selftext,
                        'author': post.author.name if post.author else '[deleted]',
                        'subreddit': post.subreddit.display_name,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'url': post.url,
                        'is_self': post.is_self,
                        'upvote_ratio': post.upvote_ratio
                    }

                    posts.append(post_data)

                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue

            logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit_name}")
            return posts

        except PRAWException as e:
            logger.error(f"Reddit API error while fetching posts: {e}")
            return posts

    def fetch_comments(self, subreddit_name: str, post_id: Optional[str] = None,
                      limit: int = None) -> List[Dict[str, Any]]:
        """
        Fetch comments from a subreddit or specific post

        Args:
            subreddit_name: Name of subreddit (without r/)
            post_id: Optional specific post ID
            limit: Maximum number of comments

        Returns:
            List of comment dictionaries
        """
        comments = []
        try:
            reddit_config = self.config.get_section('reddit')
            limit = limit or reddit_config.get('limit_per_request', 100)

            if post_id:
                submission = self.reddit.submission(id=post_id)
                submission.comments.replace_more(limit=0)
                comment_forest = submission.comments.list()
                logger.info(f"Fetching comments from post {post_id}")
            else:
                subreddit = self.reddit.subreddit(subreddit_name)
                comment_forest = subreddit.comments(limit=limit)
                logger.info(f"Fetching comments from r/{subreddit_name}")

            for comment in comment_forest[:limit]:
                try:
                    if self.db.comment_exists(comment.id):
                        continue

                    comment_data = {
                        'reddit_id': comment.id,
                        'content': comment.body,
                        'author': comment.author.name if comment.author else '[deleted]',
                        'subreddit': comment.subreddit.display_name if hasattr(comment, 'subreddit') else subreddit_name,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'parent_id': comment.parent_id,
                        'post_id': getattr(comment, 'link_id', None)
                    }

                    comments.append(comment_data)

                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue

            logger.info(f"Successfully fetched {len(comments)} comments")
            return comments

        except PRAWException as e:
            logger.error(f"Reddit API error while fetching comments: {e}")
            return comments

    def save_posts_to_db(self, posts: List[Dict[str, Any]]) -> int:
        """
        Save posts to MongoDB

        Args:
            posts: List of post dictionaries

        Returns:
            Number of posts saved
        """
        saved_count = 0
        for post in posts:
            try:
                result = self.db.insert_post(post)
                if result:
                    saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save post: {e}")

        logger.info(f"Saved {saved_count}/{len(posts)} posts to database")
        return saved_count

    def save_comments_to_db(self, comments: List[Dict[str, Any]]) -> int:
        """
        Save comments to MongoDB

        Args:
            comments: List of comment dictionaries

        Returns:
            Number of comments saved
        """
        saved_count = 0
        for comment in comments:
            try:
                result = self.db.insert_comment(comment)
                if result:
                    saved_count += 1
            except Exception as e:
                logger.error(f"Failed to save comment: {e}")

        logger.info(f"Saved {saved_count}/{len(comments)} comments to database")
        return saved_count

    def fetch_and_save_subreddit_data(self, subreddit_name: str, time_filter: str = 'month',
                                     posts_limit: int = None, comments_per_post: int = None) -> Dict[str, int]:
        """
        Fetch and save both posts and comments from a subreddit

        Args:
            subreddit_name: Subreddit name
            time_filter: Time filter for posts
            posts_limit: Max posts to fetch
            comments_per_post: Max comments per post

        Returns:
            Dictionary with counts of saved posts and comments
        """
        stats = {'posts': 0, 'comments': 0}

        try:
            # Fetch posts
            posts = self.fetch_posts(subreddit_name, time_filter, posts_limit)
            stats['posts'] = self.save_posts_to_db(posts)

            # Optional: Fetch comments from each post
            if comments_per_post:
                for post in posts[:min(5, len(posts))]:  # Limit to avoid rate limits
                    comments = self.fetch_comments(subreddit_name, post['reddit_id'], comments_per_post)
                    stats['comments'] += self.save_comments_to_db(comments)
                    time.sleep(self.config.get('data_collection.sleep_between_requests', 2))

        except Exception as e:
            logger.error(f"Error in fetch_and_save_subreddit_data: {e}")

        return stats

    def close(self) -> None:
        """Close database connection"""
        if self.db:
            self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

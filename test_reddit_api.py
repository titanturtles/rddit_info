"""
Test script for Reddit API connection
Verifies that Reddit credentials are valid and working
"""

import logging
from config_loader import get_config
from logger_setup import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def test_reddit_connection():
    """Test Reddit API connection and authentication"""

    print("\n" + "="*70)
    print("TESTING REDDIT API CONNECTION")
    print("="*70 + "\n")

    try:
        # Load config
        print("1. Loading configuration...")
        config = get_config()
        reddit_config = config.get_section('reddit')

        client_id = reddit_config.get('client_id')
        client_secret = reddit_config.get('client_secret')
        user_agent = reddit_config.get('user_agent')

        print(f"   ✓ Config loaded")
        print(f"   - Client ID: {client_id[:15]}..." if client_id else "   - Client ID: NOT SET")
        print(f"   - Client Secret: {client_secret[:15]}..." if client_secret else "   - Client Secret: NOT SET")
        print(f"   - User Agent: {user_agent}")
        print()

        # Check if credentials are set
        if client_id == "YOUR_REDDIT_CLIENT_ID" or client_secret == "YOUR_REDDIT_CLIENT_SECRET":
            print("   ✗ ERROR: Credentials not configured!")
            print("   Please edit config.json and add your Reddit API credentials")
            return False

        # Import PRAW
        print("2. Importing PRAW library...")
        try:
            import praw
            print("   ✓ PRAW imported successfully")
        except ImportError:
            print("   ✗ PRAW not installed. Run: pip install praw")
            return False

        print()

        # Initialize Reddit connection
        print("3. Initializing Reddit API connection...")
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            print("   ✓ Connection initialized")
        except Exception as e:
            print(f"   ✗ Failed to initialize: {e}")
            return False

        print()

        # Test authentication
        print("4. Testing authentication...")
        try:
            # This will fail if credentials are wrong
            user = reddit.user.me()
            print(f"   ✓ Authentication successful!")
            print(f"   - User: {user}")
        except Exception as e:
            print(f"   ✗ Authentication failed: {e}")
            print("   - Check your client_id and client_secret")
            print(f"   - Error details: {type(e).__name__}")
            return False

        print()

        # Test fetching posts
        print("5. Fetching posts from r/wallstreetbets...")
        try:
            subreddit = reddit.subreddit('wallstreetbets')
            posts = []

            for i, post in enumerate(subreddit.hot(limit=5)):
                posts.append(post)
                print(f"   Post {i+1}:")
                print(f"     - Title: {post.title[:50]}...")
                print(f"     - Author: {post.author.name if post.author else '[deleted]'}")
                print(f"     - Score: {post.score}")
                print(f"     - Comments: {post.num_comments}")

            print(f"\n   ✓ Successfully fetched {len(posts)} posts")
        except Exception as e:
            print(f"   ✗ Failed to fetch posts: {e}")
            return False

        print()

        # Test fetching comments
        print("6. Fetching comments from a post...")
        try:
            if posts:
                first_post = posts[0]
                first_post.comments.replace_more(limit=0)
                comments = first_post.comments.list()[:3]

                for i, comment in enumerate(comments):
                    print(f"   Comment {i+1}:")
                    print(f"     - Author: {comment.author.name if comment.author else '[deleted]'}")
                    print(f"     - Content: {comment.body[:50]}...")
                    print(f"     - Score: {comment.score}")

                print(f"\n   ✓ Successfully fetched comments")
        except Exception as e:
            print(f"   ✗ Failed to fetch comments: {e}")
            return False

        print()
        print("="*70)
        print("✅ REDDIT API TEST SUCCESSFUL!")
        print("="*70)
        print()
        print("Summary:")
        print("  ✓ Configuration loaded")
        print("  ✓ PRAW library working")
        print("  ✓ Authentication successful")
        print("  ✓ Can fetch posts from subreddit")
        print("  ✓ Can fetch comments from posts")
        print()
        print("Your Reddit API credentials are VALID and working! 🎉")
        print()

        return True

    except Exception as e:
        print("="*70)
        print("❌ REDDIT API TEST FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()

        import traceback
        print("Full traceback:")
        traceback.print_exc()

        print()
        print("Troubleshooting:")
        print("  1. Check if praw is installed: pip install praw")
        print("  2. Verify config.json has correct Reddit credentials")
        print("  3. Check internet connection")
        print("  4. Ensure Reddit app created at https://www.reddit.com/prefs/apps")
        print("  5. Check that your IP is not rate-limited")

        return False


def main():
    """Run the Reddit API test"""
    success = test_reddit_connection()
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

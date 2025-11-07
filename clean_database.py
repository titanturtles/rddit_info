#!/usr/bin/env python3
"""
Database cleaning utility for Reddit Trading Bot
Provides multiple cleaning options with safety confirmations
"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Optional
from database import MongoDBConnection
from config_loader import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """Cleans and maintains the MongoDB database"""

    def __init__(self):
        """Initialize database cleaner"""
        self.db = MongoDBConnection()
        self.config = get_config()

    def get_collection_stats(self) -> dict:
        """Get statistics for all collections"""
        stats = {}
        logger.info("=" * 80)
        logger.info("DATABASE COLLECTION STATISTICS")
        logger.info("=" * 80)

        for key, collection in self.db.collections.items():
            count = collection.count_documents({})
            size = self.db.db.command("collStats", collection.name)["size"]
            avg_doc_size = size // count if count > 0 else 0

            stats[key] = {
                'name': collection.name,
                'count': count,
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'avg_doc_size': avg_doc_size
            }

            logger.info(f"\n[{key.upper()}]")
            logger.info(f"  Collection: {collection.name}")
            logger.info(f"  Documents: {count:,}")
            logger.info(f"  Size: {stats[key]['size_mb']} MB")
            logger.info(f"  Avg Doc Size: {avg_doc_size:,} bytes")

        total_size_mb = sum(s['size_mb'] for s in stats.values())
        total_docs = sum(s['count'] for s in stats.values())

        logger.info("=" * 80)
        logger.info(f"TOTAL: {total_docs:,} documents, {total_size_mb} MB")
        logger.info("=" * 80)

        return stats

    def delete_old_posts(self, days: int = 90) -> int:
        """
        Delete posts older than specified days

        Args:
            days: Number of days to keep (default 90)

        Returns:
            Number of deleted documents
        """
        logger.info("=" * 80)
        logger.info(f"[CLEANUP] Deleting posts older than {days} days")
        logger.info("=" * 80)

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        posts_col = self.db.collections.get('posts')

        if posts_col is None:
            logger.error("Posts collection not found")
            return 0

        query = {'created_utc': {'$lt': cutoff_date}}
        old_posts = posts_col.count_documents(query)

        if old_posts == 0:
            logger.info("No old posts found to delete")
            return 0

        logger.warning(f"Found {old_posts:,} posts older than {days} days")
        confirmation = input(f"Delete {old_posts:,} posts? (yes/no): ").strip().lower()

        if confirmation != 'yes':
            logger.info("Deletion cancelled")
            return 0

        result = posts_col.delete_many(query)
        logger.info(f"[DELETED] {result.deleted_count:,} old posts")
        return result.deleted_count

    def delete_duplicate_posts(self) -> int:
        """
        Delete duplicate posts (based on reddit_id)

        Returns:
            Number of deleted documents
        """
        logger.info("=" * 80)
        logger.info("[CLEANUP] Detecting duplicate posts")
        logger.info("=" * 80)

        posts_col = self.db.collections.get('posts')

        if posts_col is None:
            logger.error("Posts collection not found")
            return 0

        # Find duplicates
        pipeline = [
            {'$group': {
                '_id': '$reddit_id',
                'count': {'$sum': 1},
                'ids': {'$push': '$_id'}
            }},
            {'$match': {'count': {'$gt': 1}}}
        ]

        duplicates = list(posts_col.aggregate(pipeline))
        total_dupes = sum(d['count'] - 1 for d in duplicates)

        if not duplicates:
            logger.info("No duplicate posts found")
            return 0

        logger.warning(f"Found {len(duplicates)} duplicate groups ({total_dupes:,} total duplicates)")

        confirmation = input(f"Delete {total_dupes:,} duplicate posts? (yes/no): ").strip().lower()

        if confirmation != 'yes':
            logger.info("Deletion cancelled")
            return 0

        deleted = 0
        for dup in duplicates:
            # Keep the first, delete the rest
            ids_to_delete = dup['ids'][1:]
            result = posts_col.delete_many({'_id': {'$in': ids_to_delete}})
            deleted += result.deleted_count
            logger.debug(f"Deleted {result.deleted_count} duplicates for reddit_id {dup['_id']}")

        logger.info(f"[DELETED] {deleted:,} duplicate posts")
        return deleted

    def delete_posts_without_sentiment(self) -> int:
        """
        Delete posts that have no corresponding sentiment analysis

        Returns:
            Number of deleted documents
        """
        logger.info("=" * 80)
        logger.info("[CLEANUP] Finding posts without sentiment analysis")
        logger.info("=" * 80)

        posts_col = self.db.collections.get('posts')
        sentiment_col = self.db.collections.get('sentiment_analysis')

        if posts_col is None or sentiment_col is None:
            logger.error("Required collections not found")
            return 0

        # Find all post reddit_ids that have sentiment
        posts_with_sentiment = set(
            doc['reddit_id'] for doc in sentiment_col.find({}, {'reddit_id': 1})
        )

        # Find posts without sentiment
        posts_without_sentiment = posts_col.count_documents(
            {'reddit_id': {'$nin': list(posts_with_sentiment)}}
        )

        if posts_without_sentiment == 0:
            logger.info("All posts have sentiment analysis")
            return 0

        logger.warning(f"Found {posts_without_sentiment:,} posts without sentiment analysis")
        confirmation = input(f"Delete {posts_without_sentiment:,} posts? (yes/no): ").strip().lower()

        if confirmation != 'yes':
            logger.info("Deletion cancelled")
            return 0

        result = posts_col.delete_many(
            {'reddit_id': {'$nin': list(posts_with_sentiment)}}
        )
        logger.info(f"[DELETED] {result.deleted_count:,} posts without sentiment")
        return result.deleted_count

    def delete_failed_llm_responses(self) -> int:
        """
        Delete failed LLM API responses

        Returns:
            Number of deleted documents
        """
        logger.info("=" * 80)
        logger.info("[CLEANUP] Deleting failed LLM responses")
        logger.info("=" * 80)

        llm_col = self.db.collections.get('llm_responses')

        if llm_col is None:
            logger.error("LLM responses collection not found")
            return 0

        failed_count = llm_col.count_documents({'status': {'$ne': 'success'}})

        if failed_count == 0:
            logger.info("No failed LLM responses found")
            return 0

        logger.warning(f"Found {failed_count:,} failed LLM responses")
        confirmation = input(f"Delete {failed_count:,} failed responses? (yes/no): ").strip().lower()

        if confirmation != 'yes':
            logger.info("Deletion cancelled")
            return 0

        result = llm_col.delete_many({'status': {'$ne': 'success'}})
        logger.info(f"[DELETED] {result.deleted_count:,} failed LLM responses")
        return result.deleted_count

    def clear_collection(self, collection_key: str) -> int:
        """
        Clear entire collection (with confirmation)

        Args:
            collection_key: Key of collection to clear

        Returns:
            Number of deleted documents
        """
        logger.info("=" * 80)
        logger.info(f"[WARNING] CLEARING COLLECTION: {collection_key.upper()}")
        logger.info("=" * 80)

        collection = self.db.collections.get(collection_key)

        if collection is None:
            logger.error(f"Collection '{collection_key}' not found")
            return 0

        count = collection.count_documents({})

        if count == 0:
            logger.info(f"Collection '{collection_key}' is already empty")
            return 0

        logger.warning(f"This will DELETE ALL {count:,} documents in {collection_key}")
        confirmation = input(f"Type 'DELETE {collection_key.upper()}' to confirm: ").strip()

        if confirmation != f'DELETE {collection_key.upper()}':
            logger.info("Clear operation cancelled")
            return 0

        result = collection.delete_many({})
        logger.info(f"[DELETED] {result.deleted_count:,} documents from {collection_key}")
        return result.deleted_count

    def rebuild_indexes(self) -> bool:
        """Rebuild all database indexes"""
        logger.info("=" * 80)
        logger.info("[MAINTENANCE] Rebuilding database indexes")
        logger.info("=" * 80)

        try:
            self.db._create_indexes()
            logger.info("Indexes rebuilt successfully")
            logger.info("=" * 80)
            return True
        except Exception as e:
            logger.error(f"Failed to rebuild indexes: {e}")
            return False

    def export_collection(self, collection_key: str, filepath: str) -> bool:
        """
        Export collection to JSON file

        Args:
            collection_key: Key of collection to export
            filepath: Path to save JSON file

        Returns:
            True if successful
        """
        import json
        from bson import ObjectId

        logger.info("=" * 80)
        logger.info(f"[EXPORT] Exporting {collection_key} to {filepath}")
        logger.info("=" * 80)

        collection = self.db.collections.get(collection_key)

        if collection is None:
            logger.error(f"Collection '{collection_key}' not found")
            return False

        try:
            documents = list(collection.find({}))
            count = len(documents)

            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                doc['_id'] = str(doc['_id'])

            with open(filepath, 'w') as f:
                json.dump(documents, f, indent=2, default=str)

            logger.info(f"[EXPORTED] {count:,} documents to {filepath}")
            logger.info("=" * 80)
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


def show_menu():
    """Display the cleaning menu"""
    print("\n" + "=" * 80)
    print("DATABASE CLEANING UTILITY")
    print("=" * 80)
    print("\n1. Show database statistics")
    print("2. Delete posts older than X days")
    print("3. Delete duplicate posts")
    print("4. Delete posts without sentiment analysis")
    print("5. Delete failed LLM responses")
    print("6. Clear entire collection")
    print("7. Rebuild indexes")
    print("8. Export collection to JSON")
    print("9. Exit")
    print("\n" + "=" * 80)


def main():
    """Main menu loop"""
    cleaner = DatabaseCleaner()

    while True:
        show_menu()
        choice = input("Select option (1-9): ").strip()

        if choice == '1':
            cleaner.get_collection_stats()

        elif choice == '2':
            days = input("Enter number of days to keep (default 90): ").strip()
            days = int(days) if days.isdigit() else 90
            cleaner.delete_old_posts(days)

        elif choice == '3':
            cleaner.delete_duplicate_posts()

        elif choice == '4':
            cleaner.delete_posts_without_sentiment()

        elif choice == '5':
            cleaner.delete_failed_llm_responses()

        elif choice == '6':
            print("\nAvailable collections:")
            for i, key in enumerate(cleaner.db.collections.keys(), 1):
                print(f"  {i}. {key}")
            col_choice = input("\nEnter collection number: ").strip()
            if col_choice.isdigit():
                collections = list(cleaner.db.collections.keys())
                if 0 <= int(col_choice) - 1 < len(collections):
                    collection_key = collections[int(col_choice) - 1]
                    cleaner.clear_collection(collection_key)

        elif choice == '7':
            cleaner.rebuild_indexes()

        elif choice == '8':
            print("\nAvailable collections:")
            for i, key in enumerate(cleaner.db.collections.keys(), 1):
                print(f"  {i}. {key}")
            col_choice = input("\nEnter collection number: ").strip()
            filepath = input("Enter filepath for export (e.g., ./posts_backup.json): ").strip()
            if col_choice.isdigit() and filepath:
                collections = list(cleaner.db.collections.keys())
                if 0 <= int(col_choice) - 1 < len(collections):
                    collection_key = collections[int(col_choice) - 1]
                    cleaner.export_collection(collection_key, filepath)

        elif choice == '9':
            logger.info("Exiting database cleaner")
            sys.exit(0)

        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    main()

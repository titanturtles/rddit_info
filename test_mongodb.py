"""
Test script for MongoDB connection
Verifies MongoDB is running and accessible
"""

import logging
from config_loader import get_config
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def test_mongodb_connection():
    """Test MongoDB connection"""

    print("\n" + "="*70)
    print("TESTING MONGODB CONNECTION")
    print("="*70 + "\n")

    try:
        # Load config
        print("1. Loading configuration...")
        config = get_config()
        mongo_config = config.get_section('mongodb')

        host = mongo_config.get('host', 'mongodb://localhost:27017')
        database = mongo_config.get('database', 'reddit_trading')

        print(f"   ✓ Config loaded")
        print(f"   - Host: {host}")
        print(f"   - Database: {database}")
        print()

        # Import pymongo
        print("2. Importing pymongo library...")
        try:
            from pymongo import MongoClient
            print("   ✓ PyMongo imported successfully")
        except ImportError:
            print("   ✗ PyMongo not installed. Run: pip install pymongo")
            return False

        print()

        # Try to connect
        print("3. Connecting to MongoDB...")
        try:
            client = MongoClient(host, serverSelectionTimeoutMS=5000)
            print("   ✓ Client created")
        except Exception as e:
            print(f"   ✗ Failed to create client: {e}")
            return False

        print()

        # Test connection with ping
        print("4. Testing connection with ping...")
        try:
            result = client.admin.command('ping')
            print(f"   ✓ Ping successful!")
            print(f"   - Response: {result}")
        except Exception as e:
            print(f"   ✗ Ping failed: {e}")
            print()
            print("   MongoDB might not be running. Try:")
            print("   - Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
            print("   - Local: sudo systemctl start mongodb")
            print("   - macOS: brew services start mongodb-community")
            return False

        print()

        # Get database
        print("5. Accessing database...")
        try:
            db = client[database]
            print(f"   ✓ Database accessed: {db.name}")
        except Exception as e:
            print(f"   ✗ Failed to access database: {e}")
            return False

        print()

        # List collections
        print("6. Listing existing collections...")
        try:
            collections = db.list_collection_names()
            if collections:
                print(f"   ✓ Found {len(collections)} collections:")
                for col in collections:
                    print(f"     - {col}")
            else:
                print("   ⊘ No collections yet (this is normal on first run)")
        except Exception as e:
            print(f"   ✗ Failed to list collections: {e}")
            return False

        print()

        # Try to create a test collection
        print("7. Testing write operation (creating test collection)...")
        try:
            test_col = db['test_collection']
            result = test_col.insert_one({'test': 'document', 'timestamp': __import__('datetime').datetime.now()})
            print(f"   ✓ Insert successful!")
            print(f"   - Inserted ID: {result.inserted_id}")
        except Exception as e:
            print(f"   ✗ Insert failed: {e}")
            return False

        print()

        # Try to read back
        print("8. Testing read operation...")
        try:
            doc = test_col.find_one({'test': 'document'})
            if doc:
                print(f"   ✓ Read successful!")
                print(f"   - Found document: {doc}")
            else:
                print("   ✗ Document not found")
                return False
        except Exception as e:
            print(f"   ✗ Read failed: {e}")
            return False

        print()

        # Clean up test collection
        print("9. Cleaning up test data...")
        try:
            test_col.delete_many({})
            db.drop_collection('test_collection')
            print("   ✓ Cleanup successful")
        except Exception as e:
            print(f"   ⚠ Cleanup failed (non-critical): {e}")

        print()

        # Close connection
        client.close()
        print()
        print("="*70)
        print("✅ MONGODB TEST SUCCESSFUL!")
        print("="*70)
        print()
        print("Summary:")
        print("  ✓ PyMongo library working")
        print("  ✓ MongoDB connection successful")
        print("  ✓ Database accessible")
        print("  ✓ Can write to database")
        print("  ✓ Can read from database")
        print()
        print("Your MongoDB is READY to use! 🎉")
        print()

        return True

    except Exception as e:
        print("="*70)
        print("❌ MONGODB TEST FAILED")
        print("="*70)
        print()
        print(f"Error: {e}")
        print()

        import traceback
        print("Full traceback:")
        traceback.print_exc()

        print()
        print("Troubleshooting:")
        print("  1. Is MongoDB running?")
        print("     - Docker: docker ps | grep mongodb")
        print("     - Local: sudo systemctl status mongodb")
        print("     - macOS: brew services list | grep mongo")
        print()
        print("  2. Start MongoDB if not running:")
        print("     - Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        print("     - Linux: sudo systemctl start mongodb")
        print("     - macOS: brew services start mongodb-community")
        print()
        print("  3. Check connection string in config.json")
        print("     - Local: mongodb://localhost:27017")
        print("     - Atlas: mongodb+srv://username:password@cluster.mongodb.net")
        print()
        print("  4. Install pymongo if needed:")
        print("     - pip install pymongo")

        return False


def main():
    """Run the MongoDB test"""
    success = test_mongodb_connection()
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

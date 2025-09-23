#!/usr/bin/env python3
"""
MongoDB Index Creation Script
Run this once during deployment to create all required indexes
Usage: python deployment/create_indexes.py
"""
import sys
from pathlib import Path
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config.settings import db_config


def create_indexes():
    """Create all required indexes for the application"""
    try:
        if not db_config.mongodb_url:
            print("❌ MongoDB URL not configured")
            return False

        print("🔄 Connecting to MongoDB...")
        client = MongoClient(db_config.connection_string)

        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")

        db = client[db_config.mongodb_database_name]

        # Create indexes for users collection
        print("🔄 Creating indexes for 'users' collection...")
        users_collection = db.users

        indexes_created = []
        indexes_skipped = []

        # Index 1: Compound unique index for seller_id + email
        try:
            users_collection.create_index(
                [("seller_id", ASCENDING), ("email", ASCENDING)],
                unique=True,
                background=True,
                name="seller_email_unique"
            )
            indexes_created.append("seller_email_unique (compound unique)")
        except OperationFailure as e:
            if "already exists" in str(e):
                indexes_skipped.append("seller_email_unique (already exists)")
            else:
                print(f"⚠️ Failed to create seller_email_unique: {e}")

        # Index 2: seller_id for basic queries
        try:
            users_collection.create_index(
                [("seller_id", ASCENDING)],
                background=True,
                name="seller_id_idx"
            )
            indexes_created.append("seller_id_idx")
        except OperationFailure as e:
            if "already exists" in str(e):
                indexes_skipped.append("seller_id_idx (already exists)")
            else:
                print(f"⚠️ Failed to create seller_id_idx: {e}")

        # Index 3: email for lookup queries
        try:
            users_collection.create_index(
                [("email", ASCENDING)],
                background=True,
                name="email_idx"
            )
            indexes_created.append("email_idx")
        except OperationFailure as e:
            if "already exists" in str(e):
                indexes_skipped.append("email_idx (already exists)")
            else:
                print(f"⚠️ Failed to create email_idx: {e}")

        # Index 4: Compound index for listing/filtering queries
        try:
            users_collection.create_index(
                [("seller_id", ASCENDING), ("is_active", ASCENDING), ("created_at", DESCENDING)],
                background=True,
                name="seller_active_created_idx"
            )
            indexes_created.append("seller_active_created_idx (compound)")
        except OperationFailure as e:
            if "already exists" in str(e):
                indexes_skipped.append("seller_active_created_idx (already exists)")
            else:
                print(f"⚠️ Failed to create seller_active_created_idx: {e}")

        # Index 5: Text search index
        try:
            users_collection.create_index(
                [("email", TEXT), ("first_name", TEXT), ("last_name", TEXT)],
                background=True,
                name="search_text_idx"
            )
            indexes_created.append("search_text_idx (text search)")
        except OperationFailure as e:
            if "already exists" in str(e):
                indexes_skipped.append("search_text_idx (already exists)")
            else:
                print(f"⚠️ Failed to create search_text_idx: {e}")

        # Summary
        print("\n📊 Index Creation Summary:")
        print(f"✅ Created: {len(indexes_created)} indexes")
        for idx in indexes_created:
            print(f"   - {idx}")

        if indexes_skipped:
            print(f"⏭️  Skipped: {len(indexes_skipped)} indexes")
            for idx in indexes_skipped:
                print(f"   - {idx}")

        # List all indexes
        print("\n📋 All indexes in users collection:")
        for index in users_collection.list_indexes():
            print(f"   - {index['name']}: {index.get('key', {})}")

        client.close()
        print("\n🎉 Index creation completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False


if __name__ == "__main__":
    success = create_indexes()
    sys.exit(0 if success else 1)
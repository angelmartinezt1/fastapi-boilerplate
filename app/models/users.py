from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import get_database
from app.utils.logger import logger


class UserModel:
    """User database model for MongoDB operations"""

    COLLECTION_NAME = "users"

    @classmethod
    async def get_collection(cls) -> AsyncIOMotorCollection:
        """Get users collection with proper indexing"""
        db = get_database()
        collection = db[cls.COLLECTION_NAME]

        # Create indexes for high concurrency and performance
        await cls._ensure_indexes(collection)
        return collection

    @classmethod
    async def _ensure_indexes(cls, collection: AsyncIOMotorCollection):
        """Ensure required indexes exist for optimal performance"""
        try:
            # Compound index for seller_id + email (unique)
            await collection.create_index(
                [("seller_id", 1), ("email", 1)],
                unique=True,
                background=True,
                name="seller_email_unique"
            )

            # Index for seller_id queries
            await collection.create_index(
                [("seller_id", 1)],
                background=True,
                name="seller_id_idx"
            )

            # Index for email queries
            await collection.create_index(
                [("email", 1)],
                background=True,
                name="email_idx"
            )

            # Compound index for search queries
            await collection.create_index(
                [("seller_id", 1), ("is_active", 1), ("created_at", -1)],
                background=True,
                name="seller_active_created_idx"
            )

            # Text index for search functionality
            await collection.create_index(
                [("email", "text"), ("first_name", "text"), ("last_name", "text")],
                background=True,
                name="search_text_idx"
            )

        except Exception as e:
            logger.warning("Failed to create some indexes", extra={"extra_data": {"error": str(e)}})

    @staticmethod
    def create_document(seller_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user document"""
        now = datetime.now(timezone.utc)
        return {
            "_id": ObjectId(),
            "seller_id": seller_id,
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "phone_number": user_data.get("phone_number"),
            "is_active": user_data.get("is_active", True),
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def update_document(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create update document with only provided fields"""
        update_doc = {"updated_at": datetime.now(timezone.utc)}

        # Only include fields that are provided
        allowed_fields = ["email", "first_name", "last_name", "phone_number", "is_active"]
        for field in allowed_fields:
            if field in user_data and user_data[field] is not None:
                update_doc[field] = user_data[field]

        return {"$set": update_doc}

    @staticmethod
    def build_search_filter(seller_id: int, search: Optional[str] = None, is_active: Optional[bool] = None) -> Dict[str, Any]:
        """Build MongoDB filter for search queries"""
        filter_doc = {"seller_id": seller_id}

        if is_active is not None:
            filter_doc["is_active"] = is_active

        if search:
            # Use text search for better performance
            filter_doc["$text"] = {"$search": search}

        return filter_doc
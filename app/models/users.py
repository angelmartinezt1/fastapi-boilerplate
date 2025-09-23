from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.collection import Collection
from app.core.database import get_database


class UserModel:
    """User database model for MongoDB operations"""

    COLLECTION_NAME = "users"

    @classmethod
    def get_collection(cls) -> Collection:
        """Get users collection - indexes are pre-created via deployment script"""
        db = get_database()
        return db[cls.COLLECTION_NAME]

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
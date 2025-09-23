from typing import Optional, Tuple, List, Dict, Any
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from pymongo.collection import Collection
from pymongo import DESCENDING
from app.models.users import UserModel
from app.schemas.users import UserCreateRequest, UserUpdateRequest, UserResponse, UserListResponse
from app.schemas.common import PaginationInfo
from app.dependencies.common import PaginationParams, SearchParams
from app.utils.logger import logger
from app.core.database import run_in_executor


class UserService:
    """Service layer for user business logic"""

    @staticmethod
    async def create_user(seller_id: int, user_data: UserCreateRequest) -> UserResponse:
        """Create a new user"""
        try:
            def _create_user():
                collection = UserModel.get_collection()
                user_doc = UserModel.create_document(seller_id, user_data.model_dump())
                result = collection.insert_one(user_doc)
                user_doc["_id"] = result.inserted_id
                return user_doc

            user_doc = await run_in_executor(_create_user)

            logger.info("User created successfully", extra={"extra_data": {
                "user_id": str(user_doc["_id"]),
                "seller_id": seller_id,
                "email": user_data.email
            }})

            return UserResponse.from_dict(user_doc)

        except DuplicateKeyError:
            logger.warning("Duplicate user creation attempt", extra={"extra_data": {
                "seller_id": seller_id,
                "email": user_data.email
            }})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists for this seller"
            )
        except Exception as e:
            logger.error("Failed to create user", extra={"extra_data": {
                "seller_id": seller_id,
                "email": user_data.email,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

    @staticmethod
    async def create_user_fast(seller_id: int, user_data: UserCreateRequest) -> dict:
        """Create a new user returning raw document (fast path)"""
        try:
            def _create_user():
                collection = UserModel.get_collection()
                user_doc = UserModel.create_document(seller_id, user_data.model_dump())
                result = collection.insert_one(user_doc)
                user_doc["_id"] = result.inserted_id
                return user_doc

            user_doc = await run_in_executor(_create_user)

            logger.info("User created successfully", extra={"extra_data": {
                "user_id": str(user_doc["_id"]),
                "seller_id": seller_id,
                "email": user_data.email
            }})

            return user_doc

        except DuplicateKeyError:
            logger.warning("Duplicate user creation attempt", extra={"extra_data": {
                "seller_id": seller_id,
                "email": user_data.email
            }})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists for this seller"
            )
        except Exception as e:
            logger.error("Failed to create user", extra={"extra_data": {
                "seller_id": seller_id,
                "email": user_data.email,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

    @staticmethod
    async def get_user_by_id(seller_id: int, user_id: str) -> UserResponse:
        """Get user by ID"""
        try:
            def _get_user():
                collection = UserModel.get_collection()
                return collection.find_one({
                    "_id": ObjectId(user_id),
                    "seller_id": seller_id
                })

            user_doc = await run_in_executor(_get_user)

            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return UserResponse.from_dict(user_doc)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get user", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user"
            )

    @staticmethod
    async def get_user_by_id_fast(seller_id: int, user_id: str) -> dict:
        """Get user by ID returning raw document (fast path)"""
        try:
            def _get_user():
                collection = UserModel.get_collection()
                return collection.find_one({
                    "_id": ObjectId(user_id),
                    "seller_id": seller_id
                })

            user_doc = await run_in_executor(_get_user)

            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return user_doc

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get user", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user"
            )

    @staticmethod
    async def update_user(seller_id: int, user_id: str, user_data: UserUpdateRequest) -> UserResponse:
        """Update user by ID"""
        try:
            collection = await UserModel.get_collection()

            # Only update fields that are provided
            update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}

            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields provided for update"
                )

            update_doc = UserModel.update_document(update_data)

            result = await collection.find_one_and_update(
                {"_id": ObjectId(user_id), "seller_id": seller_id},
                update_doc,
                return_document=True
            )

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info("User updated successfully", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id,
                "updated_fields": list(update_data.keys())
            }})

            return UserResponse.from_dict(result)

        except HTTPException:
            raise
        except DuplicateKeyError:
            logger.warning("Duplicate email in user update", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id
            }})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists for this seller"
            )
        except Exception as e:
            logger.error("Failed to update user", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

    @staticmethod
    async def delete_user(seller_id: int, user_id: str) -> bool:
        """Delete user by ID (soft delete by setting is_active=False)"""
        try:
            collection = await UserModel.get_collection()

            result = await collection.find_one_and_update(
                {"_id": ObjectId(user_id), "seller_id": seller_id},
                UserModel.update_document({"is_active": False}),
                return_document=True
            )

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info("User soft deleted successfully", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id
            }})

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to delete user", extra={"extra_data": {
                "user_id": user_id,
                "seller_id": seller_id,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

    @staticmethod
    async def list_users(
        seller_id: int,
        pagination: PaginationParams,
        search: SearchParams
    ) -> UserListResponse:
        """List users with pagination and search"""
        try:
            def _list_users():
                collection = UserModel.get_collection()

                # Build filter
                filter_doc = UserModel.build_search_filter(
                    seller_id=seller_id,
                    search=search.search,
                    is_active=search.is_active
                )

                # Get total count
                total_count = collection.count_documents(filter_doc)

                # Get users with sorting and pagination
                users = list(collection.find(filter_doc)
                           .sort("created_at", DESCENDING)
                           .skip(pagination.skip)
                           .limit(pagination.page_size))

                return users, total_count

            users, total_count = await run_in_executor(_list_users)

            # Convert to response objects
            user_responses = [UserResponse.from_dict(user) for user in users]

            # Calculate pagination info
            total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
            has_next = pagination.page < total_pages
            has_previous = pagination.page > 1

            pagination_info = PaginationInfo(
                total_count=total_count,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )

            return UserListResponse(
                data=user_responses,
                pagination=pagination_info
            )

        except Exception as e:
            logger.error("Failed to list users", extra={"extra_data": {
                "seller_id": seller_id,
                "page": pagination.page,
                "error": str(e)
            }})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve users"
            )

    @staticmethod
    async def get_user_by_email(seller_id: int, email: str) -> Optional[UserResponse]:
        """Get user by email (for internal use)"""
        try:
            collection = await UserModel.get_collection()

            user_doc = await collection.find_one({
                "seller_id": seller_id,
                "email": email
            })

            return UserResponse.from_dict(user_doc) if user_doc else None

        except Exception as e:
            logger.error("Failed to get user by email", extra={"extra_data": {
                "seller_id": seller_id,
                "email": email,
                "error": str(e)
            }})
            return None
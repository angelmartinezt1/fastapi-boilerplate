from typing import Optional
from fastapi import HTTPException, status, Path, Query, Depends
from bson import ObjectId
from bson.errors import InvalidId


async def validate_seller_id(
    seller_id: int = Path(..., gt=0, description="Seller unique identifier")
) -> int:
    """Validate seller_id path parameter"""
    return seller_id


async def validate_user_id(
    user_id: str = Path(..., description="User unique identifier")
) -> str:
    """Validate user_id path parameter and ensure it's a valid ObjectId"""
    try:
        ObjectId(user_id)
        return user_id
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


class PaginationParams:
    """Reusable pagination parameters"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size


class SearchParams:
    """Reusable search parameters"""

    def __init__(
        self,
        search: Optional[str] = Query(None, min_length=2, description="Search term"),
        is_active: Optional[bool] = Query(None, description="Filter by active status")
    ):
        self.search = search
        self.is_active = is_active


async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """Dependency to get pagination parameters"""
    return PaginationParams(page=page, page_size=page_size)


async def get_search_params(
    search: Optional[str] = Query(None, min_length=2, description="Search term"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
) -> SearchParams:
    """Dependency to get search parameters"""
    return SearchParams(search=search, is_active=is_active)
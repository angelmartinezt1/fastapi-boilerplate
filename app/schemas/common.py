from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationInfo(BaseModel):
    """Schema for pagination information"""
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response with data and pagination separated"""
    metadata: dict = Field(..., description="Response metadata")
    data: T = Field(..., description="Response data")
    pagination: PaginationInfo = Field(..., description="Pagination information")
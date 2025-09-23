from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId


class UserCreateRequest(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=2, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=2, max_length=50, description="User last name")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, description="User phone number")
    is_active: bool = Field(default=True, description="Whether the user is active")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, and plus sign')
        return v

    model_config = {"str_strip_whitespace": True}


class UserUpdateRequest(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    first_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User first name")
    last_name: Optional[str] = Field(None, min_length=2, max_length=50, description="User last name")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, description="User phone number")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Phone number must contain only digits, spaces, hyphens, and plus sign')
        return v

    model_config = {"str_strip_whitespace": True}


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., description="User unique identifier")
    seller_id: int = Field(..., description="Seller identifier")
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    phone_number: Optional[str] = Field(None, description="User phone number")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")

    @classmethod
    def from_dict(cls, data: dict):
        """Convert MongoDB document to UserResponse"""
        return cls(
            id=str(data["_id"]),
            seller_id=data["seller_id"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data.get("phone_number"),
            is_active=data.get("is_active", True),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: list[UserResponse] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class UserSearchQuery(BaseModel):
    """Schema for user search query parameters"""
    search: Optional[str] = Field(None, min_length=2, description="Search term for email, first_name, or last_name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    model_config = {"str_strip_whitespace": True}
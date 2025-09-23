from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId
from app.schemas.common import PaginationInfo


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

    model_config = {
        "str_strip_whitespace": True,
        # Performance optimizations
        "validate_assignment": False,  # Skip validation on assignment
        "validate_default": False,     # Skip default value validation
        "use_list": True,             # Faster list processing
        "arbitrary_types_allowed": True # Allow any types without validation
    }


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

    model_config = {
        "str_strip_whitespace": True,
        # Performance optimizations
        "validate_assignment": False,
        "validate_default": False,
        "use_list": True,
        "arbitrary_types_allowed": True
    }


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

    model_config = {
        # Performance optimizations for response serialization
        "validate_assignment": False,
        "validate_default": False,
        "use_list": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            # Fast datetime serialization
            datetime: lambda v: v.isoformat() if v else None
        }
    }

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

    @classmethod
    def from_dict_fast(cls, data: dict) -> dict:
        """Ultra-fast serialization bypassing Pydantic completely"""
        return {
            "id": str(data["_id"]),
            "seller_id": data["seller_id"],
            "email": data["email"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone_number": data.get("phone_number"),
            "is_active": data.get("is_active", True),
            "created_at": data["created_at"].isoformat() if data["created_at"] else None,
            "updated_at": data["updated_at"].isoformat() if data["updated_at"] else None
        }


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    data: list[UserResponse] = Field(..., description="List of users")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class UserSearchQuery(BaseModel):
    """Schema for user search query parameters"""
    search: Optional[str] = Field(None, min_length=2, description="Search term for email, first_name, or last_name")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    model_config = {
        "str_strip_whitespace": True,
        # Performance optimizations
        "validate_assignment": False,
        "validate_default": False,
        "use_list": True,
        "arbitrary_types_allowed": True
    }
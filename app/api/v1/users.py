from fastapi import APIRouter, status, Depends
from app.schemas.response import StandardResponse
from app.schemas.users import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse
)
from app.services.users import UserService
from app.dependencies.common import (
    validate_seller_id,
    validate_user_id,
    get_pagination_params,
    get_search_params,
    PaginationParams,
    SearchParams
)
from app.utils.response import create_success_response

router = APIRouter()


@router.post(
    "/api/{seller_id}/users",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
    tags=["Users"],
    summary="Create a new user",
    description="Create a new user for the specified seller"
)
async def create_user(
    user_data: UserCreateRequest,
    seller_id: int = Depends(validate_seller_id)
) -> StandardResponse[UserResponse]:
    """Create a new user"""
    user = await UserService.create_user(seller_id, user_data)

    return create_success_response(
        data=user,
        message="User created successfully"
    )


@router.get(
    "/api/{seller_id}/users/{user_id}",
    response_model=StandardResponse[UserResponse],
    response_model_exclude_none=True,
    tags=["Users"],
    summary="Get user by ID",
    description="Retrieve a specific user by their ID"
)
async def get_user(
    seller_id: int = Depends(validate_seller_id),
    user_id: str = Depends(validate_user_id)
) -> StandardResponse[UserResponse]:
    """Get user by ID"""
    user = await UserService.get_user_by_id(seller_id, user_id)

    return create_success_response(
        data=user,
        message="User retrieved successfully"
    )


@router.put(
    "/api/{seller_id}/users/{user_id}",
    response_model=StandardResponse[UserResponse],
    response_model_exclude_none=True,
    tags=["Users"],
    summary="Update user",
    description="Update an existing user's information"
)
async def update_user(
    user_data: UserUpdateRequest,
    seller_id: int = Depends(validate_seller_id),
    user_id: str = Depends(validate_user_id)
) -> StandardResponse[UserResponse]:
    """Update user"""
    user = await UserService.update_user(seller_id, user_id, user_data)

    return create_success_response(
        data=user,
        message="User updated successfully"
    )


@router.delete(
    "/api/{seller_id}/users/{user_id}",
    response_model=StandardResponse[dict],
    response_model_exclude_none=True,
    tags=["Users"],
    summary="Delete user",
    description="Soft delete a user (sets is_active to false)"
)
async def delete_user(
    seller_id: int = Depends(validate_seller_id),
    user_id: str = Depends(validate_user_id)
) -> StandardResponse[dict]:
    """Delete user (soft delete)"""
    await UserService.delete_user(seller_id, user_id)

    return create_success_response(
        data={"deleted": True},
        message="User deleted successfully"
    )


@router.get(
    "/api/{seller_id}/users",
    response_model=StandardResponse[UserListResponse],
    response_model_exclude_none=True,
    tags=["Users"],
    summary="List users",
    description="Get a paginated list of users with optional search and filtering"
)
async def list_users(
    seller_id: int = Depends(validate_seller_id),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: SearchParams = Depends(get_search_params)
) -> StandardResponse[UserListResponse]:
    """List users with pagination and search"""
    users = await UserService.list_users(seller_id, pagination, search)

    return create_success_response(
        data=users,
        message="Users retrieved successfully"
    )
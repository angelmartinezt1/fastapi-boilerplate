from fastapi import APIRouter
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from pydantic import BaseModel

router = APIRouter()


class SellerData(BaseModel):
    seller_id: int


@router.get("/api/{seller_id}", response_model=StandardResponse[SellerData], response_model_exclude_none=True)
async def get_seller(seller_id: int):
    """
    Get seller by ID
    """
    data = SellerData(seller_id=seller_id)

    return create_success_response(
        data=data,
        message="Seller retrieved successfully"
    )
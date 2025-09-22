from fastapi import APIRouter
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from pydantic import BaseModel

router = APIRouter()


class WelcomeData(BaseModel):
    message: str
    api_version: str


@router.get("/", response_model=StandardResponse[WelcomeData])
async def root():
    data = WelcomeData(
        message="Hola mundo!",
        api_version="1.0.0"
    )

    return create_success_response(
        data=data,
        message="Welcome message retrieved successfully"
    )
from fastapi import APIRouter
from ulid import ULID
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from pydantic import BaseModel

router = APIRouter()


class UlidData(BaseModel):
    ulid: str


@router.get("/ulid", response_model=StandardResponse[UlidData])
async def ulid():
    generated_ulid = str(ULID())
    data = UlidData(ulid=generated_ulid)

    return create_success_response(
        data=data,
        message="ULID generated successfully"
    )
from fastapi import APIRouter
from ulid import ULID

router = APIRouter()


@router.get("/ulid")
async def ulid():
    usuario = str(ULID())
    return {"ulid": usuario}
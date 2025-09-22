from fastapi import APIRouter
from pydantic import BaseModel
from ulid import ULID

router = APIRouter()


class Usuario(BaseModel):
    ulid: ULID
    nombre: str
    email: str


@router.post("/usuarios")
async def crear_usuario(usuario: Usuario):
    return {"usuario": usuario}
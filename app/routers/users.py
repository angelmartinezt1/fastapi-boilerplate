from fastapi import APIRouter
from pydantic import BaseModel
from ulid import ULID
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response

router = APIRouter()


class Usuario(BaseModel):
    ulid: ULID
    nombre: str
    email: str


class UsuarioResponse(BaseModel):
    usuario: Usuario


@router.post("/usuarios", response_model=StandardResponse[UsuarioResponse])
async def crear_usuario(usuario: Usuario):
    data = UsuarioResponse(usuario=usuario)

    return create_success_response(
        data=data,
        message="Usuario created successfully"
    )
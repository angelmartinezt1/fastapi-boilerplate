from fastapi import APIRouter
from pydantic import BaseModel
from ulid import ULID
from app.schemas.response import StandardResponse
from app.utils.response import create_success_response
from app.utils.logger import logger

router = APIRouter()


class Usuario(BaseModel):
    ulid: ULID
    nombre: str
    email: str


class UsuarioResponse(BaseModel):
    usuario: Usuario


@router.post("/usuarios", response_model=StandardResponse[UsuarioResponse])
async def crear_usuario(usuario: Usuario):
    logger.info("Creating new user", extra={"extra_data": {
        "endpoint": "/usuarios",
        "user_ulid": str(usuario.ulid),
        "user_name": usuario.nombre
    }})

    data = UsuarioResponse(usuario=usuario)

    logger.info("User created successfully", extra={"extra_data": {
        "user_ulid": str(usuario.ulid),
        "user_name": usuario.nombre,
        "user_email": usuario.email
    }})

    return create_success_response(
        data=data,
        message="Usuario created successfully"
    )
from fastapi import APIRouter, Request, Depends
from app.schemas.response import StandardResponse
from app.middleware.auth import get_auth_context, get_current_user_id, get_current_user_email, get_current_store
from app.utils.response import create_success_response
from typing import Dict, Any

router = APIRouter()


@router.get(
    "/me",
    response_model=StandardResponse[Dict[str, Any]],
    tags=["Authentication"],
    summary="Get current user context",
    description="Returns the Lambda authorizer context for the authenticated user"
)
async def get_me(request: Request):
    """
    Endpoint para obtener el contexto del usuario autenticado
    Solo funciona en Lambda con Lambda Authorizer configurado
    """
    # Obtener contexto completo del authorizer
    auth_context = get_auth_context(request)

    # Obtener campos específicos usando helpers
    user_id = get_current_user_id(request)
    user_email = get_current_user_email(request)
    current_store = get_current_store(request)

    # Estructura de respuesta con información del usuario
    user_info = {
        "user_id": user_id,
        "email": user_email,
        "current_store": current_store,
        "access_type": getattr(request.state, "access_type", None),
        "scope": getattr(request.state, "scope", None),
        "full_context": auth_context
    }

    return create_success_response(
        data=user_info,
        message="User context retrieved successfully"
    )
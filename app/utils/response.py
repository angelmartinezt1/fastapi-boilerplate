from typing import TypeVar
from datetime import datetime, timezone
from app.schemas.response import StandardResponse, ResponseMetadata, ErrorResponse, ErrorDetail
from app.schemas.common import PaginationInfo
from app.config.settings import app_config

T = TypeVar('T')


def create_success_response(
    data: T,
    message: str
) -> StandardResponse[T]:
    """
    Crea una respuesta exitosa estandarizada

    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje descriptivo

    Returns:
        StandardResponse con formato estandarizado
    """
    metadata = ResponseMetadata(
        success=True,
        message=message
    )

    return StandardResponse(metadata=metadata, data=data)


def create_error_response(
    message: str,
    errors: list[ErrorDetail] = None
) -> ErrorResponse:
    """
    Crea una respuesta de error estandarizada

    Args:
        message: Mensaje de error general
        errors: Lista de errores específicos

    Returns:
        ErrorResponse con formato estandarizado
    """
    metadata = ResponseMetadata(
        success=False,
        message=message
    )

    if errors is None:
        errors = []

    return ErrorResponse(metadata=metadata, errors=errors)


def create_paginated_response(
    data: list[T],
    pagination: PaginationInfo,
    message: str = "Data retrieved successfully"
):
    """
    Crea una respuesta paginada estandarizada

    Args:
        data: Lista de datos
        pagination: Información de paginación
        message: Mensaje descriptivo

    Returns:
        Respuesta con formato data[] y pagination{}
    """
    if app_config.validate_responses:
        # Ruta con validación completa
        metadata = ResponseMetadata(
            success=True,
            message=message
        )
        return {
            "metadata": metadata.model_dump(),
            "data": data,
            "pagination": pagination.model_dump()
        }
    else:
        # Ruta rápida sin validación
        return {
            "metadata": {
                "success": True,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "data": data,
            "pagination": pagination.model_dump()
        }


def create_fast_response(
    data: T,
    message: str
):
    """
    Crea una respuesta rápida sin validación Pydantic

    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje descriptivo

    Returns:
        Dict con formato de respuesta estándar
    """
    return {
        "metadata": {
            "success": True,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "data": data
    }



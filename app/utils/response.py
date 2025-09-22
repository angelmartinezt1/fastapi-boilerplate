from typing import TypeVar
from app.schemas.response import StandardResponse, ResponseMetadata, ErrorResponse, ErrorDetail

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



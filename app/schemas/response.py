from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class ResponseMetadata(BaseModel):
    """Metadata para respuestas estandarizadas"""
    success: bool = Field(default=True, description="Indica si la operación fue exitosa")
    message: str = Field(description="Mensaje descriptivo de la operación")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Timestamp de la respuesta")


class StandardResponse(BaseModel, Generic[T]):
    """Respuesta estandarizada para toda la API"""
    metadata: ResponseMetadata = Field(description="Metadatos de la respuesta")
    data: T = Field(description="Datos de la respuesta")

    model_config = {"populate_by_name": True, "exclude_none": True}


class ErrorDetail(BaseModel):
    """Detalle de error"""
    code: str = Field(description="Código del error")
    field: Optional[str] = Field(default=None, description="Campo que causó el error")
    message: str = Field(description="Mensaje del error")


class ErrorResponse(BaseModel):
    """Respuesta de error estandarizada"""
    metadata: ResponseMetadata = Field(description="Metadatos de la respuesta")
    errors: list[ErrorDetail] = Field(description="Lista de errores")

    model_config = {"populate_by_name": True, "exclude_none": True}
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any
import json
from app.config.settings import app_config
from app.utils.logger import logger


class LambdaAuthorizerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que procesa el contexto del Lambda Authorizer
    Solo funciona en entorno Lambda
    """

    def __init__(self, app):
        super().__init__(app)
        self.protected_paths = [
            # "/api/",  # Todas las rutas de API requieren autenticación
            "/me"  # Endpoint de perfil de usuario
        ]
        self.excluded_paths = ["/health", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next):
        # Solo aplicar en Lambda
        if not app_config.is_lambda:
            logger.debug(
                "Skipping Lambda authorizer middleware (not in Lambda environment)"
            )
            return await call_next(request)

        path = request.url.path

        # Excluir rutas públicas
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return await call_next(request)

        # Verificar si la ruta requiere autenticación
        requires_auth = any(
            path.startswith(protected) for protected in self.protected_paths
        )

        if requires_auth:
            # Debug: Log request scope info
            logger.debug(
                "Processing protected route",
                extra={
                    "extra_data": {
                        "path": path,
                        "method": request.method,
                        "scope_type": type(request.scope).__name__,
                        "scope_keys": (
                            list(request.scope.keys())
                            if hasattr(request.scope, "keys")
                            else "N/A"
                        ),
                    }
                },
            )

            # Extraer contexto del Lambda Authorizer
            auth_context = self._extract_authorizer_context(request)

            if not auth_context:
                logger.warning(
                    "Missing Lambda authorizer context",
                    extra={
                        "extra_data": {
                            "path": path,
                            "method": request.method,
                            "headers": dict(request.headers),
                        }
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "metadata": {
                            "success": False,
                            "message": "Authentication required",
                            "timestamp": None,
                        },
                        "errors": [
                            {
                                "field": "authorization",
                                "message": "Missing or invalid authorization context",
                            }
                        ],
                    },
                )

            # Validar contexto requerido
            validation_error = self._validate_context(auth_context)
            if validation_error:
                logger.warning(
                    "Invalid Lambda authorizer context",
                    extra={
                        "extra_data": {
                            "path": path,
                            "method": request.method,
                            "validation_error": validation_error,
                            "context": auth_context,
                        }
                    },
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "metadata": {
                            "success": False,
                            "message": "Access forbidden",
                            "timestamp": None,
                        },
                        "errors": [
                            {"field": "authorization", "message": validation_error}
                        ],
                    },
                )

            # Agregar contexto a la request para uso en endpoints
            request.state.auth_context = auth_context
            request.state.user_id = auth_context.get("sub")
            request.state.user_email = auth_context.get("email")
            request.state.current_store = auth_context.get("current_store")
            request.state.access_type = auth_context.get("accessType")
            request.state.scope = auth_context.get("scope")

            logger.info(
                "Lambda authorizer context validated",
                extra={
                    "extra_data": {
                        "path": path,
                        "method": request.method,
                        "user_id": auth_context.get("sub"),
                        "email": auth_context.get("email"),
                        "access_type": auth_context.get("accessType"),
                    }
                },
            )

        return await call_next(request)

    def _extract_authorizer_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Extrae el contexto del Lambda Authorizer desde el evento de API Gateway
        """
        try:
            # Para REST API, el contexto está en request.scope["aws.event"]["requestContext"]["authorizer"]
            # Para HTTP API v2, está en request.scope["aws.event"]["requestContext"]["authorizer"]["lambda"]

            # Método 1: Extraer desde request.scope (Mangum)
            if hasattr(request.scope, "get") and "aws.event" in request.scope:
                aws_event = request.scope["aws.event"]
            else:
                # Método 2: Buscar en request.scope directamente
                aws_event = getattr(request.scope, "get", lambda k, d=None: None)(
                    "aws.event"
                )

            if not aws_event:
                # Método 3: Buscar en diferentes ubicaciones de request
                for attr in ["aws_event", "_aws_event", "event"]:
                    aws_event = getattr(request, attr, None)
                    if aws_event:
                        break

            if not aws_event:
                logger.debug(
                    "No AWS event found in request scope",
                    extra={
                        "extra_data": {
                            "scope_keys": (
                                list(request.scope.keys())
                                if hasattr(request.scope, "keys")
                                else "N/A"
                            ),
                            "path": request.url.path,
                        }
                    },
                )
                return self._extract_from_headers(request)

            request_context = aws_event.get("requestContext", {})
            authorizer = request_context.get("authorizer", {})

            logger.debug(
                "Found authorizer context",
                extra={
                    "extra_data": {
                        "authorizer_keys": (
                            list(authorizer.keys()) if authorizer else []
                        ),
                        "request_context_keys": list(request_context.keys()),
                        "path": request.url.path,
                    }
                },
            )

            # REST API: contexto directo en authorizer
            if authorizer and "lambda" not in authorizer:
                # Filtrar campos de sistema de API Gateway
                context = {}
                for key, value in authorizer.items():
                    if not key.startswith("principalId") and key not in [
                        "policy",
                        "context",
                    ]:
                        context[key] = value

                # Si hay un campo 'context', usar ese
                if "context" in authorizer:
                    context.update(authorizer["context"])

                if context:
                    return context

            # HTTP API v2: contexto en authorizer.lambda
            if "lambda" in authorizer:
                return authorizer["lambda"]

            # Fallback: todo el objeto authorizer si tiene datos útiles
            if authorizer and len(authorizer) > 1:  # Más que solo principalId
                return authorizer

            return None

        except Exception as e:
            logger.error(
                "Failed to extract Lambda authorizer context",
                extra={
                    "extra_data": {
                        "error": str(e),
                        "path": request.url.path,
                        "error_type": type(e).__name__,
                    }
                },
            )
            return None

    def _extract_from_headers(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Fallback: extraer contexto desde headers personalizados
        """
        try:
            # API Gateway puede pasar el contexto en headers personalizados
            context_header = request.headers.get("x-apigateway-context")
            if context_header:
                return json.loads(context_header)

            # Extraer campos individuales de headers
            auth_context = {}

            # Headers estándar que API Gateway puede pasar
            mapping = {
                "x-apigateway-user-id": "sub",
                "x-apigateway-user-email": "email",
                "x-apigateway-access-type": "accessType",
                "x-apigateway-scope": "scope",
                "x-apigateway-current-store": "current_store",
                "x-apigateway-issuer": "iss",
                "x-apigateway-azp": "azp",
            }

            for header_name, context_key in mapping.items():
                value = request.headers.get(header_name)
                if value:
                    auth_context[context_key] = value

            return auth_context if auth_context else None

        except Exception as e:
            logger.error(
                "Failed to extract context from headers",
                extra={"extra_data": {"error": str(e)}},
            )
            return None

    def _validate_context(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Valida que el contexto tenga los campos requeridos
        """
        required_fields = ["sub", "email"]

        for field in required_fields:
            if not context.get(field):
                return f"Missing required field: {field}"

        # Validaciones adicionales
        if not isinstance(context.get("email"), str) or "@" not in context.get(
            "email", ""
        ):
            return "Invalid email format"

        return None


def get_auth_context(request: Request) -> Dict[str, Any]:
    """
    Helper function para obtener el contexto de autenticación desde la request
    """
    return getattr(request.state, "auth_context", {})


def get_current_user_id(request: Request) -> Optional[str]:
    """
    Helper function para obtener el ID del usuario actual
    """
    return getattr(request.state, "user_id", None)


def get_current_user_email(request: Request) -> Optional[str]:
    """
    Helper function para obtener el email del usuario actual
    """
    return getattr(request.state, "user_email", None)


def get_current_store(request: Request) -> Optional[str]:
    """
    Helper function para obtener la tienda actual
    """
    return getattr(request.state, "current_store", None)

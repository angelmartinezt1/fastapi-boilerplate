"""
Custom exception handlers for better error logging and response formatting
"""
import json
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.utils.logger import logger
from app.utils.response import create_error_response
from app.schemas.response import ErrorDetail


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    try:
        # Get request body for logging if available
        request_body = None
        if hasattr(request, "_body"):
            try:
                request_body = json.loads(request._body.decode())
            except Exception:
                request_body = "Could not parse request body"

        # Extract validation errors
        validation_errors = []
        error_details = []

        for error in exc.errors():
            field_name = ".".join(str(loc) for loc in error["loc"]) if error.get("loc") else "unknown"
            error_msg = error.get("msg", "Validation error")
            error_input = error.get("input")

            validation_errors.append({
                "field": field_name,
                "message": error_msg,
                "type": error.get("type"),
                "input": error_input
            })

            error_details.append(ErrorDetail(
                code="validation_error",
                field=field_name,
                message=f"{error_msg} (received: {error_input})" if error_input is not None else error_msg
            ))

        # Log comprehensive validation error
        logger.warning("Request validation failed", extra={"extra_data": {
            "method": request.method,
            "url": str(request.url),
            "path_params": dict(request.path_params),
            "query_params": dict(request.query_params),
            "request_body": request_body,
            "validation_errors": validation_errors,
            "total_errors": len(validation_errors)
        }})

        # Create standardized error response
        error_response = create_error_response(
            message="Request validation failed",
            errors=error_details
        )

        return JSONResponse(
            status_code=422,
            content=error_response.model_dump()
        )

    except Exception as log_error:
        logger.error("Failed to log validation error", extra={"extra_data": {
            "log_error": str(log_error),
            "original_validation_errors": str(exc.errors())
        }})

        # Fallback to default response
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with logging"""
    logger.warning("HTTP exception occurred", extra={"extra_data": {
        "method": request.method,
        "url": str(request.url),
        "status_code": exc.status_code,
        "detail": exc.detail
    }})

    # Create standardized error response
    error_response = create_error_response(
        message=str(exc.detail),
        errors=[ErrorDetail(
            code=f"http_{exc.status_code}",
            field=None,
            message=str(exc.detail)
        )]
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with logging"""
    logger.error("Unexpected error occurred", extra={"extra_data": {
        "method": request.method,
        "url": str(request.url),
        "error": str(exc),
        "error_type": type(exc).__name__
    }})

    # Create standardized error response
    error_response = create_error_response(
        message="Internal server error",
        errors=[ErrorDetail(
            code="internal_error",
            field=None,
            message="An unexpected error occurred"
        )]
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )
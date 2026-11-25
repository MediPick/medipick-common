"""
MediPick Core — Custom Exceptions & Global Exception Handlers
Unified exception classes and FastAPI global error handlers.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class MediPickException(Exception):
    """
    Raise this anywhere in the application to return a structured API error.
    Example:
        raise MediPickException("OTP_INVALID", 400, "The OTP you entered is incorrect.")
    """
    def __init__(
        self,
        code: str,
        status_code: int,
        message: str,
        fields: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.status_code = status_code
        self.message = message
        self.fields = fields
        super().__init__(message)


def error_json(
    code: str,
    message: str,
    status_code: int,
    fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Standard MediPick JSON error response payload dictionary."""
    body: dict[str, Any] = {
        "success": False,
        "error": code,
        "message": message,
        "statusCode": status_code,
    }
    if fields:
        body["fields"] = fields
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers onto a FastAPI app instance."""

    @app.exception_handler(MediPickException)
    async def medipick_exception_handler(
        request: Request, exc: MediPickException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_json(exc.code, exc.message, exc.status_code, exc.fields),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields: dict[str, str] = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            fields[field] = error["msg"]

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_json(
                "VALIDATION_ERROR",
                "One or more fields failed validation. Please correct the highlighted entries.",
                status.HTTP_400_BAD_REQUEST,
                fields,
            ),
        )

    @app.exception_handler(ExpiredSignatureError)
    async def expired_jwt_exception_handler(
        request: Request, exc: ExpiredSignatureError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_json(
                "TOKEN_EXPIRED",
                "Your session has expired. Please sign in again.",
                status.HTTP_401_UNAUTHORIZED,
            ),
        )

    @app.exception_handler(JWTError)
    async def jwt_exception_handler(
        request: Request, exc: JWTError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_json(
                "TOKEN_INVALID",
                "Invalid or expired authentication token.",
                status.HTTP_401_UNAUTHORIZED,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException | StarletteHTTPException
    ) -> JSONResponse:
        code_map = {
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "REQUEST_ENTITY_TOO_LARGE",
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "UNSUPPORTED_MEDIA_TYPE",
            status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
        }
        error_code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        message = exc.detail if isinstance(exc.detail, str) else "A request error occurred."
        return JSONResponse(
            status_code=exc.status_code,
            content=error_json(error_code, message, exc.status_code),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled server error while processing %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_json(
                "INTERNAL_ERROR",
                "An unexpected server error occurred. Please try again later or contact support.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )

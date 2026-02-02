import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception class for all exceptions raised by this module."""
    def __init__(
            self,
            status_code: int,
            error: str,
            message: str,
            details: dict | None = None,
    ):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details


class DuplicateEmailException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error="DUPLICATE_EMAIL",
            message="Email already registered",
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            error="INVALID_CREDENTIALS",
            message="Invalid email or password",
        )


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=404,
            error="NOT_FOUND",
            message=f"{resource} not found",
        )


class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            error="TOKEN_EXPIRED",
            message="Token has expired",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            error="INVALID_TOKEN",
            message="Invalid or malformed token",
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.error,
            "message": exc.message,
            "details": exc.details or {},
        },
    )


async def validation_exception_handler(
        _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": exc.errors()},
        },
    )


async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )

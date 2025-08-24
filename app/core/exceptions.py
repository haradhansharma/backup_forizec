# app/core/exceptions.py

from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def want_html(request: Request) -> bool:
    """Check if the request wants HTML response."""
    return "text/html" in request.headers.get("accept", "").lower()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error at: {request.url}: {exc.errors()}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Validation error occurred.</h1><pre>" + str(exc.errors()) + "</pre>",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error at: {request.url}: {exc.detail}")
    if want_html(request):
        return HTMLResponse(
            content=f"<h1>{exc.status_code} Error</h1><p>{exc.detail}</p>",
            status_code=exc.status_code,
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle integrity errors."""
    logger.error(f"Integrity error at: {request.url}: {exc.orig}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Integrity error occurred.</h1><pre>" + str(exc.orig) + "</pre>",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc.orig)})


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unexpected error at: {request.url}: {exc}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Internal Server Error</h1><p>An unexpected error occurred.</p>",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )

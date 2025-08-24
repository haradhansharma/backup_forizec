from fastapi import Request, status, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from app.core.logging_config import get_logger
from app.core.config import settings
import traceback
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = get_logger(__name__)


def want_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "").lower()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error at: {request.url}: {exc.errors()}")
    if want_html(request):
        return HTMLResponse(
            content=f"<h1>422 Validation Error</h1><pre>{exc.errors()}</pre>",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Covers FastAPI.HTTPException and Starlette.HTTPException generically."""
    logger.error(f"HTTP error at: {request.url}: {exc.detail}")
    if want_html(request):
        return HTMLResponse(
            content=f"<h1>{exc.status_code} Error</h1><p>{exc.detail}</p>",
            status_code=exc.status_code,
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Special handling for common Starlette exceptions (404, 405, 413)."""
    if exc.status_code == 404:
        logger.warning(f"Not found: {request.url}")
        content = "<h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p>"
    elif exc.status_code == 405:
        logger.warning(f"Method Not Allowed: {request.method} {request.url}")
        content = f"<h1>405 - Method Not Allowed</h1><p>{request.method} not allowed here.</p>"
    elif exc.status_code == 413:
        logger.warning(f"Payload too large at {request.url}")
        content = "<h1>413 - Payload Too Large</h1><p>Your upload exceeds the allowed size.</p>"
    else:
        return await http_exception_handler(request, exc)  # fallback

    if want_html(request):
        return HTMLResponse(content=content, status_code=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail or content})


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error at: {request.url}: {exc.orig}")
    if want_html(request):
        return HTMLResponse(
            content=f"<h1>Integrity error occurred</h1><pre>{exc.orig}</pre>",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc.orig)})


async def db_operational_error_handler(request: Request, exc: OperationalError):
    logger.critical(f"Database connection error: {exc}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Database Error</h1><p>Cannot connect to database.</p>",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"detail": "Database unavailable"}
    )


async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    logger.error(f"File not found: {exc}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>File Not Found</h1><p>The requested file could not be located.</p>",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "File not found"})


async def server_error_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error at {request.url}: {exc}", exc_info=True)
    if want_html(request):
        return HTMLResponse(
            content="<h1>500 - Internal Server Error</h1><p>Something went wrong.</p>",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc) if settings.DEBUG else "Internal Server Error",
            "traceback": traceback.format_exc() if settings.DEBUG else None,
        },
    )


async def permission_exception_handler(request: Request, exc: PermissionError):
    logger.error(f"Permission error at: {request.url} - {exc}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Permission Denied</h1><p>You do not have access to this resource.</p>",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied. You do not have access to this resource."},
    )


async def timeout_exception_handler(request: Request, exc: TimeoutError):
    logger.error(f"Timeout at: {request.url} - {exc}")
    if want_html(request):
        return HTMLResponse(
            content="<h1>Request Timeout</h1><p>The server took too long to respond.</p>",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": "The server took too long to respond. Please try again later."},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)  # type: ignore
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore
    app.add_exception_handler(OperationalError, db_operational_error_handler)  # type: ignore
    app.add_exception_handler(FileNotFoundError, file_not_found_handler)  # type: ignore
    app.add_exception_handler(PermissionError, permission_exception_handler)  # type: ignore
    app.add_exception_handler(TimeoutError, timeout_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, server_error_handler)  # final catch-all

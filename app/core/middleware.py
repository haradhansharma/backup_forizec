# app/core/middleware.py

import re
from typing import Awaitable, Callable
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette_csrf import CSRFMiddleware  # type: ignore
import time
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger()


class CustomResponseCSRFMiddleware(CSRFMiddleware):
    def _get_error_response(self, request: Request) -> Response:
        return JSONResponse(content={"details": "CSRF Validation Failed"}, status_code=403)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled error while processing {request.url}. reasons: {exc}")
            raise  # Let your exception handlers catch it
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f} seconds"
        logger.info(
            f"{request.method} {request.url} - {response.status_code} [{process_time:.4f}s]"
        )
        return response


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestLoggingMiddleware)

    if settings.ENV == 'dev':
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,  # if true allow_origins, allow_methods,allow_headers should not ['*']
            allow_methods=['*'],
            allow_headers=["*"],
            expose_headers=[],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGIN,
            allow_credentials=True,  # if true allow_origins, allow_methods,allow_headers should not ['*']
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type", settings.CSRF_HEADER_NAME],
            expose_headers=[],
        )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="fourize_sessionid",
        same_site="lax",
        https_only=settings.ENV == "prod",
    )

    """
    GET request set a cookie: Set-Cookie: csrftoken=<key>
    POST, PUT, DELETE must need header: x-csrftoken in header by taking from cookie.
    """
    app.add_middleware(
        CustomResponseCSRFMiddleware,
        secret=settings.CSRF_SECRET,
        cookie_name=settings.CSRF_COOKIE_NAME,
        cookie_secure=settings.CSRF_COOKIE_SECURE,
        cookie_samesite=settings.CSRF_COOKIE_SAMESITE,
        header_name=settings.CSRF_HEADER_NAME,
        exempt_urls=[
            re.compile(rf"^{settings.API_V1_STR}(/.*)?$"),
            re.compile(rf"^{settings.API_V2_STR}(/.*)?$"),
        ],  # APIs use tokens, not cookies
    )

    if settings.ENV == 'prod':
        app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    app.add_middleware(GZipMiddleware)

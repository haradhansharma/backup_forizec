# app/main.py
# This file initializes the FastAPI application and sets up the necessary configurations.

import time
from contextlib import asynccontextmanager

# from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

# from sqlalchemy.ext.asyncio import async_engine_from_config
from app.api.v1.routes import admin, auth, user
from app.views.auth import router as web_auth_router
from app.views.dashboard import router as web_dashboard_router
from app.views.public import router as web_public_router
from app.core.config import settings
from app.core.db import Base, engine

from app.core.exceptions import (
    generic_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    validation_exception_handler,
)

from app.core.logging_config import configure_logging, get_logger


# configure logging ar startup
configure_logging()

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize app state or resources if needed
    app.state.settings = settings
    logger.info(f"Forizec App started with BASE_DIR: {settings.BASE_DIR}")

    if settings.DEBUG and settings.ENV == "dev":
        async with engine.begin() as conn:
            # Create all tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
    yield

    # print("Forizec App shutting down...")
    logger.debug("Forizec App shutting down...")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore
    app.add_exception_handler(Exception, generic_exception_handler)

    # Mount static files
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

    # Set up Jinja2 templates
    templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
    app.state.templates = templates

    # Include routers
    app.include_router(admin.router, prefix=settings.API_V1_STR, tags=["admin"])
    app.include_router(user.router, prefix=settings.API_V1_STR, tags=["user"])
    app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
    
    app.include_router(web_auth_router,tags=["web"])
    app.include_router(web_dashboard_router,tags=["web"])
    app.include_router(web_public_router, tags=["web"])

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled error while processing {request.url}")
            raise  # Let your exception handlers catch it
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f} seconds"
        logger.info(f"{request.method} {request.url} - {response.status_code} [{process_time:.4f}s]")
        return response


    
    

    return app


app = create_app()

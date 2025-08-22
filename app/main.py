# app/main.py
# This file initializes the FastAPI application and sets up the necessary configurations.
from contextlib import asynccontextmanager
import time
from pathlib import Path
# from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.db import Base, engine
# from sqlalchemy.ext.asyncio import async_engine_from_config
from app.api.v1.routes import admin, user, auth
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    generic_exception_handler
)
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize app state or resources if needed
    app.state.settings = settings
    # print(f"Starting Forizec App with settings: {settings.dict()}")
    # Create async engine from settings
    print(f"Forizec App started with BASE_DIR: {settings.BASE_DIR}")
 
    # if settings.DEBUG:
    #     async with engine.begin() as conn:
    #         # Create all tables if they don't exist
    #         await conn.run_sync(Base.metadata.create_all)
    yield
    
    print("Forizec App shutting down...")
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

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
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

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        # Process the request   
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        print(f"Request processed in {process_time:.4f} seconds")
        # Add custom header with process time
        response.headers["X-Process-Time"] = f"{process_time:.4f} seconds"
        return response

    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return templates.TemplateResponse(request,"index.html", {"request": request})

    return app

app = create_app()


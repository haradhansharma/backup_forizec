# app/tests/conftest.py
# This file sets up the testing environment for the FastAPI application using pytest and pytest-async
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import create_app
from app.core.db import Base, get_async_session

# ---------------------
# Test Database Configuration
# ---------------------

# Use in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Async engine for test database
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    future=True,
)

# Session factory for test database
AsyncSessionLocal = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency override for FastAPI
async def override_get_async_session():
    async with AsyncSessionLocal() as session:
        yield session

# ---------------------
# Pytest Fixtures
# ---------------------

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Create the database tables before tests and drop them after tests."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()

@pytest_asyncio.fixture
async def client():
    """
    FastAPI test client with the DB dependency overridden to use the test database.
    """
    app = create_app()
    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

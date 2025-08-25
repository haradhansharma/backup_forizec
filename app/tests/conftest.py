import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db_session
from app.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine_test, # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
) # type: ignore


async def override_get_async_session():
    async with AsyncSessionLocal() as session: # type: ignore
        yield session


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
async def async_session():
    """Provide a transactional scope for each test."""
    async with AsyncSessionLocal() as session: # type: ignore
        yield session


@pytest_asyncio.fixture
async def client():
    app = create_app()
    app.dependency_overrides[get_db_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

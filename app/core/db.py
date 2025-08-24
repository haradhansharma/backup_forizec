# app/core/db.py
# This file contains the database setup and session management for the Forizec application.

from __future__ import annotations
from typing import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Naming convention
convention = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

engine = create_async_engine(
    settings.EFFECTIVE_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    # important for Postgres/MySQL
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

async_session_maker = sessionmaker(
    bind=engine,  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore


# async def get_async_session() -> AsyncSession:
#     async with async_session_maker() as session:
#         yield session


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:  # type: ignore
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise

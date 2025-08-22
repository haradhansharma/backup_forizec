# migrations/env.py
# This file is used by Alembic to manage database migrations for the Forizec application

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# --- Import your app's settings and Base ---
# Make sure your app package is importable (PYTHONPATH / prepend_sys_path in alembic.ini helps)
from app.core.config import settings
from app.core.db import Base
import app.models  # noqa: F401  # ensure models are imported so metadata is populated


# Alembic Config object
config = context.config

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata

# Resolve DB URL: prefer env var DATABASE_URL, else settings.EFFECTIVE_DATABASE_URL
db_url = os.getenv("DATABASE_URL", settings.EFFECTIVE_DATABASE_URL)

# Inject URL into alembic's config so async_engine_from_config sees it
config.set_main_option("sqlalchemy.url", db_url)

# Enable SQLite-friendly batch mode when needed
def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")

def get_context_kwargs():
    # Common config for context.configure()
    kwargs = dict(
        target_metadata=target_metadata,
        compare_type=True,   # detect column type changes
        compare_server_default=True,
        render_as_batch=_is_sqlite(db_url),  # important for SQLite
    )
    return kwargs


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode'."""
    context.configure(
        url=db_url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **get_context_kwargs(),
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, **get_context_kwargs())
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # Async engine for online migrations
    # Uses sqlalchemy.url we injected above
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode'."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

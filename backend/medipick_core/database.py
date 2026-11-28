"""
MediPick Core — Async Database Engine & Session
SQLAlchemy 2.0 async setup using asyncpg driver.
"""
from __future__ import annotations

import os
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://medipick:password@localhost:5433/medipick_db",
)

def create_db_engine(database_url: str | None = None):
    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    ssl_env = os.getenv("DATABASE_SSL", "").lower()
    connect_args: dict[str, object] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    }
    if ssl_env in ("true", "1", "yes", "require"):
        connect_args["ssl"] = "require"
    return create_async_engine(
        url,
        echo=False,
        pool_size=5,
        max_overflow=5,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

engine = create_db_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

class Base(DeclarativeBase):
    """All MediPick ORM models inherit from this base."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields an async database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.cache import redis_connection
from app.db.db import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async Postgres connection"""
    async with async_session_maker() as session:
        yield session


async def get_async_redis() -> AsyncGenerator[Redis, None]:
    r = redis_connection()
    try:
        yield r
    finally:
        await r.close()

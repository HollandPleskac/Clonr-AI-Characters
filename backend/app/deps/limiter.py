import time
from typing import Annotated, Any, Callable, Coroutine, Optional

import sqlalchemy as sa
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from limits import parse
from limits.aio.storage import RedisStorage
from limits.aio.strategies import FixedWindowRateLimiter, MovingWindowRateLimiter
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.settings import settings

from .db import get_async_session
from .users import next_auth_cookie

# the limits library uses coredis, which I think is now deprecated
# Note, the user is always default for some reason: https://github.com/redis/node-redis/issues/1591
STORAGE_URI = f"async+redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"


def get_remote_address(request: Request) -> str:
    """
    Returns the ip address for the current request (or 127.0.0.1 if none found)
    """
    if not request.client or not request.client.host:
        return "127.0.0.1"

    return request.client.host


async def get_redis_storage():
    storage = RedisStorage(STORAGE_URI)
    yield storage


def user_id_cookie_fixed_window_ratelimiter(
    window: str,
) -> Callable[[RedisStorage, AsyncSession, Optional[str]], Coroutine[Any, Any, Any]]:
    try:
        parse(window)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    async def inner(
        storage: Annotated[RedisStorage, Depends(get_redis_storage)],
        db: Annotated[AsyncSession, Depends(get_async_session)],
        token: Annotated[str | None, Depends(next_auth_cookie)],
    ):
        if token is None:
            detail = "Failed to provide Authorization cookie"
            logger.info(detail)
            raise HTTPException(status_code=401, detail=detail)
        user_id = await db.scalar(
            sa.select(models.User.id)
            .join(models.Session, models.Session.user_id == models.User.id)
            .where(models.Session.session_token == token)
        )
        # use the redis connection from storage to avoid holding two connections
        if not user_id:
            logger.info("Provided session ID does not correspond to a user")
            raise HTTPException(status_code=401)
        user_id_str = str(user_id)
        try:
            window_obj = parse(window)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        limiter = FixedWindowRateLimiter(storage=storage)
        ok = await limiter.hit(window_obj, user_id_str, cost=1)
        if not ok:
            stats = await limiter.get_window_stats(window_obj, user_id_str)
            wait_time = stats.reset_time - time.time()
            detail = f"Wait time: {wait_time:.02f}s"
            raise HTTPException(status_code=429, detail=detail)

    return inner


def ip_addr_moving_ratelimiter(
    window: str,
) -> Callable[[Optional[str], RedisStorage], Coroutine[Any, Any, Any]]:
    try:
        window_obj = parse(window)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    async def inner(
        ip_addr: Annotated[str, Depends(get_remote_address)],
        storage: Annotated[RedisStorage, Depends(get_redis_storage)],
    ):
        limiter = MovingWindowRateLimiter(storage=storage)
        ok = await limiter.hit(window_obj, ip_addr, cost=1)
        if not ok:
            logger.info(f"Ratelimited IP addr: {ip_addr}.")
            raise HTTPException(status_code=429)

    return inner

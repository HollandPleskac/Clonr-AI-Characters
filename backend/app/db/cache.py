import logging
from typing import AsyncGenerator

from loguru import logger
from opentelemetry.instrumentation.redis import RedisInstrumentor
from redis.asyncio import Redis
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from app.settings import settings

RedisInstrumentor().instrument()


def redis_connection(host: str | None = None, port: int | None = None):
    if port is None:
        port = settings.REDIS_PORT
    if host is None:
        host = settings.REDIS_HOST
    return Redis(
        host=host,
        port=port,
        password=settings.REDIS_PASSWORD,
    )


@retry(
    stop=stop_after_attempt(20),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before=before_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.WARN),  # type: ignore
)
async def wait_for_redis():
    r = redis_connection()
    try:
        await r.ping()
    except Exception as e:
        logger.error(e)
        raise e
    logger.info("Established connection to Redis")


async def clear_redis():
    r = redis_connection()
    try:
        await r.flushall()
    finally:
        await r.close()


async def get_async_redis() -> AsyncGenerator[Redis, None]:
    conn = redis_connection()
    try:
        yield conn
    finally:
        await conn.close()

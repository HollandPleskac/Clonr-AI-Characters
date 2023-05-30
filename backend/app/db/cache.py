import json
import logging
from typing import AsyncGenerator, Optional

import redis.asyncio as redis
from app import models, schemas
from app.settings import settings
from app.utils import iso2unix
from fastapi.encoders import jsonable_encoder
from loguru import logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential


async def clear_redis():
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )
    try:
        await r.flushall()
    finally:
        await r.close()


async def get_async_redis_client():
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )
    try:
        yield r
    finally:
        await r.close()


@retry(
    stop=stop_after_attempt(20),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_redis():
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )
    try:
        await r.ping()
    except Exception as e:
        logger.error(e)
        raise e
    logger.info("Established connection to Redis")


class APIKeyCache:
    def __init__(self, r, delimiter: str = ":", prefix: str = "apikey"):
        self.r = r
        self.delimiter = delimiter
        self.prefix = prefix

    def make_redis_key(self, apikey: str):
        return f"{self.prefix}{self.delimiter}{apikey}"

    async def add(self, apikey: models.APIKey | schemas.APIKey) -> str:
        key = self.make_redis_key(apikey.key)
        value = json.dumps(jsonable_encoder(apikey))
        await self.r.set(key, value)
        return key

    async def delete(self, apikey: str | models.APIKey) -> str:
        if isinstance(apikey, models.APIKey):
            apikey = apikey.key
        key = self.make_redis_key(apikey)
        value = await self.r.delete(key)
        return value

    async def get(self, apikey: str | models.APIKey) -> Optional[schemas.APIKey]:
        if isinstance(apikey, models.APIKey):
            apikey = apikey.key
        key = self.make_redis_key(apikey)
        value = await self.r.get(key)
        if value is None:
            logger.info("API KEY CACHE MISS!")
            return value
        logger.info("API KEY CACHE HIT!")
        return schemas.APIKey(**json.loads(value.decode("utf-8")))


async def get_async_apikey_cache() -> AsyncGenerator[APIKeyCache, None]:
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )
    try:
        yield APIKeyCache(r=r)
    finally:
        await r.close()


class ConversationCache:
    def __init__(self, r, delimiter: str = ":", prefix: str = "conversation"):
        self.r = r
        self.delimiter = delimiter
        self.prefix = prefix

    def make_redis_key(self, conversation_id: str):
        return f"{self.prefix}{self.delimiter}{conversation_id}"

    async def add_message(self, message: models.Message | schemas.Message) -> str:
        key = self.make_redis_key(str(message.conversation_id))
        score = iso2unix(message.created_at.isoformat())
        value = json.dumps(jsonable_encoder(message))
        # (redis docs): nx forces ZADD to only create new elements and not to update scores for elements that already exist.
        # this makes a sorted set on key, where elements are value and they sort according to score.
        await self.r.zadd(key, {value: score}, nx=True)
        logger.info(f"Added to redis cache: {key}")
        return key

    async def n_messages(self, conversation_id: str) -> str:
        key = self.make_redis_key(str(conversation_id))
        n = await self.r.zcard(key)
        return n

    async def delete(self, conversation_id: str) -> int:
        key = self.make_redis_key(str(conversation_id))
        n = await self.r.delete(conversation_id)
        return int(n)

    async def get(
        self, conversation_id: str, offset: int = 0, limit: int = 10
    ) -> list[schemas.Message]:
        key = self.make_redis_key(str(conversation_id))
        res = await self.r.zrevrange(key, offset, limit)
        res = [schemas.Message(**json.loads(m.decode("utf-8"))) for m in res]
        logger.info(f"CONVO CACHE HIT!")
        return res


async def get_async_convo_cache() -> AsyncGenerator[ConversationCache, None]:
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )
    try:
        yield ConversationCache(r=r)
    finally:
        await r.close()

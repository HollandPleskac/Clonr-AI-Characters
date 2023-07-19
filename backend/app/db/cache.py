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


def _redis_connection():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )


@retry(
    stop=stop_after_attempt(20),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_redis():
    r = _redis_connection()
    try:
        await r.ping()
    except Exception as e:
        logger.error(e)
        raise e
    logger.info("Established connection to Redis")


async def clear_redis():
    r = _redis_connection()
    try:
        await r.flushall()
    finally:
        await r.close()


async def get_async_redis_client() -> AsyncGenerator[redis.Redis, None]:
    r = _redis_connection()
    try:
        yield r
    finally:
        await r.close()


class RedisCache:
    def __init__(self, r, delimiter: str = ":"):
        self.r = r
        self.delimiter = delimiter
        self.api_key_prefix = "api_key"
        self.conversation_prefix = "conversation"
        self.clone_prefix = "clone"
        self.user_ban_prefix = "user_ban"

    def make_api_key_key(self, apikey: str):
        return f"{self.api_key_prefix}{self.delimiter}{apikey}"

    def make_conversation_key(self, conversation_id: str):
        return f"{self.conversation_prefix}{self.delimiter}{conversation_id}"

    def make_clone_key(self, clone_id: str):
        return f"{self.clone_prefix}{self.delimiter}{clone_id}"

    async def api_key_create(self, api_key: models.APIKey) -> str:
        key = self.make_api_key_key(api_key.hashed_key)
        value = jsonable_encoder(api_key)
        await self.r.set(key, json.dumps(value))
        logger.info(f"CACHE CREATE: {key}")
        return key

    async def api_key_delete(self, hashed_key: str) -> str:
        key = self.make_api_key_key(hashed_key)
        value = await self.r.delete(key)
        logger.info(f"CACHE DELETE: {key}")
        return value

    async def api_key_get(self, hashed_key: str) -> Optional[schemas.APIKey]:
        key = self.make_api_key_key(hashed_key)
        if value := await self.r.get(key):
            logger.info(f"CACHE HIT: {key}")
            return schemas.APIKey(**json.loads(value.decode("utf-8")))
        logger.info(f"CACHE MISS: {key}")

    async def message_add(self, message: models.Message) -> str:
        key = self.make_conversation_key(str(message.conversation_id))
        score = iso2unix(message.created_at.isoformat())
        value = json.dumps(jsonable_encoder(message))
        # (redis docs): nx forces ZADD to only create new elements and not to update scores for elements that already exist.
        # this makes a sorted set on key, where elements are value and they sort according to score.
        await self.r.zadd(key, {value: score}, nx=True)
        logger.info(f"CACHE CREATE: {key}")
        return key

    async def message_get_latest(
        self, conversation_id: str, offset: int = 0, limit: int = 20
    ) -> list[schemas.Message]:
        key = self.make_conversation_key(str(conversation_id))
        values = await self.r.zrevrange(key, offset, limit)
        res = [schemas.Message(**json.loads(m.decode("utf-8"))) for m in values]
        logger.info(f"CACHE GET: {key}. NUM_MESSAGES: {len(values)}")
        return res

    async def message_get(
        self, conversation_id: str, offset: int = 0, limit: int = 20
    ) -> list[schemas.Message]:
        key = self.make_conversation_key(str(conversation_id))
        values = await self.r.zrevrange(key, offset, limit)
        res = [schemas.Message(**json.loads(m.decode("utf-8"))) for m in values]
        logger.info(f"CACHE GET: {key}")
        return res

    async def message_count(self, conversation_id: str) -> str:
        key = self.make_conversation_key(str(conversation_id))
        n = await self.r.zcard(key)
        return n

    async def message_delete(self, conversation_id: str, message_id: str) -> int:
        key = self.make_conversation_key(str(conversation_id))
        n = await self.r.zrem(conversation_id, message_id)
        logger.info(f"CACHE DELETE: {key}")
        return int(n)

    async def conversation_delete(
        self,
        conversation_id: str,
    ) -> list[schemas.Message]:
        key = self.make_conversation_key(str(conversation_id))
        res = await self.r.delete(key)
        logger.info(f"CACHE DELETE: {key}")
        return res

    async def clone_add(self, clone: models.Clone) -> str:
        key = self.make_clone_key(clone.id)
        value = jsonable_encoder(clone)
        await self.r.hmset(key, value)
        return key

    async def clone_delete(self, clone_id: str) -> str:
        key = self.make_clone_key(clone_id)
        value = await self.r.delete(key)
        return value

    async def clone_get(self, clone_id: str, value: Optional[str] = None):
        key = self.make_clone_key(clone_id)
        if value is None:
            return await self.r.hgetall(clone_id) or None
        return await self.r.hget(key, value)

    async def ban_user(self, user_id: int):
        key = f"{self.user_ban_prefix}{self.delimiter}{user_id}"
        await self.r.set(key, "True")

    async def is_user_banned(self, user_id: int) -> bool:
        key = f"{self.user_ban_prefix}{self.delimiter}{user_id}"
        return await self.r.get(key) == b"True"


async def get_async_redis_cache() -> AsyncGenerator[RedisCache, None]:
    r = _redis_connection()
    try:
        yield RedisCache(r=r)
    finally:
        await r.close()

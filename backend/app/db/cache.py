import logging
import uuid
from typing import AsyncGenerator

import redis.asyncio as redis
from loguru import logger
from opentelemetry.instrumentation.redis import RedisInstrumentor
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from app.settings import settings

RedisInstrumentor().instrument()


def redis_connection(host: str | None = None, port: int | None = None):
    return redis.Redis(
        host=host or settings.REDIS_HOST,
        port=port or settings.REDIS_PORT,
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


class CacheCounter:
    def __init__(self, conn, key: str):
        self.conn = conn
        self.key = key

    async def set(self, value: int):
        await self.conn.set(self.key, value)

    async def get(self) -> int:
        r = await self.conn.get(self.key)
        return int(r)

    async def increment(self, importance: int) -> int:
        r = await self.conn.incrby(self.key, amount=importance)
        return int(r)


# FixMe (Jonny): This whole class is probably broken. Refactored clone-related
# caching to its own file under app/clone/cache.py
class RedisCache:
    def __init__(self, conn):
        self.conn = conn

    def _clone_key(self, clone_id: str | uuid.UUID) -> str:
        clone_id = str(clone_id)
        return f"clone_id::{clone_id}"

    def _conversation_key(self, conversation_id: str | uuid.UUID) -> str:
        id = str(conversation_id)
        return f"conversation_id::{id}"

    def reflection_counter(self, clone_id: str | uuid.UUID):
        """Example usage:  await cache.reflection_counter(clone_model.id).increment(10) to add 10 to the counter."""
        return CacheCounter(
            conn=self.conn, key=f"{self._clone_key(clone_id)}::reflection_counter"
        )

    def agent_summary_counter(self, clone_id: str | uuid.UUID):
        return CacheCounter(
            conn=self.conn, key=f"{self._clone_key(clone_id)}::agent_summary_counter"
        )

    def entity_context_counter(self, clone_id: str | uuid.UUID):
        return CacheCounter(
            conn=self.conn, key=f"{self._clone_key(clone_id)}::entity_context_counter"
        )

    # TODO (Jonny): fix and test this
    # def _api_key_key(self, apikey: str):
    #     return f"{self.api_key_prefix}{self.delimiter}{apikey}"

    # async def add_api_key(self, api_key: models.APIKey) -> str:
    #     key = self._api_key_key(api_key.hashed_key)
    #     value = jsonable_encoder(api_key)
    #     await self.r.set(key, json.dumps(value))
    #     return key

    # async def delete_api_key(self, hashed_key: str) -> str:
    #     key = self._api_key_key(hashed_key)
    #     value = await self.r.delete(key)
    #     return value

    # async def get_api_key(self, hashed_key: str) -> Optional[schemas.APIKey]:
    #     key = self._api_key_key(hashed_key)
    #     if value := await self.r.get(key):
    #         return schemas.APIKey(**json.loads(value.decode("utf-8")))

    # async def add_clone(self, clone: models.Clone) -> bool:
    #     key = self._clone_key(clone.id)
    #     value = json.dumps(jsonable_encoder(clone)).encode()
    #     return await self.conn.set(key, value)

    # async def delete_clone(self, clone_id: str) -> str:
    #     key = self._clone_key(clone_id)
    #     return await self.conn.delete(key)

    # async def get_clone(self, clone_id: str) -> models.Clone:
    #     key = self._clone_key(clone_id)
    #     r = await self.conn.get(key)
    #     data = json.loads(r.decode("utf-8"))
    #     return models.Clone(**data)

    # async def add_message(self, message: models.Message) -> bool:
    #     key = self._conversation_key(message.conversation_id)
    #     score = message.timestamp.timestamp()
    #     value = json.dumps(jsonable_encoder(message))
    #     # (redis docs): nx forces ZADD to only create new elements and not to update scores for elements that already exist.
    #     # this makes a sorted set on key, where elements are value and they sort according to score.
    #     return await self.conn.zadd(key, {value: score}, nx=True)

    # async def get_messages(
    #     self, conversation_id: str, offset: int = 0, limit: int = 20
    # ) -> list[models.Message]:
    #     key = self._conversation_key(conversation_id)
    #     values = await self.conn.zrevrange(key, offset, limit)
    #     return [models.Message(**json.loads(m.decode("utf-8"))) for m in values]

    # async def count_messages(self, conversation_id: str) -> int:
    #     key = self._conversation_key(conversation_id)
    #     n = await self.conn.zcard(key)
    #     n = n or 0
    #     return int(n)

    # async def delete_message(self, message: models.Message) -> int:
    #     key = self._conversation_key(message.conversation_id)
    #     value = json.dumps(jsonable_encoder(message))
    #     n = await self.conn.zrem(key, value)
    #     return int(n)

    # async def cache_total_conversations(self, user_id: int, total_conversations: int):
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}:total_conversations"
    #     await self.r.set(key, total_conversations)
    #     logger.info(f"CACHE SET: {key}")

    # async def get_cached_total_conversations(self, user_id: int) -> Optional[int]:
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}:total_conversations"
    #     if value := await self.r.get(key):
    #         logger.info(f"CACHE HIT: {key}")
    #         return int(value)
    #     logger.info(f"CACHE MISS: {key}")

    # async def cache_total_messages(
    #     self, user_id: int, num_msgs_sent: int, num_msgs_received: int
    # ):
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}:total_messages"
    #     await self.r.hmset(
    #         key,
    #         {"num_msgs_sent": num_msgs_sent, "num_msgs_received": num_msgs_received},
    #     )
    #     logger.info(f"CACHE SET: {key}")

    # async def get_cached_total_messages(self, user_id: int) -> Optional[dict[str, int]]:
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}:total_messages"
    #     if values := await self.r.hgetall(key):
    #         logger.info(f"CACHE HIT: {key}")
    #         return {
    #             "num_msgs_sent": int(values.get(b"num_msgs_sent", 0)),
    #             "num_msgs_received": int(values.get(b"num_msgs_received", 0)),
    #         }
    #     logger.info(f"CACHE MISS: {key}")

    # async def conversation_delete(
    #     self,
    #     conversation_id: str,
    # ) -> list[models.Message]:
    #     key = self._conversation_key(conversation_id)
    #     res = await self.conn.delete(key)
    #     return res

    # async def clone_add(self, clone: models.Clone) -> str:
    #     key = self.make_clone_key(clone.id)
    #     value = jsonable_encoder(clone)
    #     await self.r.hmset(key, value)
    #     return key

    # async def clone_delete(self, clone_id: str) -> str:
    #     key = self.make_clone_key(clone_id)
    #     value = await self.r.delete(key)
    #     return value

    # async def clone_get(self, clone_id: str, value: Optional[str] = None):
    #     key = self.make_clone_key(clone_id)
    #     if value is None:
    #         return await self.r.hgetall(clone_id) or None
    #     return await self.r.hget(key, value)

    # async def ban_user(self, user_id: int):
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}"
    #     await self.r.set(key, "True")

    # async def is_user_banned(self, user_id: int) -> bool:
    #     key = f"{self.user_ban_prefix}{self.delimiter}{user_id}"
    #     return await self.r.get(key) == b"True"


async def get_async_redis_cache() -> AsyncGenerator[RedisCache, None]:
    r = redis_connection()
    try:
        yield RedisCache(r=r)
    finally:
        await r.close()

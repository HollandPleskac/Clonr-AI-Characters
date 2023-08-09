import json
import uuid

from fastapi.encoders import jsonable_encoder

from app import models


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


class CloneCache:
    # TODO (Jonny): Should this be instantiated with `clone_id`?
    def __init__(self, conn):
        self.conn = conn

    def _clone_key(self, clone_id: str | uuid.UUID) -> str:
        clone_id = str(clone_id)
        return f"clone_id::{clone_id}"

    def _user_key(self, user_id: str | uuid.UUID) -> str:
        user_id = str(user_id)
        return f"user_id::{user_id}"

    def _conversation_key(self, conversation_id: str | uuid.UUID) -> str:
        id = str(conversation_id)
        return f"conversation_id::{id}"

    def reflection_counter(self, conversation_id: str | uuid.UUID):
        """Example usage:  await cache.reflection_counter(clone_model.id).increment(10) to add 10 to the counter."""
        return CacheCounter(
            conn=self.conn,
            key=f"{self._conversation_key(conversation_id)}::reflection_counter",
        )

    def agent_summary_counter(self, conversation_id: str | uuid.UUID):
        return CacheCounter(
            conn=self.conn,
            key=f"{self._conversation_key(conversation_id)}::agent_summary_counter",
        )

    def entity_context_counter(self, conversation_id: str | uuid.UUID):
        return CacheCounter(
            conn=self.conn,
            key=f"{self._conversation_key(conversation_id)}::entity_context_counter",
        )

    async def increment_all_counters(
        self, conversation_ids: list[str | uuid.UUID], importance: int
    ):
        if isinstance(conversation_ids, (str, uuid.UUID)):
            conversation_ids = [conversation_ids]
        async with self.conn.pipeline() as p:
            for conversation_id in conversation_ids:
                k = self._conversation_key(conversation_id=str(conversation_id))
                p.incrby(f"{k}::reflection_counter", importance)
                p.incrby(f"{k}::agent_summary_counter", importance)
                p.incrby(f"{k}::entity_context_counter", importance)
            await p.execute()

    async def add_clone(self, clone: models.Clone) -> bool:
        key = self._clone_key(clone.id)
        value = json.dumps(jsonable_encoder(clone)).encode()
        return await self.conn.set(key, value)

    async def delete_clone(self, clone_id: str) -> str:
        key = self._clone_key(clone_id)
        return await self.conn.delete(key)

    async def get_clone(self, clone_id: str) -> models.Clone:
        key = self._clone_key(clone_id)
        r = await self.conn.get(key)
        data = json.loads(r.decode("utf-8"))
        return models.Clone(**data)

    def moderation_violations_counter(self, user_id: str | uuid.UUID):
        return CacheCounter(
            conn=self.conn,
            key=f"{self._user_key(user_id)}::moderation_violations_counter",
        )

    async def add_moderation_violations(self, user_id: str | uuid.UUID, count: int = 1):
        moderation_counter = self.moderation_violations_counter(user_id)
        await moderation_counter.increment(count)

    # Note (Jonny): Decided against using Redis to retrieve messages. These
    # will grow the cache quickly and could cause problems, and setting a smart eviction
    # policy that handles all edge cases is really not obvious
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

    # async def conversation_delete(
    #     self,
    #     conversation_id: str,
    # ) -> list[models.Message]:
    #     key = self._conversation_key(conversation_id)
    #     res = await self.conn.delete(key)
    #     return res

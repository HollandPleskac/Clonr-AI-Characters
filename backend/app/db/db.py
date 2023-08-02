import logging
from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper
from loguru import logger
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from app.db.events import (
    decrement_clone_num_conversations,
    decrement_clone_num_messages,
    increment_clone_num_conversations,
    increment_clone_num_messages,
)
from app.models import Base, Creator, OAuthAccount, User
from app.settings import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@retry(
    stop=stop_after_attempt(20),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_db():
    async with async_session_maker() as conn:
        try:
            await conn.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(e)
            raise e
    logger.info("Established connection to DB")


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;"))
        # await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trm;"))
        # for hybrid search, see: https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search.py
        # an example usage is:
        # await cur.execute("SELECT id, content FROM document, plainto_tsquery('english', %s) query WHERE
        # to_tsvector('english', content) @@ query ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC LIMIT 5", (query,))
        # await conn.execute("CREATE INDEX ON document USING GIN (to_tsvector('english', content))")
        await conn.run_sync(Base.metadata.create_all)


async def clear_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)


async def create_superuser() -> User:
    async with async_session_maker() as db:
        password = settings.SUPERUSER_PASSWORD
        hashed_password = PasswordHelper().hash(password=password)
        user = User(
            email=settings.SUPERUSER_EMAIL,
            is_superuser=True,
            hashed_password=hashed_password,
        )
        creator = Creator(user=user, username="superuser")
        db.add(creator)
        try:
            await db.commit()
        except Exception as e:
            logger.exception(e)
            await db.rollback()
    return user

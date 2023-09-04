import logging

from loguru import logger
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_exponential

from app import models
from app.settings import settings

from .events import decrement_clone_num_conversations  # noqa
from .events import decrement_clone_num_messages  # noqa
from .events import increment_clone_num_conversations  # noqa
from .events import increment_clone_num_messages  # noqa

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

# FixMe (Jonny): why is sqlalchemy typing fucked on async sessionmaker
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


@retry(
    stop=stop_after_attempt(20),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before=before_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.WARN),  # type: ignore
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
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        # for hybrid search, see: https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search.py
        # an example usage is:
        # await cur.execute("SELECT id, content FROM document, plainto_tsquery('english', %s) query WHERE
        # to_tsvector('english', content) @@ query ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC LIMIT 5", (query,))
        # await conn.execute("CREATE INDEX ON document USING GIN (to_tsvector('english', content))")
        await conn.run_sync(models.Base.metadata.create_all)


async def clear_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)


async def create_superuser() -> models.User:
    from datetime import datetime, timedelta

    async with async_session_maker() as db:
        user = models.User(
            name="superuser",
            email="admin@example.com",
            is_superuser=True,
        )
        creator = models.Creator(user=user, username="superuser")
        session = models.Session(
            session_token="SUPERUSER_TOKEN",
            expires=datetime.now() + timedelta(days=1),
            user=user,
        )
        user2 = models.User(
            name="normal_user",
            email="normal@user.com",
            is_superuser=False,
        )
        creator2 = models.Creator(user=user2, username="normal_user")
        session2 = models.Session(
            session_token="NORMAL_USER_TOKEN",
            expires=datetime.now() + timedelta(days=1),
            user=user2,
        )
        user3 = models.User(
            name="creator_user",
            email="creeator@user.com",
            is_superuser=False,
        )
        creator3 = models.Creator(user=user3, username="creator_user")
        session3 = models.Session(
            session_token="CREATOR_USER_TOKEN",
            expires=datetime.now() + timedelta(days=1),
            user=user3,
        )
        db.add(creator)
        db.add(session)
        db.add(creator2)
        db.add(session2)
        db.add(creator3)
        db.add(session3)
        try:
            await db.commit()
        except Exception as e:
            logger.exception(e)
            await db.rollback()
    return user

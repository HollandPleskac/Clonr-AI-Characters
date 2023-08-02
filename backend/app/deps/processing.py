from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, Path, status
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.clone.cache import CloneCache
from app.clone.db import CloneDB
from app.clone.shared import (
    SHARED_DYNAMIC_SPLITTER,
    SHARED_TOKENIZER,
    DynamicTextSplitter,
)
from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

from .db import get_async_redis, get_async_session
from .users import get_current_active_user


async def get_embedding_client():
    async with EmbeddingClient() as client:
        yield client


async def get_text_splitter() -> DynamicTextSplitter:
    yield SHARED_DYNAMIC_SPLITTER


async def get_tokenizer() -> Tokenizer:
    yield SHARED_TOKENIZER


async def get_clonedb(
    clone_id: Annotated[str, Path()],
    user: Annotated[models.User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    conn: Annotated[Redis, Depends(get_async_redis)],
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
    conversation_id: Annotated[str | None, Path()] = None,
) -> CloneDB:
    """This method is authenticated, and ensures that the user has access to edit
    the clone"""
    if not user.is_superuser and not (
        await db.execute(
            sa.select(models.Clone.creator_id)
            .where(models.Clone.creator_id == user.id)
            .where(models.Clone.id == clone_id)
        ).all()
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    cache = CloneCache(conn=conn)
    clonedb = CloneDB(
        db=db,
        cache=cache,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
        clone_id=clone_id,
        conversation_id=conversation_id,
    )
    yield clonedb


# async def get_llm_as_creator(
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     clone_id: Annotated[str, Path()],
#     user: Annotated[str, Depends(get_current_active_user)],
#     tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
# ) -> LLM:
#     callbacks: list[LLMCallback] = [
#         LoggingCallback(),
#         AddToPostgresCallback(
#             db=db, clone_id=clone_id, user_id=user_id, conversation_id=conversation_id
#         ),
#     ]
#     if settings.LLM == "mock":
#         llm = MockLLM(callbacks=callbacks)
#     else:
#         llm = OpenAI(
#             model=settings.LLM,
#             api_key=settings.OPENAI_API_KEY,
#             tokenizer=tokenizer,
#             callbacks=callbacks,
#         )
#     yield llm


# async def get_clone_model_as_creator(
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     clone_id: Annotated[str, Path()],
#     user: Annotated[str, Depends(get_current_active_user)],
# ) -> models.Clone:
#     if clone := await db.get(models.Clone, clone_id):
#         if user.id == clone.creator_id or user.is_superuser:
#             yield clone
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Clone id ({clone_id}) not found.",
#         )

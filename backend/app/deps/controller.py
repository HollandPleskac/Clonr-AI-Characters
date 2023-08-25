import os
import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import BackgroundTasks, Depends, Path, status
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.clone.cache import CloneCache
from app.clone.controller import Controller
from app.clone.db import CloneDB
from app.embedding import EmbeddingClient
from app.settings import settings
from clonr.llms.callbacks import AddToPostgresCallback, LLMCallback, LoggingCallback
from clonr.tokenizer import Tokenizer

from .db import get_async_redis, get_async_session
from .embedding import get_embedding_client
from .llm import _get_llm
from .text import get_tokenizer
from .users import get_free_or_paying_user


@lru_cache(maxsize=1)
def is_docker() -> bool:
    path = "/proc/self/cgroup"
    if os.path.exists("/.dockerenv"):
        return True
    if os.path.isfile(path) and any("docker" in line for line in open(path)):
        return True
    return False


# Requires either the clone_id or conversation_id
async def get_controller(
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(get_free_or_paying_user)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
    conn: Annotated[Redis, Depends(get_async_redis)],
    background_tasks: BackgroundTasks,
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
):
    # Auth, convo, and clone
    if not (conversation := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found.",
        )
    user_id = conversation.user_id
    if not user.is_superuser and conversation.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this conversation.",
        )
    if (clone := await db.get(models.Clone, conversation.clone_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clone with does not exist. ID: {conversation.clone_id}.",
        )

    # LLM. We have to repeat the code from get_llm, since this runs before the conversation has
    # been created. This could use a refactor
    callbacks: list[LLMCallback] = [
        LoggingCallback(),
        AddToPostgresCallback(
            db=db, clone_id=clone.id, user_id=user.id, conversation_id=conversation_id
        ),
    ]
    llm = _get_llm(model_name=settings.LLM, tokenizer=tokenizer, callbacks=callbacks)

    # redis cache
    cache = CloneCache(conn=conn)

    # postgres db
    clonedb = CloneDB(
        db=db,
        cache=cache,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
        clone_id=clone.id,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    controller = Controller(
        llm=llm,
        user=user,
        clone=clone,
        clonedb=clonedb,
        conversation=conversation,
        background_tasks=background_tasks,
    )

    yield controller

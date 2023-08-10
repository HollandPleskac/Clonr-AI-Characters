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
from clonr.llms import LlamaCpp, MockLLM, OpenAI
from clonr.llms.callbacks import AddToPostgresCallback, LLMCallback, LoggingCallback
from clonr.tokenizer import Tokenizer

from .db import get_async_redis, get_async_session
from .embedding import get_embedding_client
from .text import get_tokenizer
from .users import get_current_active_user


# Requires either the clone_id or conversation_id
async def get_controller(
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.Creator, Depends(get_current_active_user)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
    conn: Annotated[Redis, Depends(get_async_redis)],
    background_tasks: BackgroundTasks,
    tokenizer: Annotated[Tokenizer, Depends(get_tokenizer)],
):
    # Auth, convo, and clone
    if not (conversation := await db.get(models.Conversation, id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found.",
        )
    if not user.is_superuser and conversation.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this conversation.",
        )
    clone = await db.get(models.Clone, conversation.clone_id)

    # LLM
    callbacks: list[LLMCallback] = [
        LoggingCallback(),
        AddToPostgresCallback(
            db=db, clone_id=clone.id, user_id=user.id, conversation_id=conversation_id
        ),
    ]
    if settings.LLM == "mock":
        # so much output parsing will break with the mock llm though...
        llm = MockLLM(response="mock response", callbacks=callbacks)
    elif settings.LLM == "llamacpp":
        llm = LlamaCpp(chat_mode=True)
    else:
        llm = OpenAI(
            model=settings.LLM,
            api_key=settings.OPENAI_API_KEY,
            tokenizer=tokenizer,
            callbacks=callbacks,
        )

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
    )

    controller = Controller(
        llm=llm,
        clone=clone,
        clonedb=clonedb,
        conversation=conversation,
        background_tasks=background_tasks,
    )

    yield controller

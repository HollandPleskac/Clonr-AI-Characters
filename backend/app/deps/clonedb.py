from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, Path, status
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.clone.cache import CloneCache
from app.clone.db import CloneDB
from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

from .db import get_async_redis, get_async_session
from .embedding import get_embedding_client
from .text import get_tokenizer
from .users import get_current_active_user


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
    exists = await db.execute(
        sa.select(models.Clone.creator_id)
        .where(models.Clone.creator_id == user.id)
        .where(models.Clone.id == clone_id)
    )
    if not user.is_superuser and not exists.all():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    user_id = user.id
    # TODO (Jonny): we should probably have a creator clonedb
    # and a user clonedb. We don't want None floating around for
    if user.is_superuser and conversation_id:
        # conversation ID
        user_id = await db.scalar(
            sa.select(models.Conversation.user_id).where(
                models.Conversation.id == conversation_id
            )
        )
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
    cache = CloneCache(conn=conn)
    clonedb = CloneDB(
        db=db,
        cache=cache,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
        clone_id=clone_id,
        conversation_id=conversation_id,
        user_id=user_id,
    )
    yield clonedb

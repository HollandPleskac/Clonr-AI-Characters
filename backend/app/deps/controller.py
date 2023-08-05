from typing import Annotated

from fastapi import Body, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.embedding import EmbeddingClient

from .db import get_async_session
from .embedding import get_embedding_client
from .users import get_current_active_user


# Requires either the clone_id or conversation_id
async def get_controller(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.Creator, Depends(get_current_active_user)],
    embedding_client: Annotated[EmbeddingClient, Depends(get_embedding_client)],
    conversation_id: Annotated[str | None, Path(min_length=36, max_length=36)] = None,
    clone_id: Annotated[str | None, Body(min_length=36, max_length=36)] = None,
):
    raise ValueError(clone_id)

import datetime
import enum
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.embedding import EmbeddingClient

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)


class MsgSortType(str, enum.Enum):
    newest: str = "newest"
    oldest: str = "oldest"
    similarity: str = "similarity"
    embedding: str = "embedding"


async def get_message(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_current_active_user)],
    message_id: Annotated[uuid.UUID, Path()] = None,
) -> models.Message:
    msg = await db.get(models.Message, message_id)
    if not msg or (not msg.is_active and not user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found.",
        )
    if not user.is_superuser and not msg.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user: {user.id}.",
        )
    return msg


@router.get("/", response_model=list[schemas.Message])
async def get_messages(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
    user: Annotated[models.Creator, Depends(deps.get_current_active_user)],
    conversation_id: Annotated[str | None, Query(min_length=36, max_length=36)] = None,
    clone_id: Annotated[str | None, Query(min_length=36, max_length=36)] = None,
    user_id: Annotated[str | None, Query(min_length=36, max_length=36)] = None,
    q: Annotated[str | None, Query(max_length=512)] = None,
    sort: Annotated[MsgSortType, Query()] = MsgSortType.newest,
    sent_after: Annotated[datetime.datetime | None, Query()] = None,
    sent_before: Annotated[datetime.datetime | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=60)] = 20,
    is_active: Annotated[bool, Query()] = True,
    is_main: Annotated[bool, Query()] = True,
):
    if not user.is_superuser and (not is_active or not is_main):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Query parameters is_active, is_main not allowed",
        )
    # auth stuff
    if q is None and sort in [MsgSortType.similarity, MsgSortType.embedding]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'If using sort type ({sort}), you must pass a query parameter "q"',
        )
    # if user_id is supplied, you better be the superuser
    if user_id is None:
        user_id = user.id
    elif not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user ID.",
        )
    # filtering by Message.user_id = user_id is really important!
    query = (
        sa.select(models.Message)
        .where(models.Message.user_id == user_id)
        .where(models.Message.is_main == is_main)
        .where(models.Message.is_active == is_active)
        .offset(offset)
        .limit(limit)
    )
    if clone_id is not None:
        query = query.where(models.Message.clone_id == clone_id)
    if conversation_id is not None:
        query = query.where(models.Message.conversation_id == conversation_id)
    if sent_after is not None:
        query = query.where(models.Message.timestamp >= sent_after)
    if sent_before is not None:
        query = query.where(models.Message.timestamp <= sent_before)
    # if q is provided, we can still filter bad matches using a hard cutoff without ordering
    # by similarity only
    if q is not None:
        if sort == MsgSortType.embedding:
            emb = (await embedding_client.encode_query(q))[0]
            dist = models.Message.embedding.max_inner_product(emb).label("distance")
        else:
            # this has to run everytime to set the minimum sim score. This is what
            # make the index really fast. full similarity is easy here, just .similarity(q)
            # similarily, strict_word_similarity is the same.
            await db.execute(sa.text("SET pg_trgm.word_similarity_threshold = 0.7"))
            sml = models.Message.case_insensitive_content.word_similarity(q)
    match sort:
        case MsgSortType.embedding:
            query = query.where(models.Message.embedding.is_not(None)).order_by(
                dist.asc()
            )
        case MsgSortType.similarity:
            # full similarity is easy here, just op('%')
            query = query.where(
                models.Message.case_insensitive_content.op("%>")(q)
            ).order_by(sml.desc())
        case MsgSortType.newest:
            query = query.order_by(models.Message.timestamp.desc())
        case MsgSortType.oldest:
            query = query.order_by(models.Message.timestamp.asc())
    r = await db.scalars(query)
    msgs = r.all()
    return msgs


@router.get("/{message_id}", response_model=schemas.Message)
async def get_message_by_id(
    msg: Annotated[models.Message, Depends(get_message)],
):
    return msg

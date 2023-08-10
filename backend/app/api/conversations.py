import datetime
import enum
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.clone.controller import Controller, MemoryStrategy
from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)

FREE_MESSAGE_LIMIT = 10


class MsgSortType(str, enum.Enum):
    newest: str = "newest"
    oldest: str = "oldest"
    similarity: str = "similarity"
    embedding: str = "embedding"


# TODO (Jonny): put a paywall behind this dependency
async def get_conversation(
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_paying_user)],
) -> models.Conversation:
    convo = await db.get(models.Conversation, conversation_id)
    if not convo or not convo.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation ({conversation_id}) not found.",
        )
    if not user.is_superuser and not convo.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return convo


# TODO (Jonny): put a paywall behind this endpoint after X messages, need to add user permissions
@router.post(
    "/", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    obj: schemas.ConversationCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_free_limit_user)],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    tokenizer: Annotated[Tokenizer, Depends(deps.get_tokenizer)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
):
    clone = await db.get(models.Clone, obj.clone_id)
    if not clone or not clone.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clone ({obj.clone_id}) not found.",
        )
    if not user.is_subscribed:
        user.num_free_messages_sent += 1

    # NOTE (Jonny): not sure if this is a security risk. Indirectly exposing the
    # UUID of a private clone, by getting a different status code.
    # you can chat with your own clone, but you can't chat with private clones.
    if not clone.is_public and not clone.creator_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if obj.user_name is None:
        obj.user_name = user.private_chat_name
    if obj.user_name.lower() == clone.name.lower():
        detail = (
            f"User's private chat name ({obj.user_name}) collides with the clone name. "
            "Please retry with a different user_name. Case does not matter."
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
    convo = await Controller.create_conversation(
        obj=obj,
        clone=clone,
        db=db,
        user=user,
        conn=conn,
        tokenizer=tokenizer,
        embedding_client=embedding_client,
    )

    return convo


@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation_by_id(
    conversation: Annotated[models.Conversation, Depends(get_conversation)],
):
    return conversation


@router.patch("/{conversation_id}", response_model=schemas.Conversation)
async def patch_conversation(
    obj: schemas.ConversationUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    conversation: Annotated[models.Conversation, Depends(get_conversation)],
):
    data = obj.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    for k, v in data.items():
        setattr(conversation, k, v)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    from fastapi.encoders import jsonable_encoder

    convo = schemas.Conversation(**jsonable_encoder(conversation))
    return convo


@router.delete("/{conversation_id}", response_class=Response)
async def delete_conversation(
    conversation_id: Annotated[str, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Conversation, Depends(deps.get_superuser)],
):
    convo = await db.get(models.Conversation, conversation_id)
    if not convo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(convo)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------- Messages ----------- #
@router.get("/{conversation_id}/messages", response_model=list[schemas.Message])
async def get_messages(
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
    user: Annotated[models.Creator, Depends(deps.get_current_active_user)],
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
    if q is None and sort in [MsgSortType.similarity, MsgSortType.embedding]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'If using sort type ({sort}), you must pass a query parameter "q"',
        )
    if not (conversation := await db.get(models.Conversation, id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found.",
        )
    if not user.is_superuser and not conversation.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this conversation.",
        )
    query = (
        sa.select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .where(models.Message.is_active == is_active)
        .where(models.Message.is_main == is_main)
        .offset(offset)
        .limit(limit)
    )
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
            # make the index really fast
            await db.execute(sa.text("SET pg_trgm.word_similarity_threshold = 0.7"))
            sml = models.Message.case_insensitive_content.word_similarity(q)
    match sort:
        case MsgSortType.embedding:
            query = query.where(models.Message.embedding.is_not(None)).order_by(
                dist.asc()
            )
        case MsgSortType.similarity:
            query = query.where(models.Message.op("%>")(q)).order_by(sml.desc())
        case MsgSortType.newest:
            query = query.order_by(models.Message.timestamp.desc())
        case MsgSortType.oldest:
            query = query.order_by(models.Message.timestamp.asc())
    r = await db.scalars(query)
    msgs = r.all()
    return msgs


@router.post("/{conversation_id}/messages", response_model=schemas.Message)
async def receive_message(
    msg_create: schemas.MessageCreate,
    conversation_id: Annotated[str, Path()],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    key = f"{conversation_id}::generating"
    if (await controller.cache.conn.get(key)) is not None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cannot send a message while the clone is generating a response. "
                "Please wait until current generation is complete."
            ),
        )
    # timeout for accidental deadlocks
    await controller.cache.conn.set(key, b"", ex=5)
    try:
        # TODO (Jonny): we'll need to handle multiple models on the backend eventually
        # TODO (Jonny): put back in, in prod
        # if not user.nsfw_enabled:
        #     if (r := await openai_moderation_check(msg_create.content)).flagged:
        #         reasons = [k for k, v in r.categories.items() if v]
        #         detail = (
        #             "The received message violates the following content moderation rules:"
        #             f" {reasons}. Please upgrade to the NSFW plan for unmoderated chat."
        #         )
        #         raise HTTPException(
        #             status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        #         )
        msg = await controller.add_user_message(msg_create=msg_create)
    finally:
        controller.cache.conn.delete(key)
    return msg


@router.post("/{conversation_id}/generate", response_model=schemas.Message)
async def generate_clone_message(
    msg_gen: schemas.MessageGenerate,
    conversation_id: Annotated[str, Path()],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    key = f"{conversation_id}::generating"
    if (await controller.cache.conn.get(key)) is not None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cannot send a generate while the clone is receiving a response. "
                "Please wait until current message has been received."
            ),
        )
    await controller.cache.conn.set(key, b"", ex=60)
    try:
        msg = await controller.generate_message(msg_gen)
    finally:
        controller.cache.conn.delete(key)
    return msg


@router.post(
    "/{conversation_id}/current_revisions", response_model=list[schemas.Message]
)
async def generate_revision_to_clone_message(
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    msgs = await controller.clonedb.get_messages(num_messages=2)
    if len(msgs) < 2:
        return []
    if len(msgs) == 1:
        return msgs
    parent = msgs[-1]
    return parent.children


@router.delete("/{conversation_id}/messages/{message_id}", response_class=Response)
async def delete_message(
    message_id: Annotated[str, Path()],
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_current_active_user)],
):
    msg = await db.get(models.Message, message_id)
    if (
        not msg
        or (not msg.is_active and not user.is_superuser)
        or msg.conversation_id != conversation_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found.",
        )
    if not user.is_superuser and not msg.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized user: {user.id}.",
        )
    memory_strategy = await db.scalar(
        sa.select(models.Conversation.memory_strategy).where(
            models.Conversation.id == conversation_id
        )
    )
    if memory_strategy != MemoryStrategy.none:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Message deletion is not allowed for anything but the Zero Memory Strategy",
        )
    r = await db.scalars(
        sa.select(models.Message)
        .where(models.Message.timestamp >= msg.timestamp)
        .where(models.Message.conversation_id == conversation_id)
    )
    for m in r.all():
        m.is_active = False
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{conversation_id}/messages/{message_id}", response_model=schemas.Message)
async def get_message_by_id(
    message_id: Annotated[str, Path(min_length=36, max_length=36)],
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.Creator, Depends(deps.get_current_active_user)],
):
    msg = await db.get(models.Message, message_id)
    if (
        not msg
        or (not msg.is_active and not user.is_superuser)
        or msg.conversation_id != conversation_id
    ):
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


@router.post(
    "/{conversation_id}/messages/{message_id}/is_main", response_model=schemas.Message
)
async def set_revision_as_main(
    message_id: Annotated[str, Path(min_length=36, max_length=36)],
    conversation_id: Annotated[str, Path(min_length=36, max_length=36)],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    msg = await controller.set_revision_as_main(message_id)
    return msg

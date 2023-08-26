import datetime
import enum
import json
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from fastapi.routing import APIRouter
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.clone.controller import Controller
from app.clone.types import AdaptationStrategy, InformationStrategy, MemoryStrategy
from app.deps.limiter import user_id_cookie_fixed_window_ratelimiter
from app.deps.users import Plan, UserAndPlan
from app.embedding import EmbeddingClient
from app.external.moderation import openai_moderation_check
from app.settings import settings
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


class ConvoSortType(str, enum.Enum):
    newest: str = "newest"
    oldest: str = "oldest"
    most_messages: str = "most_messages"
    fewest_messages: str = "fewest_messages"


async def get_conversation(
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
) -> models.Conversation:
    convo = await db.get(models.Conversation, conversation_id)
    if not convo or not convo.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation ({conversation_id}) not found.",
        )
    if not user.is_superuser and convo.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return convo


@router.get("/", response_model=list[schemas.Conversation], status_code=200)
async def query_conversations(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    tags: Annotated[list[int] | None, Query()] = None,
    clone_name: Annotated[str | None, Query()] = None,
    clone_id: Annotated[uuid.UUID | None, Query()] = None,
    sort: Annotated[ConvoSortType, Query()] = ConvoSortType.newest,
    memory_strategy: Annotated[MemoryStrategy | None, Query()] = None,
    adaptation_strategy: Annotated[AdaptationStrategy | None, Query()] = None,
    information_strategy: Annotated[InformationStrategy | None, Query()] = None,
    updated_after: Annotated[datetime.datetime | None, Query()] = None,
    updated_before: Annotated[datetime.datetime | None, Query()] = None,
    offset: Annotated[int, Query(title="database row offset", ge=0)] = 0,
    limit: Annotated[int, Query(title="database row return limit", ge=1, le=60)] = 10,
):
    query = sa.select(models.Conversation).where(models.Conversation.user_id == user.id)
    if clone_name is not None:
        query = query.where(
            models.Conversation.case_insensitive_clone_name.ilike(f"%{clone_name}%")
        )
    if clone_id is not None:
        query = query.where(models.Conversation.clone_id == clone_id)
    if updated_after is not None:
        query = query.where(models.Conversation.updated_at >= updated_after)
    if updated_before is not None:
        query = query.where(models.Conversation.updated_at <= updated_before)
    if adaptation_strategy is not None:
        query = query.where(
            models.Conversation.adaptation_strategy == adaptation_strategy
        )
    if memory_strategy is not None:
        query = query.where(models.Conversation.memory_strategy == memory_strategy)
    if information_strategy is not None:
        query = query.where(
            models.Conversation.information_strategy == information_strategy
        )
    if tags is not None:
        subquery = (
            sa.select(models.clones_to_tags.c.clone_id)
            .where(models.clones_to_tags.c.tag_id.in_(tags))
            .group_by(models.clones_to_tags.c.clone_id)
            .having(sa.func.count(models.clones_to_tags.c.clone_id) == len(tags))
            .subquery()
        )
        query = query.join(
            subquery, models.Conversation.clone_id == subquery.c.clone_id
        )
    match sort:
        case ConvoSortType.newest:
            query = query.order_by(models.Conversation.updated_at.desc())
        case ConvoSortType.oldest:
            query = query.order_by(models.Conversation.updated_at.asc())
        case ConvoSortType.most_messages:
            query = query.order_by(models.Conversation.num_messages_ever.desc())
        case ConvoSortType.fewest_messages:
            query = query.order_by(models.Conversation.num_messages_ever.asc())
    query = query.offset(offset=offset).limit(limit=limit)
    convos = await db.scalars(query)
    return convos.unique().all()


@router.get(
    "/sidebar", response_model=list[schemas.ConversationInSidebar], status_code=200
)
async def get_sidebar_conversations(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    convo_limit: Annotated[
        int, Query(title="Number of conversations to return per clone", ge=1, le=5)
    ] = 3,
    offset: Annotated[int, Query(title="database row offset", ge=0)] = 0,
    limit: Annotated[int, Query(title="database row return limit", ge=1, le=60)] = 30,
):
    # Rank from newest to oldest
    rank = (
        sa.func.rank()
        .over(
            order_by=models.Conversation.updated_at.desc(),
            partition_by=models.Conversation.clone_id,
        )
        .label("rank")
    )

    # Use this as a filter to sort the final list
    group_updated_at = (
        sa.func.max(models.Conversation.updated_at)
        .over(partition_by=models.Conversation.clone_id)
        .label("group_updated_at")
    )

    # Run a subquery to fill in the partition values
    subquery = (
        sa.select(models.Conversation, rank, group_updated_at)
        .where(models.Conversation.user_id == user.id)
        .subquery()
    )

    # Keep only the top ranking convos in terms of recency
    query = (
        sa.select(subquery)
        .where(subquery.c.rank <= convo_limit)
        .order_by(subquery.c.group_updated_at, subquery.c.rank, subquery.c.name)
    )

    query = query.offset(offset).limit(limit)

    # Get back row-objects, which need to be converted to the schemas
    rows = await db.execute(query)
    convos = [schemas.ConversationInSidebar.model_validate(x) for x in rows.unique()]
    return convos


# TODO (Jonny): put a paywall behind this endpoint after X messages, need to add user permissions
@router.post(
    "/", response_model=schemas.Conversation, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    obj: schemas.ConversationCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user_and_plan: Annotated[UserAndPlan, Depends(deps.get_free_or_paying_user)],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    tokenizer: Annotated[Tokenizer, Depends(deps.get_tokenizer)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
):
    user = user_and_plan.user
    plan = user_and_plan.plan
    if obj.memory_strategy != MemoryStrategy.zero and plan != Plan.plus:
        # TODO (Jonny): is this for clonr+ or for normal subscribers?
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Long-term memory only available for clonr+ subscribers.",
        )

    clone = await db.get(models.Clone, obj.clone_id)
    if not clone or not clone.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clone ({obj.clone_id}) not found.",
        )

    if not clone.is_public and clone.creator_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

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

    if plan == Plan.free:
        user.num_free_messages_sent = user.num_free_messages_sent + 1
        await db.commit()

    await db.refresh(convo)
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
    convo = schemas.Conversation(**jsonable_encoder(conversation))
    return convo


@router.delete(
    "/{conversation_id}",
    response_class=Response,
    dependencies=[Depends(deps.get_superuser)],
)
async def delete_conversation(
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
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
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    embedding_client: Annotated[EmbeddingClient, Depends(deps.get_embedding_client)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    q: Annotated[str | None, Query(max_length=512)] = None,
    sort: Annotated[MsgSortType, Query()] = MsgSortType.newest,
    sent_after: Annotated[datetime.datetime | None, Query()] = None,
    sent_before: Annotated[datetime.datetime | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=60)] = 20,
    is_active: Annotated[bool, Query()] = True,
    is_main: Annotated[bool, Query()] = True,
):
    if not user.is_superuser and not (is_active and is_main):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Query parameters is_active, is_main are not allowed",
        )
    if q is None and sort in [MsgSortType.similarity, MsgSortType.embedding]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'If using sort type ({sort}), you must pass a query parameter "q"',
        )
    if not (conversation := await db.get(models.Conversation, conversation_id)):
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


@router.post(
    "/{conversation_id}/messages",
    response_model=schemas.Message,
    status_code=201,
    dependencies=[
        Depends(
            user_id_cookie_fixed_window_ratelimiter("5/second"),
        )  # TODO (Jonny): This needs another ratelimit for long-term mem since it incurs LLM costs
    ],
)
async def receive_message(
    msg_create: schemas.MessageCreate,
    conversation_id: Annotated[uuid.UUID, Path()],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    key = f"{conversation_id}::generating"
    if (await controller.clonedb.cache.conn.get(key)) is not None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cannot send a message while the clone is generating a response. "
                "Please wait until current generation is complete."
            ),
        )
    # timeout for accidental deadlocks
    await controller.clonedb.cache.conn.set(key, b"", ex=5)
    try:
        # TODO (Jonny): we'll need to handle multiple models on the backend eventually
        # TODO (Jonny): put back in, in prod
        if not settings.DEV and not controller.user.nsfw_enabled:
            logger.info("Content moderation request to OpenAI")
            if (r := await openai_moderation_check(msg_create.content)).flagged:
                reasons = [k for k, v in r.categories.items() if v]
                violation = models.ContentViolation(
                    content=msg_create.content,
                    reasons=json.dumps(reasons),
                    clone_id=controller.clone.id,
                    conversation_id=controller.conversation.id,
                    user_id=controller.conversation.user_id,
                )
                controller.clonedb.db.add(violation)
                await controller.clonedb.db.commit()
                detail = (
                    "The received message violates the following content moderation rules:"
                    f" {reasons}. Please upgrade to the NSFW plan for unmoderated chat."
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=detail
                )
        msg = await controller.add_user_message(msg_create=msg_create)
    finally:
        await controller.clonedb.cache.conn.delete(key)
    return msg


@router.post(
    "/{conversation_id}/generate",
    response_model=schemas.Message,
    status_code=201,
    dependencies=[
        Depends(user_id_cookie_fixed_window_ratelimiter("3000/month")),
        Depends(
            user_id_cookie_fixed_window_ratelimiter("300/day"),
        ),
    ],
)
async def generate_clone_message(
    msg_gen: schemas.MessageGenerate,
    conversation_id: Annotated[uuid.UUID, Path()],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    if (
        msg_gen.is_revision
        and controller.conversation.memory_strategy != MemoryStrategy.zero
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message regeneration is not allowed for anything but the Zero Memory Strategy",
        )
    key = f"{conversation_id}::generating"
    if (await controller.clonedb.cache.conn.get(key)) is not None:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=(
                "Cannot send a generate while the clone is receiving a response. "
                "Please wait until current message has been received."
            ),
        )
    await controller.clonedb.cache.conn.set(key, b"", ex=60)
    try:
        msg = await controller.generate_message(msg_gen)

        if controller.subscription_plan == Plan.free:
            controller.user.num_free_messages_sent = (
                controller.user.num_free_messages_sent + 1
            )
            await controller.clonedb.db.commit()

    finally:
        await controller.clonedb.cache.conn.delete(key)
    return msg


@router.get(
    "/{conversation_id}/current_revisions", response_model=list[schemas.Message]
)
async def get_current_revisions(
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    msgs = await controller.clonedb.get_messages(num_messages=1)
    if not msgs:
        return []
    msg = msgs[0]
    if not msg.is_clone or not msg.parent_id:
        return []
    print(msg)
    r = await controller.clonedb.db.scalars(
        sa.select(models.Message)
        .where(models.Message.parent_id.is_not(None))
        .where(models.Message.parent_id == msg.parent_id)
        .where(models.Message.is_active)
        .where(models.Message.is_clone)
    )
    return r.all()


@router.delete("/{conversation_id}/messages/{message_id}", response_class=Response)
async def delete_message(
    message_id: Annotated[uuid.UUID, Path()],
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    msg = await db.get(models.Message, message_id)
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message {message_id} not found.",
        )
    if not user.is_superuser and msg.conversation_id != conversation_id:
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
    if memory_strategy != MemoryStrategy.zero:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    message_id: Annotated[uuid.UUID, Path()],
    conversation_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
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
    message_id: Annotated[uuid.UUID, Path()],
    controller: Annotated[Controller, Depends(deps.get_controller)],
):
    if controller.conversation.memory_strategy != MemoryStrategy.zero:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message regeneration is not allowed for anything but the Zero Memory Strategy",
        )
    msg = await controller.set_revision_as_main(message_id)
    return msg

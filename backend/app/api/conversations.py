from typing import Annotated

from app import models, schemas
from app.auth.users import current_active_user
from app.db import RedisCache, get_async_redis_cache, get_async_session
from fastapi import Depends, FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5/minute"],
    storage_uri="redis://localhost:6379",
)


def calculate_dynamic_rate_limit(request: Request):
    print("TODO")
    # raise error for now
    raise HTTPException(status_code=400, detail="Not implemented")


router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Conversation)
async def create_conversation(
    obj: schemas.ConversationCreate,
    clone_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    clone = await db.get(models.Clone, clone_id)
    if not clone:
        raise HTTPException(
            status_code=400, detail="Clone corresponding to this key does not exist"
        )
    conversation = models.Conversation(**obj.dict())
    msg = models.Message(
        content=clone.greeting_message,
        sender_name=clone.name,
        from_clone=True,
        conversation=conversation,
    )
    db.add_all([msg, conversation])
    await db.commit()
    await db.refresh(conversation)
    await cache.message_add(msg)
    return conversation


@router.post("/{conversation_id}/messages", response_model=schemas.Message)
async def create_message(
    conversation_id: str,
    message: schemas.MessageCreate,
    clone_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation not found"
        )
    if clone_id != convo.clone_id or user.id != convo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    msg = models.Message(
        **message.dict(), from_clone=False, conversation_id=conversation_id
    )
    db.add(msg)
    await db.commit()
    await db.flush(msg)
    await cache.message_add(msg)
    return msg


@router.get("/", response_model=list[schemas.Conversation])
async def get_conversations(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
):
    promise = await db.scalars(
        select(models.Conversation).where(
            models.Conversation.user_id == user.id,
        )
    )
    return promise.all()


# TODO: revisit this endpoint. Users should be able to access conversations
# using both API Key and user credentials. At the moment, we're only offering
# one or the other. OR maybe not idk. maybe we make this a security thing where
# API Keys completely control their conversations and all that
@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if user.id != convo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    return convo


@router.get("/{conversation_id}/messages", response_model=list[schemas.Message])
async def get_latest_messages(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
    offset: int = 0,
    limit: int = 25,
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if user.id != convo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    # TODO: This blocks access to our DB since we likely won't have cache misses
    # Becomes problematic once our cache fills up! Also the FIFO eviction policy should
    # be in place
    messages = await cache.message_get_latest(convo.id, offset=offset, limit=limit)
    if messages:
        return messages
    promise = await db.scalars(
        select(models.Message)
        .where(models.Message.conversation_id == id)
        .order_by(models.Message.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    messages = promise.all()
    return messages


@router.delete("/{id}", response_model=schemas.Conversation)
async def delete_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if not (convo := db.get(models.Conversation, id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if user.id != convo.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    await cache.conversation_delete(convo.id)
    await db.delete(convo)
    await db.commit()
    return convo


@router.delete(
    "/{conversation_id}/messages/{message_id}", response_model=schemas.Conversation
)
async def delete_message(
    request: Request,
    conversation_id: str,
    message_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if not (convo := await db.get(models.Conversation, conversation_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not (msg := await db.get(models.Message, message_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if user.id != convo.user_id or msg.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    await cache.message_delete(conversation_id=conversation_id, message_id=message_id)
    await db.delete(convo)
    await db.commit()
    return convo


@router.get("/v1/conversation/{convo_id}/response")
@limiter.limit(calculate_dynamic_rate_limit)
async def get_response(
    request: Request,
    convo_id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    ## TODO: modify later, this is a stub
    response = {"response": "hello world"}
    # add to cache
    await cache.conversation_add(convo_id, response)
    return response


@router.get("/total_conversations", response_model=int)
async def get_total_conversations(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if (
        cached_total_conversations := await cache.get_cached_total_conversations(
            user.id
        )
    ) is not None:
        return cached_total_conversations

    total_conversations = await db.scalar(
        select(func.count(models.Conversation.id)).where(
            models.Conversation.user_id == user.id
        )
    )

    await cache.cache_total_conversations(user.id, total_conversations)

    return total_conversations


@router.get("/total_messages", response_model=dict[str, int])
async def get_total_messages(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[schemas.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if (
        cached_total_messages := await cache.get_cached_total_messages(user.id)
    ) is not None:
        return cached_total_messages

    num_msgs_sent = await db.scalar(
        select(func.count(models.Message.id)).where(
            sa.and_(
                models.Message.clone_id == user.id, models.Message.is_clone == False
            )
        )
    )

    num_msgs_received = await db.scalar(
        select(func.count(models.Message.id)).where(
            sa.and_(models.Message.clone_id != user.id, models.Message.is_clone == True)
        )
    )

    await cache.cache_total_messages(user.id, num_msgs_sent, num_msgs_received)

    return {"num_msgs_sent": num_msgs_sent, "num_msgs_received": num_msgs_received}

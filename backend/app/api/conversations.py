from typing import Annotated

from app import models, schemas
from app.auth.api_keys import get_api_key
from app.auth.users import current_active_user
from app.db import ConversationCache, get_async_convo_cache, get_async_session
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{id}", response_model=schemas.Conversation)
async def get_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    promise = await db.scalars(
        select(models.Conversation).where(models.Conversation.id == id)
    )
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not api_key.user_id == obj.user_id or not api_key.clone_id == obj.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    return obj


@router.get("/{id}/messages", response_model=list[schemas.Message])
async def get_latest_messages(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
    cache: Annotated[ConversationCache, Depends(get_async_convo_cache)],
    offset: int = 0,
    limit: int = 25,
):
    promise = await db.scalars(
        select(models.Conversation).where(models.Conversation.id == id)
    )
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not api_key.user_id == obj.user_id or not api_key.clone_id == obj.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    messages = await cache.get(obj.id, offset=offset, limit=limit)
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


@router.post("/{conversation_id}/messages", response_model=list[schemas.Message])
async def create_message(
    conversation_id: str,
    message: schemas.MessageCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
    cache: Annotated[ConversationCache, Depends(get_async_convo_cache)],
):
    promise = await db.scalars(
        select(models.Conversation).where(models.Conversation.id == id)
    )
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not api_key.user_id == obj.user_id or not api_key.clone_id == obj.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")

    # TODO: the message model is broken. It should have a separate sender_id token, since user_id does not actually
    # correspond to a user chatting with the application. Maybe we can just do a boolean like is_bot
    msg = models.Message(
        message=message.message,
        conversation_id=conversation_id,
        user_id=api_key.user_id,
        clone_id=api_key.clone_id,
    )
    db.add(msg)
    await db.commit()
    await db.flush(msg)
    cache.add_message(msg)
    return msg


@router.post("/", response_model=schemas.Conversation)
async def create_conversation(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[ConversationCache, Depends(get_async_convo_cache)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    conv = schemas.ConversationCreate(
        user_id=api_key.user_id, clone_id=api_key.clone_id
    )
    conversation = models.Conversation(**conv.dict())
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    promise = await db.scalars(
        select(models.Clone.greeting_message).where(models.Clone.id == api_key.clone_id)
    )
    greeting = promise.first()
    message = models.Message(
        message=greeting, clone_id=api_key.clone_id, conversation_id=conversation.id
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    await cache.add_message(message)
    return conversation


@router.delete("/{id}", response_model=schemas.Conversation)
async def delete_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[ConversationCache, Depends(get_async_convo_cache)],
    api_key: Annotated[schemas.APIKey, Depends(get_api_key)],
):
    promise = await db.scalars(
        select(models.Conversation).where(models.Conversation.id == id)
    )
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not api_key.user_id == obj.user_id or not api_key.clone_id == obj.clone_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    await db.delete(obj)
    await db.commit()
    await cache.delete(id)
    return obj

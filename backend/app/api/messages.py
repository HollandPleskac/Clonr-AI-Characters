from typing import Annotated, List

from app import models, schemas
from app.db import get_async_session
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{message_id}", response_model=schemas.Message)
async def get_message(
    message_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    message = await db.get(models.Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post("/", response_model=schemas.Message, status_code=201)
async def create_message(
    message_create: schemas.MessageCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        message = models.Message(**message_create.dict())
        db.add(message)
        await db.refresh(message)
        return message


@router.delete("/{message_id}")
async def delete_message(
    message_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    async with db.begin():
        message = await db.get(models.Message, message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        db.delete(message)
        return {"message": "Message deleted"}


@router.get("/conversation/{conversation_id}", response_model=List[schemas.Message])
async def get_conversation_messages(
    conversation_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    messages = await db.filter(models.Message.conversation_id == conversation_id).all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages


@router.get("/user/{user_id}", response_model=List[schemas.Message])
async def get_user_messages(
    user_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    messages = await db.filter(models.Message.user_id == user_id).all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return messages

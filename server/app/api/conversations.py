from typing import Annotated, List

from app import models, schemas
from app.db import get_async_session
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{conversation_id}", response_model=schemas.Conversation)
async def get_conversation(
    conversation_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    conversation = await db.get(models.Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/", response_model=schemas.Conversation, status_code=201)
async def create_conversation(
    conversation_create: schemas.ConversationCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        conversation = models.Conversation(**conversation_create.dict())
        db.add(conversation)
        await db.refresh(conversation)
        return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    async with db.begin():
        conversation = await db.get(models.Conversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        db.delete(conversation)
        return {"message": "Conversation deleted"}


@router.get("/user/{user_id}", response_model=List[schemas.Conversation])
async def get_user_conversations(
    user_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    conversations = await db.filter(models.Conversation.user_id == user_id).all()
    if not conversations:
        raise HTTPException(status_code=404, detail="Conversations not found")
    return conversations


@router.get("/clone/{clone_id}", response_model=List[schemas.Conversation])
async def get_clone_conversations(
    clone_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    conversations = await db.filter(models.Conversation.clone_id == clone_id).all()
    if not conversations:
        raise HTTPException(status_code=404, detail="Conversations not found")
    return conversations

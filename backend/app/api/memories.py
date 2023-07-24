from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.auth.users import current_active_user
from app import models, schemas
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/memories",
    tags=["memories"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Memory)
async def create_memory(
    memory: schemas.MemoryCreate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    new_memory = models.Memory(**memory.dict())
    db.add(new_memory)
    await db.commit()
    await db.refresh(new_memory)
    print(type(new_memory.memory_embedding))
    # <class 'numpy.ndarray'> -> list of floats
    new_memory.memory_embedding = list(new_memory.memory_embedding)
    return new_memory


@router.get("/{id}", response_model=schemas.Memory)
async def get_memory(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    memory = await db.get(models.Memory, id)
    if memory is None or memory.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found"
        )
    return memory


@router.put("/{id}", response_model=schemas.Memory)
async def update_memory(
    id: str,
    updated_memory: schemas.MemoryUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    memory = await db.get(models.Memory, id)
    if memory is None or memory.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found"
        )
    for field, value in updated_memory.dict(exclude_unset=True).items():
        setattr(memory, field, value)
    await db.commit()
    await db.refresh(memory)
    return memory


@router.delete("/{id}", response_model=schemas.Memory)
async def delete_memory(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    memory = await db.get(models.Memory, id)
    if memory is None or memory.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found"
        )
    db.delete(memory)
    await db.commit()
    return memory


@router.get("/conversation/{conversation_id}", response_model=List[schemas.Memory])
async def get_memories_for_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    memories = await db.execute(
        select(models.Memory)
        .filter(models.Memory.conversation_id == conversation_id)
        .join(models.Clone)
        .filter(
            models.Clone.conversation_id == conversation_id
            and models.Clone.creator_id == user.id
        )
    )
    return memories.scalars().all()

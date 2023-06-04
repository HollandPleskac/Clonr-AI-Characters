from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.auth.users import current_active_user
from app import models, schemas
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/reflections",
    tags=["reflections"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Reflection)
async def create_reflection(
    reflection: schemas.ReflectionCreate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    new_reflection = models.Reflection(**reflection.dict())
    user.reflections.append(new_reflection)
    db.add(new_reflection)
    await db.commit()
    await db.refresh(new_reflection)
    return new_reflection


@router.get("/{id}", response_model=schemas.Reflection)
async def get_reflection(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    reflection = await db.get(models.Reflection, id)
    if reflection is None or reflection.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reflection not found"
        )
    return reflection


@router.put("/{id}", response_model=schemas.Reflection)
async def update_reflection(
    id: str,
    updated_reflection: schemas.ReflectionUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    reflection = await db.get(models.Reflection, id)
    if reflection is None or reflection.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reflection not found"
        )
    for field, value in updated_reflection.dict(exclude_unset=True).items():
        setattr(reflection, field, value)
    await db.commit()
    await db.refresh(reflection)
    return reflection


@router.delete("/{id}", response_model=schemas.Reflection)
async def delete_reflection(
    id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    reflection = await db.get(models.Reflection, id)
    if reflection is None or reflection.clone.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reflection not found"
        )
    db.delete(reflection)
    await db.commit()
    return reflection


@router.get("/conversation/{conversation_id}", response_model=List[schemas.Fact])
async def get_reflections_for_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_async_session),
    user: models.User = Depends(current_active_user),
):
    reflections = await db.execute(
        select(models.Reflection)
        .filter(models.Reflection.conversation_id == conversation_id)
        .join(models.Clone)
        .filter(
            models.Clone.conversation_id == conversation_id
            and models.Clone.user_id == user.id
        )
    )
    return reflections.scalars().all()

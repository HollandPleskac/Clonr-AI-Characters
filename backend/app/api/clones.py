from typing import Annotated

from app import models, schemas
from app.db import get_async_session
from app.users import current_active_user
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/clones",
    tags=["clones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{id}", response_model=schemas.Clone)
async def get(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    promise = await db.scalars(select(models.Clone).where(models.Clone.id == id))
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not obj.is_public and not obj.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    return obj


@router.post("/", response_model=schemas.Clone)
async def create(
    obj: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    data = obj.dict()
    data["user_id"] = user.id
    clone = models.Clone(**data)
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone


@router.put("/{id}", response_model=schemas.Clone)
async def update_(
    id: str,
    obj: schemas.CloneUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    promise = await db.scalars(
        update(models.Clone)
        .where(models.Clone.id == id)
        .values(**obj.dict(exclude_unset=True))
        .returning(models.Clone)
    )
    clone = promise.first()
    await db.commit()
    await db.refresh(clone)
    return clone


@router.delete("/{id}", response_model=schemas.Clone)
async def delete(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    promise = await db.scalars(select(models.Clone).where(models.Clone.id == id))
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    await db.delete(obj)
    await db.commit()
    return obj

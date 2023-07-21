from typing import Annotated

from app import models, schemas
from app.auth.users import current_active_user
from app.db import get_async_session
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/clones",
    tags=["clones"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Clone)
async def create(
    obj: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    clone = models.Clone(**obj.dict(), user_id=user.id)
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone


@router.get("/{id}", response_model=schemas.Clone)
async def get(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    if (clone := await db.get(models.Clone, id)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    if not clone.is_public and not clone.user_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not found")
    return clone


@router.get("/", response_model=list[schemas.Clone])
async def get_clones(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    limit: int = 10,
    offset: int = 0,
):
    clones = await db.scalars(
        select(models.Clone)
        .where(models.Clone.creator_id == user.id)
        .order_by(models.Clone.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return clones.all()


@router.put("/{id}", response_model=schemas.Clone)
async def update_(
    id: str,
    obj: schemas.CloneUpdate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if not await db.get(models.Clone, id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
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
    if (clone := await db.get(models.Clone, id)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    await db.delete(clone)
    await db.commit()
    return clone

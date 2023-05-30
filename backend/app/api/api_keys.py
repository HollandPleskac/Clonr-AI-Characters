from typing import Annotated, Optional

from app import models, schemas
from app.auth.users import current_active_user
from app.db import APIKeyCache, get_async_apikey_cache, get_async_session
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/apikeys",
    tags=["apikeys"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[schemas.APIKey])
async def get(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    clone_id: Optional[str] = None,
    user_id: Optional[str] = None,
    name: Optional[str] = None,
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
):
    if user_id is not None and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use Oauth authentication instead of user_id.",
        )
    if user_id is None and user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="As superuser, must include user_id.",
        )
    stmt = select(models.APIKey).where(models.APIKey.user_id == user.id)
    if clone_id is not None:
        stmt = stmt.where(models.APIKey.clone_id == clone_id)
    if name is not None:
        stmt = stmt.where(models.APIKey.name == name)
    if offset is not None:
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid offset: {offset}",
            )
        stmt = stmt.offset(offset)
    if limit is not None:
        if limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid limit: {limit}",
            )
        stmt = stmt.limit(limit)
    promise = await db.scalars(stmt)
    keys = promise.all()
    return keys


@router.post("/", response_model=schemas.APIKeyDB)
async def create(
    obj: schemas.APIKeyCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    cache: Annotated[APIKeyCache, Depends(get_async_apikey_cache)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="For security, API Keys are only available on request. please regenerate your API Key.",
        )
    if user.is_superuser and obj.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As superuser, you must supply a user_id",
        )
    if not user.is_superuser:
        obj = schemas.APIKeyCreate(**obj.dict(exclude_unset=True), user_id=user.id)
    key = models.APIKey(**obj.dict(exclude_unset=True))
    db.add(key)
    await db.commit()
    await db.flush(key)
    await cache.add(key)
    return key


@router.delete("/{id}", response_model=schemas.APIKey)
async def get(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    cache: Annotated[APIKeyCache, Depends(get_async_apikey_cache)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    promise = await db.scalars(select(models.APIKey).where(models.APIKey.id == id))
    obj = promise.first()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    await db.delete(obj)
    await db.commit()
    await cache.delete(obj)
    return obj

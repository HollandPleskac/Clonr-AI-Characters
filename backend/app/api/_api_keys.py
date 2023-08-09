# TODO (Jonny): API Keys are a V2 features, so this goes to the backlog for now.

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth.users import current_active_user
from app.db import RedisCache, get_async_redis_cache, get_async_session
from app.utils import generate_api_key, sha256_hash

router = APIRouter(
    prefix="/api_keys",
    tags=["api_keys"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.APIKeyOnce)
async def create(
    obj: schemas.APIKeyCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if user.is_superuser and obj.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As superuser, you must supply a user_id",
        )
    if not user.is_superuser:
        obj.user_id = user.id
    if (clone := await db.get(models.Clone, obj.clone_id)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not found."
        )
    if clone.user_id != obj.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    key = generate_api_key()
    hashed_key = sha256_hash(key)
    data = obj.dict(exclude_unset=True)
    data.pop("user_id")
    data["hashed_key"] = hashed_key
    key_obj = models.APIKey(**data)
    db.add(key_obj)
    await db.commit()
    await db.flush(key_obj)
    await cache.api_key_create(key_obj)
    res = schemas.APIKeyOnce(**jsonable_encoder(key_obj), key=key)
    return res


@router.get("/", response_model=list[schemas.APIKey])
async def get(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    id: Optional[str] = None,
    clone_id: Optional[str] = None,
    user_id: Optional[str] = None,
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
):
    if user_id is None:
        user_id = user.id
    elif not user.is_superuser:
        raise HTTPException(status_code=403)
    stmt = (
        select(models.APIKey)
        .join(models.Clone, models.Clone.id == models.APIKey.clone_id)
        .join(models.User, models.User.id == models.Clone.creator_id)
        .where(models.User.id == user_id)
    )
    if id is not None:
        stmt = stmt.where(models.APIKey.id == id)
    if clone_id is not None:
        stmt = stmt.where(models.APIKey.clone_id == clone_id)
    stmt = stmt.offset(offset).limit(limit)
    promise = await db.scalars(stmt)
    keys = promise.all()
    return keys


@router.delete("/{id}", response_model=schemas.APIKey)
async def get_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
    cache: Annotated[RedisCache, Depends(get_async_redis_cache)],
):
    if not user.is_superuser and not id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    if (key := await db.get(models.APIKey, id)) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
    # order is reversed on deletion, since cache falls back to DB on misses.
    await cache.api_key_delete(key.hashed_key)
    await db.delete(key)
    await db.commit()
    return key

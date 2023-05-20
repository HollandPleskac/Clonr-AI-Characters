from typing import Annotated, List

from app.db import get_async_session
from app import models, schemas
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=schemas.User, status_code=201)
async def create_user(
    user_create: schemas.UserCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        new_user = models.User(email=user_create.email)
        db.add(new_user)
        await db.refresh(new_user)
    return new_user


@router.get("/{user_id}/clones", response_model=List[schemas.Clone])
async def get_user_clones(
    user_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.clones


@router.post("/{user_id}/clones", response_model=schemas.Clone, status_code=201)
async def create_user_clone(
    user_id: str,
    clone_create: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        user = await db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_clone = models.Clone(**clone_create.dict(), user_id=user_id)
        db.add(new_clone)
        await db.refresh(new_clone)
    return new_clone

from typing import Annotated, List

from app.db import get_async_session
from app.models import Clone, User
from app.schemas import Clone, CloneCreate, User, UserCreate
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    async with get_async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@router.post("/", response_model=User, status_code=201)
async def create_user(user_create: UserCreate):
    async with get_async_session() as session:
        new_user = User(email=user_create.email)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


@router.get("/{user_id}/clones", response_model=List[Clone])
async def get_user_clones(user_id: str):
    async with get_async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.clones


@router.post("/{user_id}/clones", response_model=Clone, status_code=201)
async def create_user_clone(user_id: str, clone_create: CloneCreate):
    async with get_async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_clone = Clone(**clone_create.dict(), user_id=user_id)
        session.add(new_clone)
        await session.commit()
        await session.refresh(new_clone)
        return new_clone

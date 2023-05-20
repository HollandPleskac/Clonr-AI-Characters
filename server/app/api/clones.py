from app.db import get_async_session
from app.models import Clone, User
from app.schemas import Clone, CloneCreate, User, UserCreate
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/clones",
    tags=["clones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{clone_id}", response_model=Clone)
async def get_eleven_clone(clone_id: str):
    async with get_async_session() as session:
        eleven_clone = await session.get(Clone, clone_id)
        if not eleven_clone:
            raise HTTPException(status_code=404, detail="Clone not found")
        return eleven_clone


@router.post("/", response_model=Clone, status_code=201)
async def create_clone(clone_create: CloneCreate):
    async with get_async_session() as session:
        new_eleven_clone = Clone(**clone_create.dict())
        session.add(new_eleven_clone)
        await session.commit()
        await session.refresh(new_eleven_clone)
        return new_eleven_clone


@router.delete("/{clone_id}")
async def delete_eleven_clone(clone_id: str):
    async with get_async_session() as session:
        eleven_clone = await session.get(Clone, clone_id)
        if not eleven_clone:
            raise HTTPException(status_code=404, detail="Clone not found")
        session.delete(eleven_clone)
        await session.commit()
        return {"message": "Clone deleted"}

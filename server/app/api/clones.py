from typing import Annotated
from app.db import get_async_session
from app import models, schemas
from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/clones",
    tags=["clones"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{clone_id}", response_model=schemas.Clone)
async def get_clone(
    clone_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    clone = await db.get(models.Clone, clone_id)
    if not clone:
        raise HTTPException(status_code=404, detail="Clone not found")
    return clone


@router.post("/", response_model=schemas.Clone, status_code=201)
async def create_clone(
    clone_create: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    async with db.begin():
        clone = models.Clone(**clone_create.dict())
        db.add(clone)
        await db.refresh(clone)
        return clone


@router.delete("/{clone_id}")
async def delete_clone(
    clone_id: str, db: Annotated[AsyncSession, Depends(get_async_session)]
):
    async with db.begin():
        clone = await db.get(models.Clone, clone_id)
        if not clone:
            raise HTTPException(status_code=404, detail="Clone not found")
        db.delete(clone)
        return {"message": "Clone deleted"}

from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import get_async_session

router = APIRouter(
    prefix="/nsfw",
    tags=["nsfw"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.NSFWSignup)
async def create(
    obj: schemas.NSFWSignupCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    signup = models.NSFWSignup(**obj.dict())
    db.add(signup)
    await db.commit()
    await db.refresh(signup)
    return signup


@router.get("/", response_model=list[schemas.NSFWSignup])
async def get_signups(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    limit: int = 10,
    offset: int = 0,
):
    signups = await db.scalars(
        select(models.NSFWSignup)
        .order_by(models.NSFWSignup.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return signups.all()

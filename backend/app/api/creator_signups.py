from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth.users import current_active_user
from app.db import get_async_session

router = APIRouter(
    prefix="/creators",
    tags=["creators"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.CreatorPartnerProgramSignup)
async def create(
    obj: schemas.CreatorPartnerProgramSignupCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    signup = models.CreatorPartnerProgramSignup(**obj.dict())
    db.add(signup)
    await db.commit()
    await db.refresh(signup)
    return signup


@router.get("/", response_model=list[schemas.CreatorPartnerProgramSignup])
async def get_signups(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    limit: int = 10,
    offset: int = 0,
):
    signups = await db.scalars(
        select(models.CreatorPartnerProgramSignup)
        .order_by(models.CreatorPartnerProgramSignup.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return signups.all()

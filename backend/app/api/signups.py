from typing import Annotated
from fastapi import Depends, status, Query
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app import deps, models, schemas


router = APIRouter(
    prefix="/signup",
    tags=["signups"],
    responses={404: {"description": "Not found"}},
)


@router.post("/plus", response_model=schemas.ClonrPlusSignup)
async def plus_signup(
    obj: schemas.ClonrPlusSignupCreate,
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if await db.scalar(
        sa.select(models.ClonrPlusSignup.user_id).where(
            models.ClonrPlusSignup.user_id == user.id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="User has already signed up",
        )
    signup = models.ClonrPlusSignup(**obj.model_dump(), user_id=user.id)
    db.add(signup)
    await db.commit()
    await db.refresh(signup)
    return signup


@router.get(
    "/plus",
    response_model=list[schemas.ClonrPlusSignup],
    dependencies=[Depends(deps.get_superuser)],
)
async def get_plus_signups(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 20,
):
    signups = await db.scalars(
        sa.select(models.ClonrPlusSignup)
        .order_by(models.ClonrPlusSignup.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return signups.all()


@router.post("/creators", response_model=schemas.CreatorPartnerProgramSignup)
async def creator_signup(
    obj: schemas.CreatorPartnerProgramSignupCreate,
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if await db.scalar(
        sa.select(models.CreatorPartnerProgramSignup.user_id).where(
            models.CreatorPartnerProgramSignup.user_id == user.id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="User has already signed up",
        )
    signup = models.CreatorPartnerProgramSignup(**obj.model_dump(), user_id=user.id)
    db.add(signup)
    await db.commit()
    await db.refresh(signup)
    return signup


@router.get(
    "/plus",
    response_model=list[schemas.CreatorPartnerProgramSignup],
    dependencies=[Depends(deps.get_superuser)],
)
async def get_creator_signups(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 20,
):
    signups = await db.scalars(
        sa.select(models.CreatorPartnerProgramSignup)
        .order_by(models.CreatorPartnerProgramSignup.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return signups.all()

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth.users import current_active_creator, current_active_user, get_superuser
from app.db import get_async_session

router = APIRouter(
    prefix="/creators",
    tags=["creators"],
    responses={404: {"description": "Not found"}},
)


# Doesn't actually delete anything O.o
@router.patch("/me", response_model=schemas.Creator)
async def patch(
    obj: schemas.CreatorPatch,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    not_modified = True
    if creator := await db.get(models.Creator, user.id):
        for k, v in obj.dict(exclude_unset=True).items():
            if v != getattr(creator, k):
                not_modified = False
                setattr(creator, k, v)
        if not_modified:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="No modifications made to creator.",
            )
        else:
            db.add(creator)
            await db.commit()
            await db.refresh(creator)
            return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User is not currently a creator.",
    )


@router.get("/me", response_model=schemas.Creator)
async def get_me(creator: Annotated[models.User, Depends(current_active_creator)]):
    return creator


@router.get(
    "/{id}", response_model=schemas.Creator, dependencies=[Depends(get_superuser)]
)
async def get_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if creator := await db.get(models.Creator, id):
        return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Creator ({id}) does not exist."
    )


@router.delete("/{id}", dependencies=[Depends(get_superuser)])
async def delete_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if creator := await db.get(models.Creator, id):
        db.delete(creator)
        await db.commit()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Creator ({id}) does not exist."
    )


# TODO (Jonny): WHY THE FUCK DOES THE CREATORS ROUTE BREAK BUT NOTHING ELSE DOES???
# UPDATE (Jonny): if you send a request to /creators/ it's actually ok, you need a / at the end for some reason.
# NOTE (Jonny): The current structure requires that all creators sign up
# first as users, and then upgrade to a creator account. This should expedite
# launch time, but also might be confusing. Maybe in the future we should add
# optional arguments to this to create a User + Creator? Idk then we have to do an internal
# api-call b/c fastapi-users is so encapsulated
@router.post("/upgrade", response_model=schemas.Creator, status_code=201)
async def create(
    obj: schemas.CreatorCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    creator = await db.get(models.Creator, user.id)
    if creator is None:
        creator = models.Creator(**obj.dict(), user_id=user.id)
        db.add(creator)
        await db.commit()
        await db.refresh(creator)
        return creator
    elif not creator.is_active:
        creator.is_active = True
        db.add(creator)
        # TODO (Jonny): are we gonna hit some exceptions here?
        await db.commit()
        await db.refresh(creator)
        return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User is already a creator.",
    )

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.settings import settings

router = APIRouter(
    prefix="/creators",
    tags=["creators"],
    responses={404: {"description": "Not found"}},
)


# Doesn't actually delete anything O.o
@router.patch("/me", response_model=schemas.Creator)
async def patch_me(
    obj: schemas.CreatorPatch,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    creator: Annotated[models.User, Depends(deps.get_current_active_creator)],
):
    not_modified = True
    for k, v in obj.model_dump(exclude_unset=True).items():
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


@router.get("/me", response_model=schemas.Creator)
async def get_me(
    creator: Annotated[models.User, Depends(deps.get_current_active_creator)]
):
    return creator


@router.get(
    "/{id}", response_model=schemas.Creator, dependencies=[Depends(deps.get_superuser)]
)
async def get_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if creator := await db.get(models.Creator, id):
        return creator
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Creator ({id}) does not exist."
    )


@router.patch("/{creator_id}", response_model=schemas.Creator)
async def patch_creator_as_superuser(
    obj: schemas.CreatorPatch,
    creator_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_superuser)],
):
    if not (creator := await db.get(models.Creator, creator_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Creator does not exist."
        )
    not_modified = True
    for k, v in obj.model_dump(exclude_unset=True).items():
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


@router.delete(
    "/{id}",
    dependencies=[Depends(deps.get_superuser)],
)
async def delete_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if creator := await db.get(models.Creator, id):
        await db.delete(creator)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Creator ({id}) does not exist."
    )


# NOTE (Jonny): The current structure requires that all creators sign up
# first as users, and then upgrade to a creator account.
@router.post("/upgrade", response_model=schemas.Creator, status_code=201)
async def create(
    obj: schemas.CreatorCreate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    if not settings.DEV and not user.is_superuser:
        # redirect to our signup page?
        # NOTE (Jonny): lol idk if this status is being used correctly
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="The Creator Partner Program is not yet availble. Please join the waitlist!",
        )
    creator = await db.get(models.Creator, user.id)
    if creator is None:
        creator = models.Creator(**obj.model_dump(), user_id=user.id)
        db.add(creator)
    elif not creator.is_active:
        creator.is_active = True
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a creator.",
        )
    await db.commit()
    await db.refresh(creator)
    return creator

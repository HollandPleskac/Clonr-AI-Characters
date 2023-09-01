import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# Doesn't actually delete anything O.o
@router.patch("/me", response_model=schemas.User)
async def patch_me(
    obj: schemas.UserUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    not_modified = True
    for k, v in obj.model_dump(exclude_unset=True).items():
        if v != getattr(user, k):
            not_modified = False
            setattr(user, k, v)
    if not_modified:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No modifications made to creator.",
        )
    else:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@router.get("/me", response_model=schemas.User)
async def get_me(user: Annotated[models.User, Depends(deps.get_current_active_user)]):
    return user


@router.get(
    "/{id}", response_model=schemas.Creator, dependencies=[Depends(deps.get_superuser)]
)
async def get_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if user := await db.get(models.User, id):
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User ({id}) does not exist."
    )


@router.patch(
    "/{user_id}",
    response_model=schemas.Creator,
    dependencies=[Depends(deps.get_superuser)],
)
async def patch_user_as_superuser(
    obj: schemas.CreatorPatch,
    user_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if not (user_db := await db.get(models.User, user_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    not_modified = True
    for k, v in obj.model_dump(exclude_unset=True).items():
        if v != getattr(user_db, k):
            not_modified = False
            setattr(user_db, k, v)
    if not_modified:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No modifications made to user.",
        )
    else:
        db.add(user_db)
        await db.commit()
        await db.refresh(user_db)
        return user_db


@router.delete(
    "/{id}",
    dependencies=[Depends(deps.get_superuser)],
)
async def delete_by_id(
    id: str,
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if user := await db.get(models.User, id):
        await db.delete(user)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"User ({id}) does not exist."
    )

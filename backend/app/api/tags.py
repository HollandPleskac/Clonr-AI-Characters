from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth.users import get_superuser
from app.db import get_async_session

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)


# See the doc suggestion output schema for what would be returned
@router.post(
    "/create", response_model=schemas.Tag, dependencies=[Depends(get_superuser)]
)
async def create_tag(
    tag_create: schemas.TagCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if (await db.get(models.Tag, tag_create.name)) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag {tag_create.name} already exists",
        )
    tag = models.Tag(**tag_create.dict(exclude_unset=True))
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.get("/{name}", response_model=schemas.Tag)
async def check_tag(
    name: Annotated[str, Path()],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if tag := await db.get(models.Tag, name):
        return tag
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {name} does not exist"
    )


@router.get("/", response_model=list[schemas.Tag])
async def get_tags(
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await db.scalars(sa.select(models.Tag).order_by(models.Tag.name))

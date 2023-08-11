import json
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.deps import get_async_redis, get_async_session, get_superuser

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)


# See the doc suggestion output schema for what would be returned
@router.post("/", response_model=schemas.Tag, dependencies=[Depends(get_superuser)])
async def create_tag(
    tag_create: schemas.TagCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if await db.scalar(
        sa.select(models.Tag.name).where(models.Tag.name == tag_create.name)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag {tag_create.name} already exists",
        )
    tag = models.Tag(**tag_create.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.get("/", response_model=list[schemas.Tag])
async def get_tags(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    conn: Annotated[Redis, Depends(get_async_redis)],
):
    if tag_bytes := await conn.get("tags"):
        tags = json.loads(tag_bytes.decode("utf-8"))
        return tags
    r = await db.scalars(sa.select(models.Tag).order_by(models.Tag.name))
    tags = r.all()
    tag_bytes = json.dumps(jsonable_encoder(tags)).encode()
    ex = 60  # recompute every minute
    await conn.set("tags", tag_bytes, ex=ex)
    return tags


@router.get("/{name}", response_model=schemas.Tag)
async def check_tag_by_name(
    name: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if tag := await db.scalar(sa.select(models.Tag).where(models.Tag.name == name)):
        return tag
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {name} does not exist"
    )


# See the doc suggestion output schema for what would be returned
@router.delete(
    "/{tag_id}", response_class=Response, dependencies=[Depends(get_superuser)]
)
async def delete_tag(
    tag_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if not (tag := await db.get(models.Tag, tag_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} does not exist",
        )
    await db.delete(tag)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{tag_id}", response_model=schemas.Tag, dependencies=[Depends(get_superuser)]
)
async def patch_tag(
    tag_update: schemas.TagUpdate,
    tag_id: Annotated[uuid.UUID, Path()],
    db: Annotated[AsyncSession, Depends(get_async_session)],
):
    if not (tag := await db.get(models.Tag, tag_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} does not exist",
        )
    for k, v in tag_update.model_dump(exclude_unset=True).items():
        setattr(tag, k, v)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag

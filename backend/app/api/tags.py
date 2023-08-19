import json
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from fastapi.encoders import jsonable_encoder
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={404: {"description": "Not found"}},
)


# See the doc suggestion output schema for what would be returned
@router.post(
    "/",
    response_model=schemas.Tag,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.get_superuser)],
)
async def create_tag(
    tag_create: schemas.TagCreate,
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
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
    await conn.delete("tags")  # Cache invalidation. Super important!
    await db.commit()
    await db.refresh(tag)
    logger.info(f"Created tag {tag}")
    return tag


@router.get("/", response_model=list[schemas.Tag])
async def get_tags(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
):
    if tag_bytes := await conn.get("tags"):
        tags = json.loads(tag_bytes.decode("utf-8"))
        return tags
    r = await db.scalars(sa.select(models.Tag).order_by(models.Tag.name))
    tags = r.all()
    tag_bytes = json.dumps(jsonable_encoder(tags)).encode()
    ex = 60 * 60 * 24  # recompute every day just in case?
    await conn.set("tags", tag_bytes, ex=ex)
    return tags


@router.get("/{tag_id}", response_model=schemas.Tag)
async def get_tag_by_id(
    tag_id: Annotated[int, Path()],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if tag := await db.scalar(sa.select(models.Tag).where(models.Tag.id == tag_id)):
        return tag
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag {tag_id} does not exist"
    )


# See the doc suggestion output schema for what would be returned
@router.delete(
    "/{tag_id}", response_class=Response, dependencies=[Depends(deps.get_superuser)]
)
async def delete_tag(
    tag_id: Annotated[int, Path()],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if not (tag := await db.get(models.Tag, tag_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} does not exist",
        )
    await conn.delete("tags")  # Cache invalidation. Super important!
    await db.delete(tag)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{tag_id}", response_model=schemas.Tag, dependencies=[Depends(deps.get_superuser)]
)
async def patch_tag(
    tag_update: schemas.TagUpdate,
    tag_id: Annotated[int, Path()],
    conn: Annotated[Redis, Depends(deps.get_async_redis)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if not (tag := await db.get(models.Tag, tag_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} does not exist",
        )
    for k, v in tag_update.model_dump(exclude_unset=True).items():
        setattr(tag, k, v)
    db.add(tag)
    await conn.delete("tags")  # Cache invalidation. Super important!
    await db.commit()
    await db.refresh(tag)
    return tag

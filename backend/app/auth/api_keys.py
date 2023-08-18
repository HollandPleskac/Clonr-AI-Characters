# type: ignore
# (Jonny): V2 feature, not currently used.
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.security.api_key import APIKeyHeader
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.utils import sha256_hash

api_key_header = APIKeyHeader(name="CLONR_API_KEY", auto_error=False)


# FixMe (Jonny): this entire function is out of date
async def get_api_key(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    cache: Annotated[Redis, Depends(deps.get_async_redis)],
    api_key_header: Annotated[str, Security(api_key_header)],
) -> schemas.APIKey:
    hashed_key = sha256_hash(api_key_header)
    if key := await cache.get(hashed_key):
        return key
    promise = await db.scalars(
        select(models.APIKey).where(models.APIKey.hashed_key == api_key_header)
    )
    if (key_model := promise.first()) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return schemas.APIKey(**jsonable_encoder(key_model))

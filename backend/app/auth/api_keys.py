import json
from typing import Annotated, Optional

from app import models, schemas
from app.db import APIKeyCache, get_async_apikey_cache, get_async_session
from fastapi import Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

api_key_header = APIKeyHeader(name="CLONR_API_KEY", auto_error=False)


async def get_api_key(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    cache: Annotated[APIKeyCache, Depends(get_async_apikey_cache)],
    api_key_header: Annotated[str, Security(api_key_header)],
) -> schemas.APIKey:
    key = await cache.get(api_key_header)
    if key:
        return key
    promise = await db.scalars(
        select(models.APIKey.id).where(models.APIKey.key == api_key_header)
    )
    if (key_model := promise.first()) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return schemas.APIKey(**jsonable_encoder(key_model))

from typing import Annotated, List

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.auth.users import current_active_creator, current_active_user
from app.db import get_async_session

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


# See the doc suggestion output schema for what would be returned
@router.get("/suggest", response_model=list[schemas.DocumentSuggestion])
async def create_document(
    clone_name: Annotated[str, Query(max_length=64)],
):
    # TODO (Jonny): implement this to automatically search wikipedia and fandom, plus others?
    # we can get an image preview using the meta property if it exists. As an example
    # <meta property="og:image" content="https://static.wikia.nocookie.net/chainsaw-man/images/
    # d/d9/Makima_anime_design_2.png/revision/latest?cb=20220919121118"/>
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Clone suggestion is currently unavailable.",
    )

import uuid
from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth.users import UserManager, auth_backend

from .db import get_async_session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, models.User, models.OAuthAccount)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[models.User, uuid.UUID](get_user_manager, [auth_backend])

get_current_active_user = fastapi_users.current_user(active=True)

get_optional_current_active_user = fastapi_users.current_user(
    active=True, optional=True
)

get_superuser = fastapi_users.current_user(active=True, superuser=True)


async def get_current_active_creator(
    user: Annotated[models.User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> models.Creator:
    if (creator := await db.get(models.Creator, user.id)).is_active:
        return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current user is not signed up as a creator or is not active.",
    )


async def get_paying_user(
    user: Annotated[models.User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> bool:
    if user.is_subscribed:
        return user
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current user is not subscribed to a payment plan.",
    )


async def get_free_limit_user(
    user: Annotated[models.User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
    max_free_messages: int = 10,
) -> models.User:
    if user.is_subscribed or user.num_free_messages_sent <= max_free_messages:
        return user
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail="Free trial exceeded, please subscribe to continue.",
    )

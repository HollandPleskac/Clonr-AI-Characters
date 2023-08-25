import uuid
from typing import Annotated

from fastapi import Cookie, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth.users import AUTH_KEY_PREFIX, UserManager, auth_backend
from app.settings import settings

from .db import get_async_redis, get_async_session


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
    if creator := await db.get(models.Creator, user.id):
        if creator.is_active:
            return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current user is not signed up as a creator or is not active.",
    )


async def get_free_or_paying_user(
    user: Annotated[models.User, Depends(get_current_active_user)],
) -> models.User:
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
            detail="User is currently banned. Please contact support for more information.",
        )
    subs = user.subscriptions
    if all(s.stripe_status != "active" for s in subs):
        if user.num_free_messages_sent >= settings.NUM_FREE_MESSAGES:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="The number of free messages has been reached. Please subscribe to continue.",
            )
    return user


async def get_user_id_from_cookie(
    conn: Annotated[Redis, Depends(get_async_redis)],
    clonr_auth: Annotated[str | None, Cookie(regex=r"[a-zA-Z0-9_\-]")],
):
    if clonr_auth and (user_id := await conn.get(f"{AUTH_KEY_PREFIX}{clonr_auth}")):
        return user_id.decode("utf-8")

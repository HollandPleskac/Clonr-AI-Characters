import uuid
from typing import Annotated, Optional

import redis.asyncio

# import redis.asyncio
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
    RedisStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app import models
from app.db import get_async_redis_cache, get_async_session, get_user_db
from app.models import User
from app.settings import settings

SECRET = settings.AUTH_SECRET

redis = redis.asyncio.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)

google_oauth_client = GoogleOAuth2(
    settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered. Request: {request}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )

    async def ban_user(self, db: Session, user_id: uuid.UUID):
        user = db.query(User).filter(User.id == user_id).first()
        user.is_banned = True
        db.commit()
        async with get_async_redis_cache() as cache:
            await cache.ban_user(user_id)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
optional_current_active_user = fastapi_users.current_user(active=True, optional=True)
get_superuser = fastapi_users.current_user(active=True, superuser=True)


async def current_active_creator(
    user: Annotated[models.User, Depends(current_active_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> models.Creator:
    if (creator := await db.get(models.Creator, user.id)).is_active:
        return creator
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Current user is not signed up as a creator or is not active.",
    )

import uuid
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
    RedisStrategy,
)
from httpx_oauth.clients.discord import DiscordOAuth2
from httpx_oauth.clients.facebook import FacebookOAuth2
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.reddit import RedditOAuth2
from loguru import logger
from redis.asyncio import Redis

from app.models import User
from app.settings import settings

SECRET = settings.AUTH_SECRET
AUTH_KEY_PREFIX = "user_auth_token:"
COOKIE_NAME = "clonrauth"

# Redundant with app.db.cache.
redis: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)

# TODO (Jonny): yo why this shit not working?
google_oauth_client = GoogleOAuth2(
    settings.GOOGLE_CLIENT_ID,
    settings.GOOGLE_CLIENT_SECRET,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)

facebook_oauth_client = FacebookOAuth2(
    settings.FACEBOOK_CLIENT_ID, settings.FACEBOOK_CLIENT_SECRET
)

reddit_oauth_client = RedditOAuth2(
    settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET
)

discord_oauth_client = DiscordOAuth2(
    settings.DISCORD_CLIENT_ID, settings.DISCORD_CLIENT_SECRET
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} has registered")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600, cookie_name=COOKIE_NAME)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600, key_prefix=AUTH_KEY_PREFIX)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)

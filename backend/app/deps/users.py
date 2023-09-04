import json
import os
import time
import uuid
import warnings
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Annotated, Any, Set

import sqlalchemy as sa
from cryptography.hazmat.primitives import hashes
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from jose import jwe
from jose.exceptions import JWEError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.auth.csrf import check_csrf_cookie, check_csrf_cookie_from_request
from app.auth.jwt import check_expiry, encrypt_secret_key
from app.schemas import Plan
from app.settings import settings

from .db import get_async_session


@dataclass
class UserAndPlan:
    plan: str
    user: models.User


def extract_token_from_cookie(cookies: dict[str, str], cookie_name: str) -> str | None:
    """
    Extracts a potentially chunked token from the cookies of a request.
    It may be in a single cookie, or chunked (with suffixes 0...n)
    :param req: The request to extract the token from
    :return: The encrypted nextauth session token
    """
    encrypted_token = ""

    # Do we have a session cookie with the expected name?
    if cookie_name in cookies:
        encrypted_token = cookies[cookie_name]

    # Or maybe a chunked session cookie?
    elif f"{cookie_name}.0" in cookies:
        counter = 0
        while f"{cookie_name}.{counter}" in cookies:
            encrypted_token += cookies[f"{cookie_name}.{counter}"]
            counter += 1

    # Or no cookie at all
    else:
        return None

    return encrypted_token


# Not currently used, as we are using session side cookies. What's annoying, is that
# nextjs could do multi-key cookies, like part.0, part.1, ..., part.N, so we can't use
# the built-in Cookie extraction, we have to use this extract function.
# Also todo here is find the correct pydantic output model for the token. it's not a string...
class NextAuthJWT:
    def __init__(
        self,
        secret: str | None = None,
        cookie_name: str | None = None,
        secure_cookie: bool | None = None,
        csrf_cookie_name: str | None = None,
        csrf_header_name: str | None = "X-XSRF-Token",
        info: bytes = b"NextAuth.js Generated Encryption Key",
        salt: bytes = b"",
        hash_algorithm: Any = hashes.SHA256(),
        csrf_prevention_enabled: bool | None = None,
        csrf_methods: Set[str] | None = None,
        check_expiry: bool | None = True,
    ):
        self.secret = secret
        if self.secret is None:
            self.secret = settings.NEXTAUTH_SECRET

        self.secure_cookie = secure_cookie
        if secure_cookie is None:
            if (nextauth_url := os.getenv("NEXTAUTH_URL", "")) is None:
                warnings.warn("NEXTAUTH_URL not set", RuntimeWarning)
            self.secure_cookie = nextauth_url.startswith("https://")

        self.cookie_name = cookie_name
        if self.cookie_name is None:
            self.cookie_name = (
                "__Secure-next-auth.session-token"
                if self.secure_cookie
                else "next-auth.session-token"
            )

        self.csrf_cookie_name = csrf_cookie_name
        if self.csrf_cookie_name is None:
            self.csrf_cookie_name = (
                "__Host-next-auth.csrf-token"
                if self.secure_cookie
                else "next-auth.csrf-token"
            )

        self.csrf_header_name = csrf_header_name

        self.key = encrypt_secret_key(
            secret=self.secret,
            length=32,
            salt=salt,
            algorithm=hash_algorithm,
            context=info,
        )

        self.csrf_prevention_enabled = csrf_prevention_enabled
        if self.csrf_prevention_enabled is None:
            self.csrf_prevention_enabled = not settings.DEV

        self.csrf_methods = csrf_methods
        if self.csrf_methods is None:
            self.csrf_methods = {"POST", "PUT", "PATCH", "DELETE"}

        self.check_expiry = check_expiry

    def __call__(self, req: Request):
        assert self.cookie_name is not None
        assert self.csrf_cookie_name is not None
        assert self.csrf_header_name is not None

        encrypted_token = extract_token_from_cookie(req.cookies, self.cookie_name)

        if encrypted_token is None:
            return None

        if self.csrf_prevention_enabled:
            check_csrf_cookie_from_request(
                req, self.csrf_cookie_name, self.csrf_header_name
            )

        try:
            decrypted_token_string = jwe.decrypt(encrypted_token, self.key)
            token = json.loads(decrypted_token_string)
        except (JWEError, JSONDecodeError) as e:
            print(e)
            raise HTTPException(status_code=401, detail="Invalid JWT format")

        if self.check_expiry:
            if "exp" not in token:
                raise HTTPException(
                    status_code=401, detail="Invalid JWT format, missing exp"
                )
            check_expiry(token["exp"])

        return token


async def next_auth_cookie(
    session_id: Annotated[str | None, Cookie(alias="next-auth.session-token")] = None,
    secure_session_id: Annotated[
        str | None, Cookie(alias="__Secure-next-auth.session-token")
    ] = None,
    csrf_cookie: Annotated[str | None, Cookie(alias="next-auth.csrf-token")] = None,
    secure_csrf_cookie: Annotated[
        str | None, Cookie(alias="__Host-next-auth.csrf-token")
    ] = None,
    csrf_header_token: Annotated[str | None, Header(alias="X-XSRF-Token")] = None,
) -> str | None:
    csrf_prevention_enabled: bool = not settings.DEV

    if settings.NEXTAUTH_URL.startswith("https://"):
        csrf_cookie = secure_csrf_cookie
        session_id = secure_session_id

    if session_id is None:
        return None

    if csrf_prevention_enabled:
        check_csrf_cookie(
            cookie=csrf_cookie,
            header_token=csrf_header_token,
        )

    return session_id


async def get_optional_current_active_user(
    token: Annotated[str | None, Depends(next_auth_cookie)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> models.User | None:
    if token is None:
        return None
    user = await db.scalar(
        sa.select(models.User)
        .join(models.Session, models.Session.user_id == models.User.id)
        .where(models.Session.session_token == token)
    )
    if user is None:
        return None
    return user


async def get_current_active_user(
    token: Annotated[str | None, Depends(next_auth_cookie)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> models.User:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization session token missing",
        )
    user = await db.scalar(
        sa.select(models.User)
        .join(models.Session, models.Session.user_id == models.User.id)
        .where(models.Session.session_token == token)
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is banned"
        )
    return user


async def get_superuser(user: Annotated[models.User, Depends(get_current_active_user)]):
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


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
) -> UserAndPlan:
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
            detail="User is currently banned. Please contact support for more information.",
        )
    if settings.DEV:
        return UserAndPlan(user=user, plan=Plan.plus)
    # TODO (Jonny): make sure we have only one plan active at a time?
    # TODO (Jonny): need to pass the plan type (basic, plus) through here as well somehow
    # TODO (Jonny): need to check to make sure that the current time < plan.subscribe time
    subs = user.subscriptions
    # if you haven't subscribed yet, check if you have remaining free messages
    if not subs:
        if user.num_free_messages_sent < settings.NUM_FREE_MESSAGES:
            return UserAndPlan(plan=Plan.free, user=user)
        else:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="The number of free messages has been reached. Please subscribe to continue.",
            )
    sub = subs[0]  # TODO make sure that this is always consistent in the future
    # if you have a subscription, check that you are within the billing period
    if time.time() > sub.stripe_current_period_end:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription has expired. Please renew to continue.",
        )
    if not sub.stripe_status == "active":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription payment has not yet been successfully completed. Please check the billing page.",
        )
    plan = Plan.plus if "plus" in sub.stripe_price_lookup_key else Plan.basic
    return UserAndPlan(user=user, plan=plan)


# deprecated. no longer using redis for storing auth session unfortunately :(. Come back to this later
async def get_user_id_from_cookie(
    user: Annotated[models.User, Depends(get_current_active_user)],
) -> uuid.UUID:
    return user.id

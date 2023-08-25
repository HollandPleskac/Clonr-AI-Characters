import time
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.settings import settings


class StripeCheckoutToken(BaseModel):
    user_id: uuid.UUID
    exp: int | None = None


class StripeCheckoutTokenResponse(BaseModel):
    token: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_stripe_checkout_token(
    user_id: uuid.UUID, expire_seconds: int | None = None
) -> str:
    data = {"user_id": str(user_id)}
    if expire_seconds:
        data["exp"] = datetime.utcnow() + timedelta(seconds=expire_seconds)
    encoded_jwt = jwt.encode(
        data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    # Stripe won't let us use periods. for 38 possible chars, the odds
    # of this naturally occurring are 1 / 10^21
    return encoded_jwt.replace(".", "-------------")


def decode_stripe_checkout_token(token: str) -> StripeCheckoutToken:
    try:
        payload = jwt.decode(
            token.replace("-------------", "."),
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if not payload.get("user_id"):
            from loguru import logger

            logger.error(f"Stripe decode error. Token: {token}. payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        res = StripeCheckoutToken(**payload)
        if res.exp and res.exp < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        return res
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
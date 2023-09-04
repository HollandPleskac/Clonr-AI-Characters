import secrets
import urllib.parse
from pydantic import BaseModel
from cryptography.hazmat.primitives import hashes
from fastapi import HTTPException, Request
from loguru import logger

from app.settings import settings


class CsrfCookie(BaseModel):
    token: str
    hash: str

    @classmethod
    def from_url_cookie(cls, cookie: str):
        unquoted_cookie = urllib.parse.unquote(cookie)  # converts %7 and shit to |
        if "|" not in unquoted_cookie:
            logger.error(f"Unrecognized CSRF cookie format: {unquoted_cookie}")
            raise HTTPException(
                status_code=401, detail="Unrecognized CSRF cookie format"
            )
        token, hash = unquoted_cookie.split("|")
        return cls(token=token, hash=hash)

    def to_str(self):
        return f"{self.token}|{self.hash}"


def generate_csrf_cookie(
    csrf_token: str | None = None, secret: str | None = None
) -> str:
    if csrf_token is None:
        csrf_token = secrets.token_bytes(32).hex()
    csrf_token_bytes = bytes(csrf_token, "ascii")
    secret_bytes = bytes(secret or settings.NEXTAUTH_SECRET, "ascii")
    hasher = hashes.Hash(hashes.SHA256())
    hasher.update(csrf_token_bytes)
    hasher.update(secret_bytes)
    token_hash = hasher.finalize().hex()
    cookie = f"{csrf_token}|{token_hash}"
    return cookie


def check_csrf_cookie(
    cookie: str | None, header_token: str | None = None, secret: str | None = None
) -> None:
    """csrf_header_token is just the same cookie you pass in arg 1 (i.e. the first part before "|").
    Apparently cross-site forgery request cannot send headers or something, so that's why this thing is needed,
    it doesn't actually matter what's in the header."""
    if cookie is None:
        raise HTTPException(status_code=401, detail="Missing CSRF cookie")

    # extract the token and hash
    cookie_obj = CsrfCookie.from_url_cookie(cookie=cookie)

    token_bytes = bytes(cookie_obj.token, "ascii")
    secret_bytes = bytes(secret or settings.NEXTAUTH_SECRET, "ascii")

    # Compute the expected hash
    # See https://github.com/nextauthjs/next-auth/blob/50fe115df6379fffe3f24408a1c8271284af660b
    # /src/core/lib/csrf-token.ts
    # for info on how the CSRF cookie is created
    hasher = hashes.Hash(hashes.SHA256())
    hasher.update(token_bytes)
    hasher.update(secret_bytes)
    actual_hash = hasher.finalize().hex()

    if cookie_obj.hash != actual_hash:
        raise HTTPException(status_code=401, detail="CSRF hash mismatch")

    # These only works when you know the request is going to send an X-XSRF header
    if not settings.DEV and header_token is None:
        raise HTTPException(status_code=401, detail="Missing CSRF header")

    # Check if the CSRF token in the headers matches the one in the cookie
    if not settings.DEV and cookie_obj.token != header_token:
        raise HTTPException(status_code=401, detail="CSRF Token mismatch")


def check_csrf_cookie_from_request(
    req: Request,
    csrf_cookie_name: str,
    csrf_header_name: str,
    csrf_methods: list[str] | None = None,
    secret: str | None = None,
):
    if req.method not in (csrf_methods or ["POST", "GET", "PUT", "PATCH", "DELETE"]):
        return

    if csrf_cookie_name not in req.cookies:
        raise HTTPException(
            status_code=401, detail=f"Missing CSRF token: {csrf_cookie_name}"
        )
    if csrf_header_name not in req.headers:
        raise HTTPException(
            status_code=401, detail=f"Missing CSRF header: {csrf_header_name}"
        )

    cookie = req.cookies[csrf_cookie_name]
    header_token = req.headers[csrf_header_name]

    check_csrf_cookie(cookie=cookie, header_token=header_token, secret=secret)

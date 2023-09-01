import secrets
import urllib.parse

from cryptography.hazmat.primitives import hashes
from fastapi import HTTPException, Request
from loguru import logger

from app.settings import settings


def extract_csrf_info(csrf_string: str) -> [str, str]:
    csrf_token_unquoted = urllib.parse.unquote(csrf_string)  # converts %7 and shit to |

    if "|" not in csrf_token_unquoted:
        logger.info(csrf_string)
        logger.info(csrf_token_unquoted)
        raise HTTPException(status_code=401, detail="Unrecognized CSRF token format")

    csrf_cookie_token, csrf_cookie_hash = csrf_token_unquoted.split("|")

    return csrf_cookie_token, csrf_cookie_hash


def validate_csrf_info(secret: str, csrf_token: str, expected_hash: str):
    csrf_token_bytes = bytes(csrf_token, "ascii")
    secret_bytes = bytes(secret, "ascii")

    hasher = hashes.Hash(hashes.SHA256())
    hasher.update(csrf_token_bytes)
    hasher.update(secret_bytes)
    actual_hash = hasher.finalize().hex()

    if expected_hash != actual_hash:
        raise HTTPException(status_code=401, detail="CSRF hash mismatch")


def generate_random_csrf_cookie():
    csrf_token = secrets.token_bytes(32).hex()
    hasher = hashes.Hash(hashes.SHA256)
    hasher.update(csrf_token)
    hasher.update(bytes(settings.NEXTAUTH_SECRET, "ascii"))
    token_hash = hasher.finalize().hex()
    cookie = f"{csrf_token}|{token_hash}"
    return cookie


def check_csrf_token(
    csrf_token: str | None,
    csrf_header_token: str | None,
):
    if csrf_token is None:
        raise HTTPException(status_code=401, detail="Missing CSRF token")

    csrf_cookie_token, csrf_cookie_hash = extract_csrf_info(csrf_token)

    # Validate if it was indeed set by the server
    # See https://github.com/nextauthjs/next-auth/blob/50fe115df6379fffe3f24408a1c8271284af660b/src/core/lib/csrf-token.ts
    # for info on how the CSRF cookie is created
    validate_csrf_info(settings.NEXTAUTH_SECRET, csrf_cookie_token, csrf_cookie_hash)

    # These only work when you know the request is going to send an X-XSRF header
    # if csrf_header_token is None:
    #     raise HTTPException(status_code=401, detail="Missing CSRF header")

    # if csrf_header_token != csrf_cookie_token:
    #     raise HTTPException(status_code=401, detail="CSRF Token mismatch")


def check_csrf_token_from_request(
    req: Request,
    csrf_cookie_name: str,
    csrf_header_name: str,
    csrf_methods: list[str] | None = None,
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

    csrf_cookie_token, csrf_cookie_hash = extract_csrf_info(
        req.cookies[csrf_cookie_name]
    )

    validate_csrf_info(settings.NEXTAUTH_SECRET, csrf_cookie_token, csrf_cookie_hash)

    # Check if the CSRF token in the headers matches the one in the cookie
    csrf_header_token = req.headers[csrf_header_name]

    if csrf_header_token != csrf_cookie_token:
        raise HTTPException(status_code=401, detail="CSRF Token mismatch")

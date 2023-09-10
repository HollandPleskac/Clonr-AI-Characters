import secrets

import pytest
from fastapi.exceptions import HTTPException

from app.auth.csrf import CsrfCookie, check_csrf_cookie, generate_csrf_cookie


def test_generate():
    # test generating when passing token
    token = "MYTOKEN"
    cookie = generate_csrf_cookie(csrf_token=token)
    assert len(cookie) == 64 + 1 + len(token), len(cookie)
    assert token == CsrfCookie.from_url_cookie(cookie).token

    # test that we do the random byte shit
    cookie = generate_csrf_cookie()
    assert len(cookie) == 2 * 64 + 1, len(cookie)


def test_csrf_generation_is_ok():
    token = secrets.token_bytes(32).hex()
    cookie = generate_csrf_cookie(token)
    check_csrf_cookie(cookie=cookie)

    cookie2 = generate_csrf_cookie(token, secret="RANDOM_OTHER_SECRET")
    with pytest.raises(HTTPException):
        check_csrf_cookie(cookie=cookie2)

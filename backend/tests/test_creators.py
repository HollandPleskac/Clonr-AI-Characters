import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models
from tests.types import LoginData


def test_creators(
    client: TestClient, creator_headers: dict[str, str], creator_data: LoginData
):
    # get user info
    r = client.get("/users/me", headers=creator_headers)
    assert r.status_code == 200, r.json()
    user_id = r.json()["id"]

    # get creator info
    r = client.get("/creators/me", headers=creator_headers)
    data = r.json()
    assert r.status_code == 200, r.json()
    assert data["user_id"] == user_id

    # test no modification
    r = client.patch("/creators/me", json=dict(is_active=True), headers=creator_headers)
    assert r.status_code == 304, r.json()

    # test changing to inactive
    r = client.patch(
        "/creators/me", json=dict(is_active=False), headers=creator_headers
    )
    assert r.status_code == 200, r.json()

    # test creator is inactive
    r = client.get("/creators/me", headers=creator_headers)
    assert r.status_code == 400, r.json()

    # change back to active so we can do shit
    r = client.patch("/creators/me", json=dict(is_active=True), headers=creator_headers)
    assert r.status_code == 200, r.json()

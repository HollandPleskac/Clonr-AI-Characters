import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import schemas
from app.main import app as main_app
from tests.types import LoginData


@pytest.fixture(name="db", scope="session")
def db_fixture():
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)
    with SessionLocal() as session:
        yield session


@pytest.fixture(name="client", scope="session")
def client_fixture():
    with TestClient(app=main_app) as client:
        yield client


@pytest.fixture(scope="session")
def user_data() -> LoginData:
    return LoginData(email="user@example.com", password="password")


@pytest.fixture(scope="session")
def creator_data() -> LoginData:
    return LoginData(email="creator@example.com", password="password")


@pytest.fixture(name="user_headers", scope="session")
def user_headers(client: TestClient, user_data: LoginData) -> dict[str, str]:
    input_data = {
        **user_data.dict(),
        "is_active": False,
        "is_superuser": True,
        "is_verified": True,
    }

    # Register user
    r = client.post("/auth/register", json=input_data)
    assert r.status_code == 201, r.json()
    data = r.json()
    assert data["is_active"], data
    assert not data["is_superuser"], data
    assert not data["is_verified"], data

    # Login user
    r = client.post(
        "/auth/cookies/login",
        data=dict(username=user_data.email, password=user_data.password),
    )
    assert r.status_code == 204, r.json()
    assert r.cookies
    # idk I just hacked this because fuck, this is annoying
    headers = {
        "Cookie": "; ".join(
            [f"{name}={value}" for name, value in client.cookies.items()][-1:]
        )
    }

    yield headers

    # get user info
    r = client.get("/users/me", headers=headers)
    data = r.json()
    assert r.status_code == 200, r.json()
    assert data["email"] == input_data["email"]

    # Logout user
    r = client.post("/auth/cookies/logout", json={}, headers=headers)
    assert r.status_code == 204, r.json()
    assert not r.cookies


@pytest.fixture(name="creator_headers", scope="session")
def creator_headers(
    client: TestClient, creator_data: LoginData, db: Session
) -> dict[str, str]:
    # Register user
    r = client.post("/auth/register", json=creator_data.dict())
    assert r.status_code == 201, r.status_code

    print(client.cookies)
    # Login user
    r = client.post(
        "/auth/cookies/login",
        data=dict(username=creator_data.email, password=creator_data.password),
    )
    assert r.status_code == 204, r.json()
    headers = {"Cookie": r.headers["set-cookie"].split(";")[0]}

    # Upgrade to Creator
    r = client.post(
        "/creators/upgrade", headers=headers, json={"username": "cool-creator-20"}
    )
    assert r.status_code == 201, r.json()

    yield headers

    # Logout user
    r = client.post("/auth/cookies/logout", json={}, headers=headers)
    assert r.status_code == 204, r.json()
    assert not r.cookies


# @pytest.fixture
# def makima_create(
#     client: TestClient, creator_headers: dict[str, str]
# ):
#     p = Path(__file__).parent / "makima.json"
#     with open(p, 'r') as f:
#         payload = schemas.CloneCreate(
#             **json.load(f),
#             is_public=True,
#             # tags=['anime']
#         )

#     r = client.post("/clones/create", headers=creator_headers, json=payload.dict(exclude_none=True))
#     data = r.json()
#     id = str(data["id"])
#     assert r.status_code == 201, data
#     assert data["greeting_message"] is None

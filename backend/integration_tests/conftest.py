import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import schemas
from app.main import app as main_app


class LoginData(BaseModel):
    email: str
    password: str


@pytest.fixture(scope="session")
def superuser_headers():
    return {"Cookie": "next-auth.session-token=SUPERUSER_TOKEN"}


@pytest.fixture(scope="session")
def user_headers():
    return {"Cookie": "next-auth.session-token=NORMAL_USER_TOKEN"}


@pytest.fixture(name="creator_headers", scope="session")
def creator_headers() -> dict[str, str]:
    return {"Cookie": "next-auth.session-token=CREATOR_USER_TOKEN"}


def load_makima_create() -> dict:
    path = Path(__file__).parent / "makima.json"
    with open(path, "r") as f:
        return json.load(f)


@pytest.fixture(name="db", scope="session")
def db_fixture():
    host = os.environ["POSTGRES_HOST"]
    DATABASE_URL = f"postgresql://postgres:postgres@{host}:5432/postgres"
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


# @pytest.fixture(name="user_headers", scope="session")
# def user_headers(superuser_headers) -> dict[str, str]:
#     return superuser_headers
# input_data = {
#     **user_data.model_dump(),
#     "is_active": False,
#     "is_superuser": True,
#     "is_verified": True,
# }

# # Register user
# r = client.post("/auth/register", json=input_data)
# assert r.status_code == 201, r.json()
# data = r.json()
# assert data["is_active"], data
# assert not data["is_superuser"], data
# assert not data["is_verified"], data

# # Login user
# r = client.post(
#     "/auth/cookies/login",
#     data=dict(username=user_data.email, password=user_data.password),
# )
# assert r.status_code == 204, r.json()
# assert r.cookies
# # idk I just hacked this because fuck, this is annoying
# headers = {
#     "Cookie": "; ".join(
#         [f"{name}={value}" for name, value in client.cookies.items()][-1:]
#     )
# }

# yield headers

# # get user info
# r = client.get("/users/me", headers=headers)
# data = r.json()
# assert r.status_code == 200, r.json()
# assert data["email"] == input_data["email"]

# # Logout user
# r = client.post("/auth/cookies/logout", json={}, headers=headers)
# assert r.status_code == 204, r.json()
# assert not r.cookies


# @pytest.fixture(name="creator_headers", scope="session")
# def creator_headers(superuser_headers) -> dict[str, str]:
#     return superuser_headers
# # Register user
# r = client.post(
#     "/auth/register",
#     json=creator_data.model_dump(),
# )
# assert r.status_code == 201, r.status_code

# print(client.cookies)
# # Login user
# r = client.post(
#     "/auth/cookies/login",
#     data=dict(username=creator_data.email, password=creator_data.password),
# )
# assert r.status_code == 204, r.json()
# headers = {"Cookie": r.headers["set-cookie"].split(";")[0]}

# # Upgrade to Creator
# r = client.post(
#     "/creators/upgrade", headers=headers, json={"username": "cool-creator-20"}
# )
# assert r.status_code == 201, r.json()

# yield headers

# # Logout user
# r = client.post("/auth/cookies/logout", json={}, headers=headers)
# assert r.status_code == 204, r.json()
# assert not r.cookies


@pytest.fixture(name="makima", scope="session")
def makima_fixture(client: TestClient, creator_headers: dict[str, str], db: Session):
    # Create a basic clone
    name = "Makima"
    short_description = "Makima is the leader of the Public Safety Devil Hunter organization, and also the Control Devil."
    greeting_message = "Hmm... you seem interesting"
    inp = schemas.CloneCreate(
        name=name,
        short_description=short_description,
        is_public=True,
        greeting_message=greeting_message,
    )
    data = inp.model_dump()
    r = client.post("/clones/", headers=creator_headers, json=data)
    data = r.json()
    clone_id = str(data["id"])
    assert r.status_code == 201, data

    yield creator_headers, clone_id


# @pytest.fixture(name="superuser_headers", scope="session")
# def superuser_headers(client: TestClient) -> dict[str, str]:
#     # Login user
#     r = client.post(
#         "/auth/cookies/login",
#         data=dict(
#             username=settings.SUPERUSER_EMAIL, password=settings.SUPERUSER_PASSWORD
#         ),
#     )
#     assert r.status_code == 204, r.json()
#     assert r.cookies
#     # idk I just hacked this because fuck, this is annoying
#     headers = {
#         "Cookie": "; ".join(
#             [f"{name}={value}" for name, value in client.cookies.items()][-1:]
#         )
#     }

#     yield headers

#     # Logout user
#     r = client.post("/auth/cookies/logout", json={}, headers=headers)
#     assert r.status_code == 204, r.json()
#     assert not r.cookies


@pytest.fixture(name="makima_id", scope="session")
def makima_clone_fixture(
    client: TestClient,
    creator_headers: dict[str, str],
    user_headers: dict[str, str],
    db: Session,
) -> str:
    # Create the Makima clone. It has a tag field, but for testing, no tags exist yet
    clone_data = load_makima_create()
    clone_create = schemas.CloneCreate(**clone_data, is_public=True, tags=[])
    clone_create.greeting_message = "Jonny-kun, have you been a good dog?"
    r = client.post(
        "/clones/",
        headers=creator_headers,
        json=clone_create.model_dump(exclude_unset=True, exclude={"tags"}),
    )
    data = r.json()
    clone_id = str(data["id"])
    assert r.status_code == 201, data

    # add document
    path = Path(__file__).parent / "makima-document.txt"
    with open(path, "r") as f:
        doc_create = schemas.DocumentCreate(
            content=f.read(),
            name="Makima wiki",
            description="fandom homepage",
            type="wiki",
            url="https://nickelback.the.one.true.god.com",
        ).model_dump()
    r = client.post(
        f"/clones/{clone_id}/documents", json=doc_create, headers=creator_headers
    )
    data = r.json()
    assert r.status_code == 201, data

    # add monologues
    monologues = []
    for m in clone_data["monologues"]:
        m_create = schemas.MonologueCreate(
            content=m,
        ).model_dump()
        monologues.append(m_create)
    r = client.post(
        f"/clones/{clone_id}/monologues", json=monologues, headers=creator_headers
    )
    assert r.status_code == 201

    yield clone_id

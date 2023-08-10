import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import schemas
from app.clone.types import InformationStrategy, MemoryStrategy


def load_makima_create() -> schemas.CloneCreate:
    path = Path("tests") / "makima.json"
    with open(path, "r") as f:
        data = json.load(f)
        clone = schemas.CloneCreate(**data, is_public=True, tags=["anime"])
    return clone


@pytest.fixture(name="makima_id", scope="module")
def makima_clone_fixture(
    client: TestClient,
    creator_headers: dict[str, str],
    user_headers: dict[str, str],
    db: Session,
) -> str:
    # Create the Makima clone. It has a tag field, but for testing, no tags exist yet
    clone_create = load_makima_create()
    clone_create.greeting_message = "Jonny-kun, have you been a good dog?"
    r = client.post(
        "/clones/",
        headers=creator_headers,
        json=clone_create.model_dump(exclude_unset=True, exclude={"tags"}),
    )
    data = r.json()
    clone_id = str(data["id"])
    assert r.status_code == 201, data

    yield clone_id


def test_zero_memory_convo(
    client: TestClient, user_headers: dict[str, str], makima_id: str, db: Session
):
    # Create a conversation as User
    user_name = "Jonny"
    convo_create = schemas.ConversationCreate(
        clone_id=makima_id,
        user_name=user_name,
        memory_strategy=MemoryStrategy.none,
        information_strategy=InformationStrategy.internal,
        adaptation_strategy=None,
    )
    req_data = jsonable_encoder(convo_create)
    r = client.post("/conversations/", json=req_data, headers=user_headers)
    data = r.json()
    assert r.status_code == 201, data
    convo_id = data["id"]

    # assert that there are no current revisions
    # because the last message is the greeting message
    r = client.get(
        f"/conversations/{convo_id}/current_revisions",
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 0

    # add a new user message. idk fastapi-users prolly has a 401, not gonna fight it
    msg_create = schemas.MessageCreate(content="aye wussup")
    r = client.post(
        f"/conversations/{convo_id}/messages",
        json=msg_create.model_dump(),
        headers={"Cookie": "lol=no"},
    )
    data = r.json()
    assert r.status_code in [401, 403], data

    msg_create = schemas.MessageCreate(content="aye wussup")
    r = client.post(
        f"/conversations/{convo_id}/messages",
        json=msg_create.model_dump(),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 201, data

    # add a second message, before requesting one from the clone
    msg_create = schemas.MessageCreate(content="wut dat mouf do doe")
    r = client.post(
        f"/conversations/{convo_id}/messages",
        json=msg_create.model_dump(),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 201, data

    # test message querying
    # test sorting
    for srt in ["oldest", "newest"]:
        r = client.get(
            f"/conversations/{convo_id}/messages",
            params=dict(q="wussup", sort=srt),
            headers=user_headers,
        )
        data = r.json()
        assert r.status_code == 200, data
        assert len(data) == 3, data
    for srt in ["embedding", "similarity"]:
        # test that these two require a search query to run
        r = client.get(
            f"/conversations/{convo_id}/messages",
            params=dict(sort=srt),
            headers=user_headers,
        )
        assert r.status_code == 409

        r = client.get(
            f"/conversations/{convo_id}/messages",
            params=dict(q="wussupp", sort=srt),
            headers=user_headers,
        )
        data = r.json()
        assert r.status_code == 200, data
        assert "wussup" in data[0]["content"]
    # test that only the superuser can get non-main and non-active messages
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(is_active=False, is_main=False),
        headers=user_headers,
    )
    assert r.status_code == 403, data
    # test sent_before timestamp
    sent_before = datetime.now() - timedelta(days=7)
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(sent_before=sent_before),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 0
    # test sent_after timestamp
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(sent_after=sent_before),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 3
    # test getting last message
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(limit=1, sort="newest"),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 1
    assert "mouf" in data[0]["content"]
    assert not data[0]["is_clone"]

    # assert that there are no current revisions
    # because the last message was the user
    r = client.get(
        f"/conversations/{convo_id}/current_revisions",
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 0

    # cross your fingers and pray this works. generate a clone message
    r = client.post(
        f"/conversations/{convo_id}/generate",
        json=dict(is_revision=False),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 201, data
    assert data["is_clone"]
    assert data["is_main"]
    assert data["is_active"]
    orig_id = data["id"]

    # generate a revision
    r = client.post(
        f"/conversations/{convo_id}/generate",
        json=dict(is_revision=True),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 201, data
    assert data["is_clone"]
    assert data["is_main"]
    assert data["is_active"]
    new_id = data["id"]

    # check we have multiple revisions
    r = client.get(
        f"/conversations/{convo_id}/current_revisions",
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 2, data
    assert sum(x["is_main"] for x in data) == 1, data

    # check the latest messages only contains one revision
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(limit=2, sort="newest"),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 2
    assert data[0]["is_clone"]
    assert not data[1]["is_clone"]
    assert data[0]["id"] == new_id

    # switch revision
    r = client.post(
        f"/conversations/{convo_id}/messages/{orig_id}/is_main",
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert data["id"] == orig_id, data

    # check the latest messages now shows the new revision
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(limit=2, sort="newest"),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 2
    assert data[0]["is_clone"]
    assert not data[1]["is_clone"]
    assert data[0]["id"] == orig_id

    # delete everything but the first message in the conversation
    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(sort="oldest", limit=2),
        headers=user_headers,
    )
    assert r.status_code == 200
    second_msg_id = r.json()[1]["id"]
    r = client.delete(
        f"/conversations/{convo_id}/messages/{second_msg_id}",
        headers=user_headers,
    )
    assert r.status_code == 204

    r = client.get(
        f"/conversations/{convo_id}/messages",
        params=dict(sort="newest", limit=2),
        headers=user_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 1, data

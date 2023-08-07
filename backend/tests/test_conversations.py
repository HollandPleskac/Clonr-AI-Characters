import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_conversations(
    client: TestClient, makima: tuple[dict[str, str], str], user_headers: dict[str, str]
):
    # test create convo
    makima_headers, clone_id = makima
    convo_create = schemas.ConversationCreate(clone_id=clone_id)
    data = jsonable_encoder(convo_create)
    print(data)
    r = client.post("/conversations/", json=data, headers=user_headers)
    data = r.json()
    assert r.status_code == 201, data
    convo_id = data["id"]

    # test get convo
    r = client.get(f"/conversations/{convo_id}", headers=user_headers)
    data = r.json()
    assert r.status_code == 200, data
    assert data["id"] == convo_id

    # test that the creator cannot get the convo
    r = client.get(f"/conversations/{convo_id}", headers=makima_headers)
    data = r.json()
    assert r.status_code == 403, data

    # test patch convo inactive
    r = client.patch(
        f"/conversations/{convo_id}", headers=user_headers, json=dict(is_active=False)
    )
    assert r.status_code == 200, r.json()

    # test that we cannot find an inactive conversation
    r = client.get(f"/conversations/{convo_id}", headers=user_headers)
    data = r.json()
    assert r.status_code == 404, data


def test_conversation_initialization(
    client: TestClient,
    makima: tuple[dict[str, str], str],
    user_headers: dict[str, str],
    db: Session,
):
    # create convo with advanced memory
    makima_headers, clone_id = makima
    convo_create = schemas.ConversationCreate(
        clone_id=clone_id,
        memory_strategy=schemas.MemoryStrategy.long_term,
        information_strategy=schemas.InformationStrategy.internal,
        adaptation_strategy=schemas.AdaptationStrategy.dynamic,
    )
    data = jsonable_encoder(convo_create)
    r = client.post("/conversations/", json=data, headers=user_headers)
    data = r.json()
    r.status_code == 201, data
    convo_id = data["id"]

    # test memories are nonzero and have one memory
    r = db.scalars(
        sa.select(models.Memory).where(models.Memory.conversation_id == convo_id)
    )
    mems = r.all()
    assert len(mems) == 1, mems

    # test that there is a single message, and it's the greating
    r = db.scalars(
        sa.select(models.Message).where(models.Message.conversation_id == convo_id)
    )
    msgs = r.all()
    assert len(msgs) == 1, msgs

    # test that our database event triggered to increase the number of messages for this clone
    r = db.get(models.Clone, clone_id)
    assert r.num_conversations >= 1, r
    assert r.num_messages >= 1, r

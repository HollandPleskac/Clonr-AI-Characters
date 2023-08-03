from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from app import schemas


def test_conversations(
    client: TestClient, makima: tuple[dict[str, str], str], user_headers: dict[str, str]
):
    # test create convo
    makima_headers, clone_id = makima
    convo_create = schemas.ConversationCreate(clone_id=clone_id)
    data = jsonable_encoder(convo_create)
    r = client.post("/conversations/", json=data, headers=user_headers)
    data = r.json()
    r.status_code == 201, data
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

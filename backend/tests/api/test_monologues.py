from fastapi.testclient import TestClient

from app import schemas


def test_monologues(client: TestClient, makima: tuple[dict[str, str], str]):
    makima_headers, clone_id = makima

    # Create some monologues
    m1_create = schemas.MonologueCreate(
        content="foo bar baz.",
        source="manual",
    ).model_dump()
    m2_create = schemas.MonologueCreate(
        content="nickelback is the greatest band ever.",
        name="nickelback",
    ).model_dump()
    r = client.post(
        f"/clones/{clone_id}/monologues",
        json=[m1_create, m2_create],
        headers=makima_headers,
    )
    data = r.json()
    assert r.status_code == 201, data
    monologue_id = data[1]["id"]

    # test get monologue
    r = client.get(
        f"/clones/{clone_id}/monologues/{monologue_id}", headers=makima_headers
    )
    data = r.json()
    assert r.status_code == 200, data
    assert data["id"] == monologue_id

    # test delete monologue
    r = client.delete(
        f"/clones/{clone_id}/monologues/{monologue_id}", headers=makima_headers
    )
    assert r.status_code == 204, r
    r = client.get(
        f"/clones/{clone_id}/monologues/{monologue_id}", headers=makima_headers
    )
    assert r.status_code == 404, r.json()

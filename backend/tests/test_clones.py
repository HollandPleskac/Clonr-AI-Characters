from fastapi.testclient import TestClient

from app import schemas


def test_clones(
    client: TestClient, creator_headers: dict[str, str], user_headers: dict[str, str]
):
    name = "Makima"
    short_description = "Makima is the leader of the Public Safety Devil Hunter organization, and also the Control Devil."
    greeting_message = "Hmm... you seem interesting"
    inp = schemas.CloneCreate(
        name=name, short_description=short_description, is_public=False
    )
    data = inp.dict()

    # Create a basic clone
    r = client.post("/clones/create", headers=creator_headers, json=data)
    data = r.json()
    id = str(data["id"])
    assert r.status_code == 201, data
    assert data["greeting_message"] is None

    # add greeting message
    r = client.patch(
        f"/clones/{id}",
        headers=creator_headers,
        json=dict(greeting_message=greeting_message),
    )
    data = r.json()
    assert r.status_code == 200, r.json()
    assert data["greeting_message"] == greeting_message

    # assert you can get a clone you own
    r = client.get(f"/clones/{id}", headers=creator_headers)
    assert r.status_code == 200

    # assert the clone is not visible to others
    r = client.get(f"/clones/{id}", headers=user_headers)
    assert r.status_code == 400, r.json()

    # change clone to be publicly visible, but hide greeting message
    r = client.patch(
        f"/clones/{id}",
        headers=creator_headers,
        json=dict(is_public=True, is_greeting_message_public=False),
    )
    assert r.status_code == 200, r.json()

    # assert that clone is visible but greeting message isn't
    r = client.get(f"/clones/{id}", headers=user_headers)
    data = r.json()
    assert r.status_code == 200, data
    assert data["greeting_message"] is None

    # add a long description, then check that the embedding was generated
    r = client.patch(
        f"/clones/{id}",
        headers=creator_headers,
        json=dict(
            long_description="The public safety administrator who turned out to be the Control devil. She's smart."
        ),
    )
    assert r.status_code == 200, r.json()
    assert r.json()["long_description"]

    # Add additional clone data to use for testing search
    for name, desc in zip(
        ["badass penguin", "bar", "dangerous pencil"],
        [
            "a penguin with a mean streak",
            "This creator is a grammy award winning hip hop artist with years of freestyle experience spitting on trap beats.",
            "a radioactive pencil eraser",
        ],
    ):
        r = client.post(
            "/clones/create",
            headers=creator_headers,
            json=dict(
                name=name, long_description=desc, short_description=desc, is_public=True
            ),
        )
        assert r.status_code == 201

    # test that similarity search works
    r = client.get(
        "/clones/similar", params=dict(q="rappers", limit=10), headers=creator_headers
    )
    assert r.status_code == 200, r.json()
    assert (
        r.json()[0]["name"] == "bar"
    ), r.json()  # rapper whould be similar to hip hop artist... I hope.

    # test that substring search works
    r = client.get("/clones/search", params=dict(q="pEnC"), headers=creator_headers)
    assert r.status_code == 200, r.json()
    assert r.json()[0]["name"] == "dangerous pencil", r.json()

    # delete the clone
    r = client.delete(f"/clones/{id}", headers=creator_headers)
    assert r.status_code == 403, "Only superusers can delete clones!"

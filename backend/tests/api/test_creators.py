from fastapi.testclient import TestClient


def test_creators(
    client: TestClient,
    creator_headers: dict[str, str],
    superuser_headers: dict[str, str],
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
    creator_id = data["user_id"]

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
    r = client.patch(
        f"/creators/{creator_id}", json=dict(is_active=True), headers=superuser_headers
    )
    assert r.status_code == 200, r.json()

    # test creator is active
    r = client.get("/creators/me", headers=creator_headers)
    assert r.status_code == 200, r.json()

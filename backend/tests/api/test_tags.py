from fastapi.testclient import TestClient

from app import schemas


def test_tags(client: TestClient, superuser_headers: dict[str, str]):
    names = ["foo1", "bar1", "baz1"]

    # create tags
    for name in names:
        r = client.post("/tags/", json=dict(name=name), headers=superuser_headers)
        data = r.json()
        assert r.status_code == 201, data

    tag_id = data["id"]

    # get all tags using db (no auth needed)
    r = client.get("/tags/")
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == len(names)

    # get one tag by ID
    id = data[0]["id"]
    name = data[0]["name"]
    r = client.get(f"/tags/{id}")
    data = r.json()
    assert r.status_code == 200, data
    assert data["name"] == name

    # patch a tag
    r = client.patch(
        f"/tags/{tag_id}", json=dict(color_code="ffffff"), headers=superuser_headers
    )
    data = r.json()
    assert r.status_code == 200, data
    assert data["color_code"] == "ffffff"

    # delete a tag, and check it's not there
    r = client.delete(f"/tags/{tag_id}", headers=superuser_headers)
    assert r.status_code == 204, r.status_code
    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 404, r.status_code


def test_browse_clones_by_tag(client: TestClient, superuser_headers: dict[str, str]):
    names = ["foo2", "bar2", "baz2"]

    # create tags
    for name in names:
        r = client.post("/tags/", json=dict(name=name), headers=superuser_headers)
        data = r.json()
        assert r.status_code == 201, data
    r = client.get("/tags/")
    tags = r.json()
    assert r.status_code == 200, tags
    tag_ids = [x["id"] for x in tags]
    print(tag_ids)

    # create some clones with these tags
    name = "test-clone"
    short_description = (
        "Makima is the leader of the Public Safety Devil Hunter organization"
        ", and also the Control Devil."
    )
    greeting_message = "Hmm... you seem interesting"
    clones: list[dict[str, str]] = []
    # [01], [012], and [12] are the setups
    tgs = [tag_ids[:2], tag_ids[:3], tag_ids[1:3]]
    for i, x in enumerate(tgs):
        inp = schemas.CloneCreate(
            name=f"{name}-{i}",
            short_description=short_description,
            is_public=True,
            tags=x,
            greeting_message=greeting_message,
        )
        data = inp.model_dump()
        r = client.post("/clones/", headers=superuser_headers, json=data)
        assert r.status_code == 201, r.json()
        assert r.json()["tags"], r.json()["tags"]
        clones.append(r.json())

    # test that we can query for multiple tags
    # query for containing tags [01], should return clones [01] and [012]
    r = client.get("/clones", params=dict(tags=tgs[0]))
    data = r.json()
    assert r.status_code == 200, data
    ids = sorted([x["id"] for x in data])
    expected_ids = sorted([x["id"] for x in clones[:2]])
    assert ids == expected_ids, (ids, expected_ids)

    # query for containing tags [12], should return clones [012] and [12]
    r = client.get("/clones", params=dict(tags=list(reversed(tgs[2]))))
    data = r.json()
    assert r.status_code == 200, data
    ids = sorted([x["id"] for x in data])
    expected_ids = sorted([x["id"] for x in clones[1:]])
    assert ids == expected_ids, (ids, expected_ids)

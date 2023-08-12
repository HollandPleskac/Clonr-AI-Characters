from fastapi.testclient import TestClient

from app import schemas


def test_long_descs(
    client: TestClient,
    makima: tuple[dict[str, str], str],
    superuser_headers: dict[str, str],
):
    makima_headers, clone_id = makima

    # Create some documents
    doc1_create = schemas.DocumentCreate(
        content="foo bar baz. 465" * 120,
        name="foobar2235",
        description="a bunch of nonsense 52345",
        type="manual",
        url=None,
    ).model_dump()
    doc2_create = schemas.DocumentCreate(
        content="nickelback is the greatest band ever 26134. " * 120,
        name="nickelback2532",
        description="only the truth",
        type="wiki",
        url="https://nickelback.the.one.true.god.com",
    ).model_dump()
    for d in [doc1_create, doc2_create]:
        print(d)
        r = client.post(f"/clones/{clone_id}/documents", json=d, headers=makima_headers)
        data = r.json()
        assert r.status_code == 201, data

    # test generate long description
    for _ in range(2):
        r = client.post(
            f"/clones/{clone_id}/generate_long_description",
            headers=superuser_headers,
        )
        data = r.json()
        assert r.status_code == 201, data

    # retrieve long descriptions
    r = client.get(
        f"/clones/{clone_id}/long_descriptions",
        headers=superuser_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) >= 2

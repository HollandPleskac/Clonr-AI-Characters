import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import models, schemas


def test_documents(client: TestClient, makima: tuple[dict[str, str], str], db: Session):
    makima_headers, clone_id = makima

    # Create some documents
    doc1_create = schemas.DocumentCreate(
        content="foo bar baz. " * 120,
        name="foobar",
        description="a bunch of nonsense",
        type="manual",
        url=None,
    ).dict()
    doc2_create = schemas.DocumentCreate(
        content="nickelback is the greatest band ever. " * 120,
        name="nickelback",
        description="only the truth",
        type="wiki",
        url="https://nickelback.the.one.true.god.com",
    ).dict()
    for d in [doc1_create, doc2_create]:
        r = client.post(
            f"/clones/{clone_id}/documents/create", json=d, headers=makima_headers
        )
        data = r.json()
        r.status_code == 201, data
        doc_id = data["id"]  # the last doc_id is nickelback. python quirk.

    # test the nodes exist, and
    nodes = db.scalars(
        sa.select(models.Node).where(models.Node.document_id == doc_id)
    ).all()
    assert all(str(x.document_id) == doc_id for x in nodes), (
        doc_id,
        nodes[0].document_id,
    )

    # test get document
    r = client.get(f"/clones/{clone_id}/documents/{doc_id}", headers=makima_headers)
    data = r.json()
    assert r.status_code == 200, data
    assert data["id"] == doc_id

    # test search documents
    r = client.get(
        f"/clones/{clone_id}/documents",
        params=dict(name="nickel"),
        headers=makima_headers,
    )
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 1
    assert data[0]["id"] == doc_id
    r = client.get(f"/clones/{clone_id}/documents", headers=makima_headers)
    data = r.json()
    assert r.status_code == 200, data
    assert len(data) == 2
    assert data[0]["id"] == doc_id

    # test delete document
    r = client.delete(f"/clones/{clone_id}/documents/{doc_id}", headers=makima_headers)
    assert r.status_code == 204, r
    r = client.get(f"/clones/{clone_id}/documents/{doc_id}", headers=makima_headers)
    assert r.status_code == 400, r.json()

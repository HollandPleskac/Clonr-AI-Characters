import numpy as np
import pytest

from app.embedding import EmbeddingClient, wait_for_embedding


@pytest.fixture
async def _wait_for_embedding():
    await wait_for_embedding()


@pytest.mark.asyncio
async def test_get_methods():
    async with EmbeddingClient() as client:
        name = await client.encoder_name()
        assert name == "intfloat/e5-small-v2", name

        normalized = await client.is_normalized()
        assert normalized, normalized


@pytest.mark.asyncio
async def test_encoding_and_ranking():
    query = "foo"
    passages = ["bar", "foo", "baz"]
    async with EmbeddingClient() as client:
        query_emb = np.array(await client.encode_query(query))
        query_emb2 = np.array(await client.encode_query([query]))
        assert np.allclose(
            query_emb, query_emb2
        ), "Shape mismatch when submitting str vs list[str] query"
        assert (sh := query_emb.shape) == (1, 384), sh

        # test that foo is encoded close to foo and far from bar
        passage_emb = np.array(await client.encode_passage(query))
        assert (scr := np.square(query_emb - passage_emb).mean()) < 1e-2, scr
        other = np.array(await client.encode_passage(passages[0]))
        assert (scr2 := np.square(query_emb - other).mean()) > scr, (scr, scr2)

        # test passage shape
        passage_embs = np.array(await client.encode_passage(passages))
        assert (x := passage_embs.shape) == (3, 384), x

        # test that foo is closest to foo
        scrs = np.array(await client.rerank_score(query, passages))
        assert scrs[1] > scrs[0] and scrs[1] > scrs[2], scrs

from typing import Any, Iterator, TypeVar

import numpy as np
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

from .types import (
    GenAgentsSearchable,
    GenAgentsSearchParams,
    GenAgentsSearchResult,
    MetricType,
    ReRankResult,
    ReRankSearchParams,
    VectorSearchable,
    VectorSearchParams,
    VectorSearchResult,
)

INF = int(1e6)
DEFAULT_RERANK_FIRST_PASS_MAX_ITEMS = 20

T = TypeVar("T", bound=VectorSearchable)
S = TypeVar("S", bound=GenAgentsSearchable)


async def vector_search(
    query: str,
    model: T,
    params: VectorSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.SQLColumnExpression] | None = None,
) -> list[VectorSearchResult[T]]:
    q = (await embedding_client.encode_query(query))[0]

    if params.metric == MetricType.cosine:
        dist = model.embedding.cosine_distance(q)
    elif params.metric == MetricType.euclidean:
        dist = model.embedding.l2_distance(q)
    elif params.metric == MetricType.inner_product:
        assert (
            await embedding_client.is_normalized()
        ), "Cannot user inner product with non-normalized embeddings."
        # NOTE (Jonny): I have no fucking idea why, but max_inner_product is actually the negative of A \cdot B
        # cosine distance in pgvector is correctly 1 - A \cdot B, so here we have to do 1 + to match it.
        dist = 1 + model.embedding.max_inner_product(q)
    else:
        raise TypeError(f"Invalid distance type: ({params.metric})")

    dist = dist.label("distance")

    # Order by should be ascending, as we want to minimize distance here
    stmt = sa.select(model, dist)

    for f in filters or []:
        stmt = stmt.where(f)

    stmt = stmt.order_by(dist.asc()).limit(params.max_items)

    r = await db.execute(stmt)

    res: list[VectorSearchResult] = []

    max_tokens = params.max_tokens  # copy so we don't mess up when using shared params.

    for i, (mdl, scr) in enumerate(r):
        if max_tokens < INF:
            # TODO (Jonny) Is this going to be too slow? maybe, tokenizing is expensive.
            # We should probably save this value, but then the data in the DB will be
            # wrong if we change tokenizers. such a pain.
            max_tokens -= tokenizer.length(mdl.content)
        if i >= params.max_items or max_tokens < 0:
            break
        cur = VectorSearchResult(model=mdl, distance=scr, metric=params.metric)
        res.append(cur)
    return res


async def rerank_search(
    query: str,
    model: T,
    params: ReRankSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.SQLColumnExpression] | None = None,
) -> list[ReRankResult[T]]:
    # If max items is not passed, defaults to pulling 20 results
    # else, it's max items * multiplier
    first_pass_max_items = int(
        params.max_items * params.overshot_multiplier
        if params.max_items < INF
        else DEFAULT_RERANK_FIRST_PASS_MAX_ITEMS
    )

    # Grab the vector search results based on distance first
    first_pass_params = VectorSearchParams(
        metric=params.metric, max_items=first_pass_max_items, max_tokens=INF
    )
    vsearch_results = await vector_search(
        query=query,
        model=model,
        params=first_pass_params,
        db=db,
        embedding_client=embedding_client,
        tokenizer=tokenizer,
        filters=filters,
    )

    if not vsearch_results:
        return []

    # batch compute the rerank scores
    rerank_scores = await embedding_client.rerank_score(
        query=query, passages=[x.model.content for x in vsearch_results]
    )

    # the rerank score is a logit for the similarity score, with domain [0, 1]
    # so a rerank score of 1 is perfect similarity
    ids = reversed(np.argsort(rerank_scores))

    # filter as we did for vector search
    max_tokens = params.max_tokens
    res: list[ReRankResult] = []
    for i, j in enumerate(ids):
        r = vsearch_results[j]
        scr = rerank_scores[j]
        if i >= params.max_items or max_tokens < 0:
            break
        if max_tokens < INF:
            max_tokens -= tokenizer.length(r.model.content)
        cur = ReRankResult(
            model=r.model, distance=r.distance, metric=params.metric, rerank_score=scr
        )
        res.append(cur)
    return res


async def gen_agents_search(
    query: str,
    model: S,
    params: GenAgentsSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.ColumnElement[Any]] | None = None,
) -> list[GenAgentsSearchResult[S]]:
    alpha_sum = params.alpha_relevance + params.alpha_importance + params.alpha_recency
    time_decay = 0.5 ** (1 / params.half_life_seconds)  # Eq: gamma^t = 1/2

    # recency score
    seconds = sa.func.extract(
        "epoch", (sa.func.current_timestamp() - model.last_accessed_at)
    ).cast(sa.Float)
    recency_score = sa.func.pow(time_decay, seconds)

    # relevance score
    q = (await embedding_client.encode_query(query))[0]
    dist = model.embedding.cosine_distance(
        q
    )  # TODO (Jonny): check if inner product is ok
    relevance_score = 0.5 * (2 - dist)  # convert to similarity i.e. [2, 0] -> [0, 1]

    # importance score
    importance_score = model.importance.cast(sa.Float) / params.max_importance_score

    # gen_agents_score
    gen_agents_score = (
        params.alpha_importance * importance_score
        + params.alpha_recency * recency_score
        + params.alpha_relevance * relevance_score
    ) / alpha_sum
    gen_agents_score = gen_agents_score.label("gen_agents_score")

    # Order by should be descending, as we want to maximize the score
    stmt = sa.select(
        model, gen_agents_score, recency_score, relevance_score, importance_score
    )
    for f in filters or []:
        stmt = stmt.where(f)
    stmt = stmt.order_by(gen_agents_score.desc()).limit(params.max_items)
    result_itr: Iterator[
        tuple[GenAgentsSearchable, float, float, float, float]
    ] = await db.execute(
        stmt
    )  # type: ignore

    # filter as we did for vector search
    max_tokens = params.max_tokens
    res: list[GenAgentsSearchResult] = []
    for i, (x, ga_scr, rec_scr, rel_scr, imp_scr) in enumerate(result_itr):
        if max_tokens < INF:
            max_tokens -= tokenizer.length(x.content)
        if i >= params.max_items or max_tokens < 0:
            break
        cur = GenAgentsSearchResult(
            model=x,
            score=ga_scr,
            recency_score=rec_scr,
            relevance_score=rel_scr,
            importance_score=imp_scr,
            metric=params.metric,
        )
        res.append(cur)
    return res

import datetime
import enum
from dataclasses import dataclass
from typing import Protocol, TypeVar

import numpy as np
import sqlalchemy as sa
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.embedding import EmbeddingClient
from clonr.tokenizer import Tokenizer

INF = int(1e6)
DEFAULT_RERANK_FIRST_PASS_MAX_ITEMS = 20


class VectorSearchProtocol(Protocol):
    embedding: list[float] | np.ndarray
    content: str


class GenAgentsSearchProtocol(Protocol):
    embedding: list[float] | np.ndarray
    content: str
    importance: int | float
    last_accessed_at: datetime.datetime


VectorSearchable = TypeVar("VectorSearchable", bound=VectorSearchProtocol)
GenAgentsSearchable = TypeVar("GenAgentsSearchable", bound=GenAgentsSearchProtocol)


class MetricType(str, enum.Enum):
    """Distance metrics available.
    Quick distance math because I'm stupid.
    cosine similarity = $\cos\theta = (a \cdot b) / |a||b|$. So the range is -1 for anticorrelated and +1 for correlated.
    inner product = $a \cdot b$ which is equivalent to cosine similarity for normalized vectors
    cosine distance is not a real distance (triangle inequality violated). Given by 1 - cossim and range is [0, 2]
    GenAgents normalizes to [0, 1] which is equivalent to dividing by 2.

    Pgvector only supports three types, cosine, inner_product, and euclidean.
    https://github.com/pgvector/pgvector-python/blob/master/pgvector/sqlalchemy/__init__.py
    """

    cosine: str = "cosine"
    inner_product: str = "inner_product"
    euclidean: str = "euclidean"


@dataclass
class VectorSearchResult:
    model: VectorSearchable
    distance: float
    metric: MetricType


@dataclass
class ReRankResult(VectorSearchResult):
    rerank_score: float


@dataclass
class GenAgentsSearchResult:
    model: GenAgentsSearchable
    recency_score: float
    relevance_score: float
    importance_score: float
    score: float
    metric: MetricType


class VectorSearchParams(BaseModel):
    max_items: int = Field(
        default=INF, ge=1, detail="Maximum number of items to retrieve from query"
    )
    max_tokens: int = Field(
        default=INF,
        ge=16,
        detail="Maximum number of tokens from all retrieved results, inlcuding newlines",
    )
    metric: MetricType = Field(
        default=MetricType.cosine,
        detail="Which metric to use. Inner product is faster, and equal to cosine if all embeddings are normalized (which they should be for us).",
    )


class ReRankSearchParams(VectorSearchParams):
    overshot_multiplier: float = Field(
        ge=1,
        default=2,
        detail="Increases number of retrieved items in 1st pass by `overshot_multiplier * max_items`, which is then cut down by re-ranking.",
    )


class GenAgentsSearchParams(VectorSearchParams):
    alpha_recency: float = Field(
        le=1.0,
        ge=0.0,
        detail="Weighting for how recently this memory was accessed.",
    )
    alpha_relevance: float = Field(
        le=1.0, ge=0.0, detail="Weighting for cosine distance similarity score"
    )
    alpha_importance: float = Field(
        le=1.0, ge=0.0, detail="Weighting for LLM predicted importance score"
    )
    half_life_seconds: float = Field(
        default=24.0 * 60 * 60,
        ge=0.0,
        detail="Half-life (in seconds) for decaying memory recency. For example, a value of 60 means that after one minute, the recency score drops from 1 => 0.5, after 2 minutes it is 0.25, 3m 0.125, etc.",
    )
    max_importance_score: float = Field(
        default=10,
        detail="Normalizing factor for the importance score. Used to weight memory importance.",
    )


async def vector_search(
    query: str,
    model: VectorSearchable,
    params: VectorSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.SQLColumnExpression] | None = None,
) -> list[VectorSearchResult]:
    q = (await embedding_client.encode_query(query))[0]

    if params.metric == MetricType.cosine:
        dist = model.embedding.cosine_distance(q)
    elif params.metric == MetricType.euclidean:
        dist = -model.embedding.l2_distance(q)
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
    model: VectorSearchable,
    params: ReRankSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.SQLColumnExpression] | None = None,
) -> list[ReRankResult]:
    # If max items is not passed, defaults to pulling 20 results
    # else, it's max items * multiplier
    first_pass_max_items = (
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
    model: GenAgentsSearchable,
    params: GenAgentsSearchParams,
    db: AsyncSession,
    embedding_client: EmbeddingClient,
    tokenizer: Tokenizer,
    filters: list[sa.SQLColumnExpression] | None = None,
) -> list[GenAgentsSearchResult]:
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
    result_itr = await db.execute(stmt)

    # filter as we did for vector search
    max_tokens = params.max_tokens
    res: list[ReRankResult] = []
    for i, (x, ga_scr, rec_scr, rel_scr, imp_scr) in enumerate(result_itr):
        if max_tokens < INF:
            max_tokens -= tokenizer.length(x.model.content)
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

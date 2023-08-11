import datetime
import enum
from dataclasses import dataclass
from typing import Protocol, TypeVar

import numpy as np
from pydantic import BaseModel, Field

INF = int(1e10)


class MemoryStrategy(str, enum.Enum):
    none = "none"
    short_term = "short_term"
    long_term = "long_term"


class InformationStrategy(str, enum.Enum):
    none = "none"
    internal = "internal"
    external = "external"


class AdaptationStrategy(str, enum.Enum):
    static = "static"
    dynamic = "dynamic"
    fluid = "fluid"


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
        default=MetricType.inner_product,
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
        default=1.0,
        le=1.0,
        ge=0.0,
        detail="Weighting for how recently this memory was accessed.",
    )
    alpha_relevance: float = Field(
        default=1.0,
        le=1.0,
        ge=0.0,
        detail="Weighting for cosine distance similarity score",
    )
    alpha_importance: float = Field(
        default=1.0,
        le=1.0,
        ge=0.0,
        detail="Weighting for LLM predicted importance score",
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

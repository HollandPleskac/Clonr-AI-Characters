import numpy as np

from typing import Protocol, TypeVar
from dataclasses import dataclass
from pydantic import BaseModel, Field
import enum

INF = int(1e10)


class VectorSearchProtocol(Protocol):
    embedding: list[float] | np.ndarray
    content: str


VectorSearchable = TypeVar("VectorSearchable", bound=VectorSearchProtocol)


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
        detail="The number of additional items to pull before reranking",
    )


class GenAgentsSearchParams(VectorSearchParams):
    alpha_recency: float = Field(detail=1.0)
    alph_relevance: float = Field(
        default=1.0, detail="Weighting for cosine distance similarity score"
    )
    alpha_importance: float = Field(
        default=1.0, detail="Weighting for LLM predicted importance score"
    )

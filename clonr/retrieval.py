from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np

from clonr.embedding import CrossEncoder
from clonr.storage import InMemoryVectorDB
from clonr.utils import get_current_datetime


# This is temporary, it doesn't really make sense to return list[dict] in general.
# but also, it likely won't be upgraded as this is not necessarily marked for prod.
class Retriever(ABC):
    @abstractmethod
    def query(self, *args, **kwargs) -> list[dict]:
        pass


class RerankRetriever(Retriever):
    def __init__(
        self,
        cross_encoder: CrossEncoder = CrossEncoder.default(),
        k_biencoder: int = 10,
    ):
        self.cross_encoder = cross_encoder
        self.k_biencoder = k_biencoder

    def query(self, query: str, db: InMemoryVectorDB, k: int = 3) -> list[dict]:
        biencoder_results = db.query(query=query, k=self.k_biencoder)
        try:
            scores = self.cross_encoder.similarity_score(
                query, [x["content"].strip() for x in biencoder_results]
            )
        except KeyError:
            raise KeyError("The added model does not contain a `content` attribute.")
        top_ids = np.argsort([-x[0] for x in scores])
        return [
            {**biencoder_results[i], "rerank_score": scores[i][0]} for i in top_ids[:k]
        ]

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}(cross_encoder={self.cross_encoder.name}, k_biencoder={self.k_biencoder})"
        except Exception:
            return super().__repr__()


class GenerativeAgentsRetriever(Retriever):
    def __init__(
        self,
        alpha_recency: float = 1.0,
        alpha_importance: float = 1.0,
        alpha_relevance: float = 1.0,
        k_biencoder: int = -1,
        half_life_hours: float = 24.0,
        max_importance_score: int = 9,
    ):
        self.alpha_recency = alpha_recency
        self.alpha_importance = alpha_importance
        self.alpha_relevance = alpha_relevance
        self.k_biencoder = 1_000_000 if k_biencoder < 1 else k_biencoder
        self.half_life_hours = half_life_hours
        seconds = 60 * 60 * half_life_hours
        self.time_decay = 0.5 ** (1 / seconds)
        self.max_importance_score = max_importance_score
        self._alpha_sum = (
            self.alpha_recency + self.alpha_importance + self.alpha_relevance
        )
        assert self._alpha_sum > 0, "At least one alpha value must be > 0."

    def query(self, query: str, db: InMemoryVectorDB, k: int = 3):
        """The vectordb must return objects that have keys for timestamp,
        importance, and similarity score.

        Args:
            query (str): query to run. a string.
            db (InMemoryVectorDB): vectordb with the above traits.
            k (int, optional): how many results to return. There is no optimization
                here, so it doesn't really matter. Defaults to 3.
        """
        items = db.query(query=query, k=self.k_biencoder)
        scores: list[float] = []
        for item in items:
            score = 0

            # calculate recency score
            timestamp: str | datetime = item["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            seconds = (get_current_datetime() - timestamp).seconds
            recency = self.time_decay**seconds
            score += recency * self.alpha_recency

            # caluclate importance score, normalized [0, 1].
            importance = int(item["importance"]) / self.max_importance_score
            score += self.alpha_importance * importance

            # calculate relevance score
            score += self.alpha_relevance * item["similarity_score"]
            score /= self._alpha_sum

            # Use a negative score so that in the next argsort step we retrieve the smallest values.
            item["generative_agents_score"] = score
            scores.append(-score)
        ids = np.argsort(scores)[:k]
        return [items[i] for i in ids]

from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np

from clonr.embedding import CrossEncoder
from clonr.storage import InMemoryVectorDB
from clonr.tokenizer import Tokenizer
from clonr.utils import get_current_datetime

# we need an integer float('inf') so just hack it together here.
INF = 1_000_000

# TODO (Jonny): remove the -1 shit.
# it's messing up the vectordb retrieval, None is better.


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
        tokenizer: Tokenizer = Tokenizer.from_openai("gpt-3.5-turbo"),
    ):
        self.cross_encoder = cross_encoder
        self.tokenizer = tokenizer

    def query(
        self,
        query: str,
        db: InMemoryVectorDB,
        max_k: int = -1,
        max_tokens: int = -1,
        k_biencoder: int = -1,
    ) -> list[dict]:
        # TODO (Jonny): Retrieval with objects that don't have a content attribute
        # is fucked. you can't count tokens and can't re-rank
        assert max_k > 0 or max_tokens > 0, "Either max_k or max_tokens should be set"
        max_k = max_k if max_k > 0 else INF
        max_tokens = max_tokens if max_tokens > 0 else INF
        biencoder_results = db.query(query=query, k=k_biencoder)
        max_tokens = max_tokens if max_tokens > 0 else float("inf")
        try:
            scores = self.cross_encoder.similarity_score(
                query, [x["content"].strip() for x in biencoder_results]
            )
        except KeyError:
            raise KeyError("The added model does not contain a `content` attribute.")

        top_ids = np.argsort([-x[0] for x in scores])
        res: list[dict] = []
        for i in top_ids[:max_k]:
            obj = {**biencoder_results[i], "rerank_score": scores[i][0]}
            if max_tokens < INF:
                max_tokens -= self.tokenizer.length(obj["content"])
            if res and max_tokens < 0:
                break
            res.append(obj)
        return res

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}(cross_encoder={self.cross_encoder.name}, k_biencoder={self.k_biencoder})"
        except Exception:
            return super().__repr__()


# TODO (Jonny): I messed up. The time difference is calculated with respect to the "last-accessed" timestamp
# not the creation timestamp! We need to define how that last-access gets set, during which queries.
class GenerativeAgentsRetriever(Retriever):
    def __init__(
        self,
        alpha_recency: float = 1.0,
        alpha_importance: float = 1.0,
        alpha_relevance: float = 1.0,
        k_biencoder: int = -1,
        half_life_hours: float = 24.0,
        max_importance_score: int = 9,
        tokenizer: Tokenizer = Tokenizer.from_openai("gpt-3.5-turbo"),
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
        self.tokenizer = tokenizer
        assert self._alpha_sum > 0, "At least one alpha value must be > 0."

    def query(
        self,
        query: str,
        db: InMemoryVectorDB,
        max_k: int = -1,
        k_biencoder: int = -1,
        max_tokens: int = -1,
    ):
        """The vectordb must return objects that have keys for timestamp,
        importance, and similarity score.

        Args:
            query (str): query to run. a string.
            db (InMemoryVectorDB): vectordb with the above traits.
            k (int, optional): how many results to return. There is no optimization
                here, so it doesn't really matter. Defaults to 3.
        """
        assert max_k > 0 or max_tokens > 0, "Either max_k or max_tokens should be set"
        max_k = max_k if max_k > 0 else INF
        max_tokens = max_tokens if max_tokens > 0 else INF
        items = db.query(query=query, k=k_biencoder)
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
            score += (
                self.alpha_relevance * item["similarity_score"] / 2.0
            )  # cosine normalization!
            score /= self._alpha_sum

            # Use a negative score so that in the next argsort step we retrieve the smallest values.
            item["generative_agents_score"] = score
            scores.append(-score)

        ids = np.argsort(scores)[:max_k]
        res: list[dict] = []
        for i in ids[:max_k]:
            obj = items[i]
            if max_tokens < INF:
                max_tokens -= self.tokenizer.length(obj["content"])
            if res and max_tokens < 0:
                break
            res.append(obj)
        return res

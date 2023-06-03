from enum import Enum

import torch
import torch.nn.functional as F
from pydantic import BaseModel
from sentence_transformers import CrossEncoder
from torch import Tensor
from transformers import AutoModel, AutoTokenizer

DEFAULT_VECTOR_ENCODER = "intfloat/e5-small-v2"
DEFAULT_CROSS_ENCODER = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class EmbeddingType(str, Enum):
    query: str = "query"
    passage: str = "passage"


class VectorSearchResult(BaseModel):
    content: str
    score: float


class VectorEncoder:
    # TODO: we should store this locally or something just in case they become unavailable in the future!
    # Latency for small v2 is like 90ms per sentence. Pretty good overall.
    def __init__(self, model, tokenizer):
        self.tokenizer = tokenizer
        self.model = model
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    @classmethod
    def from_pretrained(cls, model_name: str | None = None):
        if model_name is None:
            model_name = DEFAULT_VECTOR_ENCODER
        model = AutoModel.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return cls(model=model, tokenizer=tokenizer)

    def _average_pool(
        self, last_hidden_states: Tensor, attention_mask: Tensor
    ) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        embeddings = last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
        normed_embeddings = F.normalize(embeddings, p=2, dim=1)
        return normed_embeddings

    @torch.no_grad()
    def _encode(
        self, text: str | list[str], encoding_type: EmbeddingType
    ) -> list[list[str]]:
        if isinstance(text, str):
            text = [text]
        text = [f"{encoding_type.value}: {x}" for x in text]
        inp = self.tokenizer(
            text, max_length=512, padding=True, truncation=True, return_tensors="pt"
        )
        inp = {k: v.to(self.device) for k, v in inp.items()}
        out = self.model(**inp)
        embeddings = (
            self._average_pool(out.last_hidden_state, inp["attention_mask"])
            .cpu()
            .detach()
        )
        return embeddings.tolist()

    def encode_query(self, text: str | list[str]) -> list[list[float]]:
        return self._encode(text, encoding_type=EmbeddingType.query)

    def encode_passage(self, text: str | list[str]) -> list[list[float]]:
        return self._encode(text, encoding_type=EmbeddingType.passage)


class ReRanker:
    def __init__(self, model):
        self.model = model

    @classmethod
    def from_pretrained(cls, name: str | None = None):
        model = CrossEncoder(DEFAULT_CROSS_ENCODER)
        return cls(model=model)

    def score(self, query: str, passage: str) -> VectorSearchResult:
        return self.model.predict([query, passage])

    def rank(self, query: str, passages: list[str]) -> list[VectorSearchResult]:
        res = [
            VectorSearchResult(content=content, score=self.score(query, content))
            for content in passages
        ]
        res.sort(key=lambda x: -x.score)
        return res

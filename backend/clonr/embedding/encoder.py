import numpy as np
import transformers
from clonr.embedding.types import EmbeddingType, ModelEnum
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

from clonr.utils import get_artifacts_dir


class EmbeddingModel:
    def __init__(
        self,
        model: transformers.PreTrainedModel,
        tokenizer: transformers.PreTrainedTokenizerBase,
        normalized: bool = True,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.max_tokens = self.model.config.max_position_embeddings
        self.dimension = self.model.config.hidden_size
        self.normalized = normalized

    @classmethod
    def from_pretrained(cls, model_name: ModelEnum, normalized: bool = True):
        if not (
            path := (get_artifacts_dir() / "onnx" / model_name.value.split("/")[-1])
        ).exists():
            raise FileNotFoundError(
                (
                    f"Could not find local Onnx copy at {path.resolve()}."
                    " First export using clonr.embedding.export_to_onnx.py"
                )
            )
        model = ORTModelForFeatureExtraction.from_pretrained(
            model_id=str(path.resolve()),
            local_files_only=True, 
        )
        tokenizer = AutoTokenizer.from_pretrained(str(path.resolve()))
        obj = cls(model=model, tokenizer=tokenizer, normalized=normalized)
        obj._pretrained_name = model_name.value
        return obj

    def _mean_pool(self, h: np.ndarray, attn_mask: np.ndarray) -> np.ndarray:
        mask = attn_mask[..., None]
        emb = np.where(mask, h, 0.0).sum(axis=1) / (mask.sum(axis=1) + 1e-9)
        if self.normalized:
            emb /= np.linalg.norm(emb, axis=1, keepdims=True)
        return emb

    def _encode(self, texts: list[str]) -> list[list[float]]:
        assert isinstance(texts, list), "Must pass list input. If just a string, make it a list of size 1."
        inp = self.tokenizer(
            texts,
            max_length=self.max_tokens,
            padding=True,
            truncation=True,
            return_tensors="np",
        )
        out = self.model(**inp)
        return self._mean_pool(out.last_hidden_state, inp["attention_mask"]).tolist()

    def encode_query(self, text: list[str]) -> list[list[float]]:
        text = [f"{EmbeddingType.query.value}: {x}" for x in text]
        return self._encode(text)

    def encode_passage(self, text: list[str]) -> list[list[float]]:
        text = [f"{EmbeddingType.passage.value}: {x}" for x in text]
        return self._encode(text)

    def __repr__(self):
        if hasattr(self, '_pretrained_name'):
            return f"{self.__class__.__name__}(model={self._pretrained_name}, dimension={self.dimension})"
        return f"{self.__class__.__name__}(dimension={self.dimension})"

import numpy as np
import transformers
from loguru import logger
from optimum.onnxruntime import (
    ORTModelForFeatureExtraction,
    ORTModelForSequenceClassification,
)

from clonr.embedding.types import CrossEncoderEnum, EmbeddingModelEnum, EmbeddingType
from clonr.tokenizer import _get_hf_tokenizer
from clonr.utils import get_artifacts_dir

# On CPU, sequential execution is pretty fast so it quickly outweighs
# The benefits of batching minus the downsides of padding. If using
# sequences without padding though, use a larger batch size.
# In the future we can also do this dynamically by scanning the stddev of lengths in a batch
MAX_BATCH_SIZE: int = 4


def get_model_or_download(model_name: str, download_if_needed: bool = False):
    if not (
        path := (get_artifacts_dir() / "onnx" / model_name.split("/")[-1])
    ).exists():
        if download_if_needed:
            from .export_to_onnx import export

            logger.info("Could not find a local Onnx copy.")
            logger.info("Proceeding to download and convert to Onnx.")
            export(model_name_or_dir=model_name)
        else:
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
    return model


class EmbeddingModel:
    def __init__(
        self,
        name: EmbeddingModelEnum,
        model: transformers.PreTrainedModel,
        tokenizer: transformers.PreTrainedTokenizerBase,
        normalized: bool = True,
        max_batch_size: int = MAX_BATCH_SIZE,
    ):
        self.name = name
        self.model = model
        self.tokenizer = tokenizer
        self.max_tokens = self.model.config.max_position_embeddings
        self.dimension = self.model.config.hidden_size
        self.normalized = normalized
        self.max_batch_size = max_batch_size

    @classmethod
    def _from_pretrained_transformers(
        cls, model_name: EmbeddingModelEnum, normalized: bool = True
    ):
        raise ValueError("Bro, don't use this, it's gonna break")
        model = transformers.AutoModel.from_pretrained(model_name.value)
        tokenizer = _get_hf_tokenizer(model_name.value)
        obj = cls(model=model, tokenizer=tokenizer, normalized=normalized)
        obj._pretrained_name = model_name.value
        return obj

    @classmethod
    def default(cls):
        return cls.from_pretrained(EmbeddingModelEnum.e5_small_v2)

    @classmethod
    def from_pretrained(
        cls,
        model_name: EmbeddingModelEnum = EmbeddingModelEnum.e5_small_v2,
        normalized: bool = True,
        download_if_needed: bool = False,
        max_batch_size: int = MAX_BATCH_SIZE,
    ):
        if not (
            path := (get_artifacts_dir() / "onnx" / model_name.split("/")[-1])
        ).exists():
            if download_if_needed:
                from .export_to_onnx import export

                logger.info("Could not find a local Onnx copy.")
                logger.info("Proceeding to download and convert to Onnx.")
                export(model_name_or_dir=model_name)
            else:
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
        tokenizer = _get_hf_tokenizer(str(path.resolve()))
        obj = cls(
            name=model_name,
            model=model,
            tokenizer=tokenizer,
            normalized=normalized,
            max_batch_size=max_batch_size,
        )
        obj._pretrained_name = model_name.value
        return obj

    def _mean_pool(self, h: np.ndarray, attn_mask: np.ndarray) -> np.ndarray:
        mask = attn_mask[..., None]
        emb = np.where(mask, h, 0.0).sum(axis=1) / (mask.sum(axis=1) + 1e-9)
        if self.normalized:
            emb /= np.linalg.norm(emb, axis=1, keepdims=True)
        return emb

    def _encode(self, texts: list[str]) -> list[list[float]]:
        assert isinstance(
            texts, list
        ), "Must pass list input. If just a string, make it a list of size 1."
        if len(texts) > self.max_batch_size:
            ids = range(0, len(texts), bsz := self.max_batch_size)
            return [x for i in ids for x in self._encode(texts[i : i + bsz])]
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
        # TODO: there is no real guardrail here for using a model that does not use this preprocessing
        # we can go back to separate classes, but there's only 2 models for now, and this seems ok.
        if isinstance(text, str):
            text = [text]
        assert all(isinstance(x, str) for x in text)
        if "e5" in getattr(self, "_pretrained_name", ""):
            text = [f"{EmbeddingType.query.value}: {x}" for x in text]
        return self._encode(text)

    def encode_passage(self, text: list[str]) -> list[list[float]]:
        if isinstance(text, str):
            text = [text]
        assert all(isinstance(x, str) for x in text)
        if "e5" in getattr(self, "_pretrained_name", ""):
            text = [f"{EmbeddingType.passage.value}: {x}" for x in text]
        return self._encode(text)

    def __repr__(self):
        if hasattr(self, "_pretrained_name"):
            return f"{self.__class__.__name__}(model={self._pretrained_name}, dimension={self.dimension})"
        return f"{self.__class__.__name__}(dimension={self.dimension})"


class CrossEncoder(EmbeddingModel):
    def __init__(
        self,
        model: transformers.PreTrainedModel,
        tokenizer: transformers.PreTrainedTokenizerBase,
        max_batch_size: int = MAX_BATCH_SIZE,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.max_tokens = self.model.config.max_position_embeddings
        self.dimension = self.model.config.hidden_size
        self.max_batch_size = max_batch_size

    @classmethod
    def _from_pretrained_transformers(cls, model_name: CrossEncoderEnum):
        raise ValueError("Bro, don't use this, it's gonna break")
        model = transformers.AutoModel.from_pretrained(model_name.value)
        tokenizer = _get_hf_tokenizer(model_name.value)
        obj = cls(model=model, tokenizer=tokenizer)
        obj._pretrained_name = model_name.value
        return obj

    @classmethod
    def default(cls):
        return cls.from_pretrained(CrossEncoderEnum.mmarco_mMiniLMv2_L12_H384_v1)

    @classmethod
    def from_pretrained(
        cls,
        model_name: CrossEncoderEnum = CrossEncoderEnum.mmarco_mMiniLMv2_L12_H384_v1,
        download_if_needed: bool = False,
    ):
        if not (
            path := (get_artifacts_dir() / "onnx" / model_name.split("/")[-1])
        ).exists():
            if download_if_needed:
                from .export_to_onnx import export

                logger.info("Could not find a local Onnx copy.")
                logger.info("Proceeding to download and convert to Onnx.")
                export(model_name_or_dir=model_name)
            else:
                raise FileNotFoundError(
                    (
                        f"Could not find local Onnx copy at {path.resolve()}."
                        " First export using clonr.embedding.export_to_onnx.py"
                    )
                )
        model = ORTModelForSequenceClassification.from_pretrained(
            model_id=str(path.resolve()),
            local_files_only=True,
        )
        tokenizer = _get_hf_tokenizer(str(path.resolve()))
        obj = cls(model=model, tokenizer=tokenizer)
        obj._pretrained_name = model_name.value
        return obj

    def similarity_score(
        self, query: str | list[str], passages: list[str]
    ) -> list[float]:
        """Higher is better"""
        if isinstance(query, str):
            query = [query] * len(passages)
        if len(passages) > self.max_batch_size:
            res: list[float] = []
            for i in range(0, len(passages), bsz := self.max_batch_size):
                res.extend(
                    self.similarity_score(query[i : i + bsz], passages[i : i + bsz])
                )
            return res
        features = self.tokenizer(
            query, passages, padding=True, truncation=True, return_tensors="np"
        )
        scores = self.model(**features).logits
        return scores.tolist()

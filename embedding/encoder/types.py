"""
For the most up-to-date models, see the current Sentence embedding benchmarks at:

https://huggingface.co/spaces/mteb/leaderboard
"""
from enum import Enum


class EmbeddingType(str, Enum):
    query: str = "query"
    passage: str = "passage"


class EmbeddingModelEnum(str, Enum):
    """Pretrained models. For more details see:
    https://huggingface.co/intfloat and
    https://huggingface.co/sentence-transformers

    These models discriminate between query embeddings and passage embeddings,
    by appropriately prefixing the text with "query" or "passage". These
    are the best ratio quality/latency as of 06/08/2023. They are Roberta-based
    English models, except for the multilingual which is XLM-Roberta based.

    E5 Dimensions:
        small => 384
        base => 768
        large => 1024
    SentenceTransformers Dimensions:
        minilm => 384
    """

    e5_small_v2: str = "intfloat/e5-small-v2"
    e5_base_v2: str = "intfloat/e5-base-v2"
    e5_large_v2: str = "intfloat/e5-large-v2"
    e5_multilingual_base: str = "intfloat/multilingual-e5-base"
    all_minilm_l6_v2: str = "sentence-transformers/all-MiniLM-L6-v2"
    all_minilm_l12_v2: str = "sentence-transformers/all-MiniLM-L12-v2"


class CrossEncoderEnum(str, Enum):
    """Cross Encoder models available from SentenceTransformers.
    the L_6 and L_12 miniLM versions have near identical performance,
    https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-12-v2
    but the latter is 2x slower, so we don't include it.

    mmarco is the multilingual version, and supports 14 languages,
    including arabic, chinese, and japanese.
    """

    ms_marco_MiniLM_L_6_v2: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    mmarco_mMiniLMv2_L12_H384_v1: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

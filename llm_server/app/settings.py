import multiprocessing
from typing import Optional

from pydantic import BaseSettings, Field

from app.utils import get_model_path


class Settings(BaseSettings):
    model: str = Field(
        description="The path to the model to use for generating completions.",
        default=get_model_path("Wizard-Vicuna-7B-Uncensored.ggmlv3.q4_0.bin"),
    )
    model_alias: Optional[str] = Field(
        default=None,
        description="The alias of the model to use for generating completions.",
    )
    n_ctx: int = Field(default=2048, ge=1, description="The context size.")
    n_gpu_layers: int = Field(
        default=0,
        ge=0,
        description="The number of layers to put on the GPU. The rest will be on the CPU.",
    )
    n_batch: int = Field(
        default=512, ge=1, description="The batch size to use per eval."
    )
    n_threads: int = Field(
        default=max(multiprocessing.cpu_count() // 2, 1),
        ge=1,
        description="The number of threads to use.",
    )
    f16_kv: bool = Field(default=True, description="Whether to use f16 key/value.")
    use_mlock: bool = Field(
        default=False,
        description="Use mlock.",
    )
    use_mmap: bool = Field(
        default=True,
        description="Use mmap.",
    )
    embedding: bool = Field(default=True, description="Whether to use embeddings.")
    last_n_tokens_size: int = Field(
        default=64,
        ge=0,
        description="Last n tokens to keep for repeat penalty calculation.",
    )
    logits_all: bool = Field(default=True, description="Whether to return logits.")
    cache: bool = Field(
        default=False,
        description="Use a cache to reduce processing times for evaluated prompts.",
    )
    cache_size: int = Field(
        default=2 << 30,
        description="The size of the cache in bytes. Only used if cache is True.",
    )
    vocab_only: bool = Field(
        default=False, description="Whether to only return the vocabulary."
    )
    verbose: bool = Field(
        default=True, description="Whether to print debug information."
    )
    PORT: int = 8080


settings = Settings()

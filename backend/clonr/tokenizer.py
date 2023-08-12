from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from pathlib import Path

import tiktoken

try:
    # Actually don't need transformers if running OpenAI,
    # since tiktoken is its own package
    from transformers import AutoTokenizer

    TRANSFORMERS_NOT_AVAILABLE = False
except ImportError:
    TRANSFORMERS_NOT_AVAILABLE = True

try:
    import llama_cpp

    LLAMA_CPP_AVAILABLE = True
except ImportError:
    import warnings

    warnings.warn("LlamaCpp not available.")
    LLAMA_CPP_AVAILABLE = False


# FixMe (Jonny): I had to copy/paste this to fix a circular import where
# the llms.__init__.py is causing the line
# from clonr.llms.schemas import OpenAIModelEnum to also import OpenAI, which
# has a circular dependency in that it imports the _get_tiktoken_tokenizer
# I don't want to move the enum out of llms and I want to be able to keep OpenAI in the
# __init__ so here we are...
class OpenAIModelEnum(str, Enum):
    chatgpt: str = "gpt-3.5-turbo"
    chatgpt_0301: str = "gpt-3.5-turbo-0301"
    chatgpt_0613: str = "gpt-3.5-turbo-0613"
    chatgpt_16k: str = "gpt-3.5-turbo-16k"
    gpt4: str = "gpt-4"
    gpt4_32k: str = "gpt-4-32k"
    gpt4_0314: str = "gpt-4-0314"
    gpt4_32k_0314: str = "gpt-4-32k-0314"


@lru_cache(maxsize=None)
def _get_tiktoken_tokenizer(model: str | OpenAIModelEnum):
    model = OpenAIModelEnum(model)
    try:
        # TODO: tiktoken is not yet updated to support the latest chatgpt
        if model.startswith("gpt-3.5"):
            tokenizer = tiktoken.encoding_for_model(model.chatgpt_0301)
        else:
            tokenizer = tiktoken.encoding_for_model(model.gpt4_0314)
    except KeyError:
        warnings.warn("Warning: model not found. Using cl100k_base encoding.")
        tokenizer = tiktoken.get_encoding("cl100k_base")
    return tokenizer


@lru_cache(maxsize=None)
def _get_llama_cpp_tokenizer(path: str | Path):
    if not LLAMA_CPP_AVAILABLE:
        raise ValueError("LlamaCpp is not installed.")
    if not Path(path).exists():
        raise FileNotFoundError("LlamaCpp ggml file not found.")
    return llama_cpp.LlamaTokenizer.from_ggml_file(path=path)


@lru_cache(maxsize=None)
def _get_hf_tokenizer(model_name_or_path: str, use_fast: bool):
    return AutoTokenizer.from_pretrained(model_name_or_path, use_fast=use_fast)


class Tokenizer(ABC):
    @abstractmethod
    def encode(self, text: str) -> list[int]:
        pass

    @abstractmethod
    def encode_batch(self, text: list[str]) -> list[list[int]]:
        pass

    @abstractmethod
    def decode(self, ids: list[int]) -> str:
        pass

    @abstractmethod
    def decode_batch(self, ids: list[list[int]]) -> list[str]:
        pass

    @classmethod
    def from_openai(cls, model: str | OpenAIModelEnum):
        return OpenAITokenizer(model=model)

    @classmethod
    def from_huggingface(cls, model: str):
        return HuggingFaceTokenizer(model=model)

    @classmethod
    def from_llama_cpp(cls, *args, **kwargs):
        raise NotImplementedError("Sorry, not gonna implement this one")

    def length(self, text: str):
        return len(self.encode(text))


class OpenAITokenizer(Tokenizer):
    def __init__(self, model: str | OpenAIModelEnum):
        model = OpenAIModelEnum(
            model
        )  # some cool nilpotency here, this is surprisingly ok
        self.model = model
        self.tokenizer = _get_tiktoken_tokenizer(model.value)

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text)

    def encode_batch(self, text: list[str]) -> list[list[int]]:
        return self.tokenizer.encode_batch(text)

    def decode(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids)

    def decode_batch(self, ids: list[list[int]]) -> list[str]:
        return self.tokenizer.decode_batch(ids)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"


class HuggingFaceTokenizer(Tokenizer):
    def __init__(self, model, use_fast: bool = True):
        if TRANSFORMERS_NOT_AVAILABLE:
            raise ImportError("`transformers` package not installed.")
        self.model = model
        self.tokenizer = _get_hf_tokenizer(model, use_fast=use_fast)

    def encode(self, text):
        return self.tokenizer.encode(text)

    def encode_batch(self, text: list[str]) -> list[list[int]]:
        return self.tokenizer(text)["input_ids"]

    def decode(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids)

    def decode_batch(self, ids: list[list[int]]) -> list[str]:
        # https://github.com/huggingface/transformers/issues/10019
        # homie says they can't go faster. sounds like a load of shit but whatever.
        return [self.tokenizer.decode(x) for x in ids]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"

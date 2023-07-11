import os
from dataclasses import dataclass

import aiohttp
import requests
from loguru import logger

from .callbacks import LLMCallback
from .openai import OpenAI
from .schemas import Message

try:
    import guidance
    import llama_cpp
    import torch
    from transformers import LlamaTokenizer

    LLAMA_CPP_IS_AVAILABLE = True
except Exception as e:
    logger.exception(f"LlamaCpp guidance is not available {e}")
    LLAMA_CPP_IS_AVAILABLE = False


class LlamaCpp(OpenAI):
    model_type = "llama-cpp"
    model = "llama-cpp"
    is_chat_model: bool = False

    def __init__(
        self,
        api_key: str = "",
        api_base: str = "http://localhost:6000/v1",
        chat_mode: bool = False,
        callbacks: list[LLMCallback] | None = None,
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.chat_mode = chat_mode
        self.callbacks = callbacks or []

    @property
    def user_start(self):
        return "### User:\n"

    @property
    def user_end(self):
        return ""

    @property
    def assistant_start(self):
        return "### Assistant:\n"

    @property
    def assistant_end(self):
        return self.user_end

    @property
    def system_start(self):
        return "### System:\n"

    @property
    def system_end(self):
        return self.user_end

    @property
    def default_system_prompt(self):
        return "Below is chat between a user and a helpful AI assistant. Write a response that appropriately completes the request."

    @property
    def context_length(self) -> int:
        return 2048  # llama context window

    def prompt_to_messages(self, prompt: str):
        # We just directly pass the prompt, and assume that the headers and stuff were taken care of
        # during templating (the role things above should fill in)
        return [Message(role="user", content=prompt)]

    async def anum_tokens(self, prompt: str):
        route = os.path.join(self.api_base, "tokens")
        async with aiohttp.ClientSession() as session:
            async with session.post(route, data={"prompt": prompt}) as resp:
                r = await resp.json()
        return int(r["num_tokens"])

    def num_tokens(self, prompt: str):
        route = os.path.join(self.api_base, "tokens")
        r = requests.post(route, json={"prompt": prompt})
        return int(r.json()["num_tokens"])


@dataclass
class _InnerModelConfig:
    vocab_size: int
    max_sequence_length: int
    pad_token_id: int | None


class _InnerModel(llama_cpp.Llama):
    def to(self):
        return self

    @property
    def device(self):
        return None

    @property
    def config(self):
        return _InnerModelConfig(
            vocab_size=llama_cpp.llama_n_vocab(self.ctx),
            max_sequence_length=self.params.n_ctx,
            pad_token_id=None,
        )

    def generate(self, inputs, **kwargs):
        kwargs["inputs"] = inputs
        gen = super().generate(
            tokens=inputs[0],
            temp=kwargs["temperature"],
            top_p=kwargs["top_p"],
            logits_processor=kwargs["logits_processor"],
            stopping_criteria=kwargs["stopping_criteria"],
        )
        d = {"sequences": [], "scores": []}
        if streamer := kwargs.get("streamer"):
            streamer.put({"sequences": inputs})
        for i, token in enumerate(gen):
            d["sequences"].append(token)
            d["scores"].append(self.eval_logits[-1])
            if streamer:
                streamer.put(
                    {k: torch.tensor(v[-1:]).reshape(1, -1) for k, v in d.items()}
                )
            if i > kwargs["max_new_tokens"]:
                break
        if streamer:
            streamer.end()
        return {
            "sequences": torch.tensor(d["sequences"]),
            "scores": torch.tensor(d["scores"])[None],
        }


class LlamaCppGuidanceLLM(guidance.llms._transformers.Transformers):
    def __init__(self, model, tokenizer=None, **kwargs):
        tokenizer = LlamaTokenizer.from_pretrained(
            tokenizer or "openlm-research/open_llama_7b"
        )
        return super().__init__(
            model=model,
            tokenizer=tokenizer,
            acceleration=False,
            caching=False,
            **kwargs,
        )

    @property
    def default_system_prompt(self):
        return "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n"

    def role_start(self, role):
        return dict(
            user="### User:\n",
            assistant="### Assistant:\n",
            system="### System:\n",
        )[role]

    def role_end(self, role):
        return "\n"

import os

import aiohttp
import requests

from .callbacks import LLMCallback
from .openai import OpenAI
from .schemas import Message


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
        return (
            "Below is chat between a user and a helpful AI assistant. "
            "Write a response that appropriately completes the request."
        )

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

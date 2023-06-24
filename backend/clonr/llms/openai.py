import asyncio
import re
import textwrap
import time
import warnings
from enum import Enum
from typing import AsyncGenerator, Generator

import aiohttp
import openai
import tiktoken
from pydantic import BaseModel, Field
from tenacity import retry, retry_if_exception_type, wait_random

from app.settings import settings

from .base import LLM, FinishReason, LLMResponse

openai.api_key = settings.OPENAI_API_KEY


class OpenAIModelEnum(str, Enum):
    chatgpt: str = "gpt-3.5-turbo"
    chatgpt_0301: str = "gpt-3.5-turbo-0301"
    chatgpt_0613: str = "gpt-3.5-turbo-0613"
    chatgpt_16k: str = "gpt-3.5-turbo-16k"
    gpt4: str = "gpt-4"
    gpt4_32k: str = "gpt-4-32k"
    gpt4_0314: str = "gpt-4-0314"
    gpt4_32k_0314: str = "gpt-4-32k-0314"


# JSON stuff
# ChatCompletion Schemas
class RoleEnum(str, Enum):
    system: str = "system"
    user: str = "user"
    assistant: str = "assistant"


class OpenAIUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIMessage(BaseModel):
    role: RoleEnum
    content: str


class OpenAIChoice(BaseModel):
    message: OpenAIMessage
    finish_reason: str
    index: int


class OpenAIResponse(BaseModel):
    model: str
    created: int
    usage: OpenAIUsage
    choices: list[OpenAIChoice]


class OpenAIStreamDelta(BaseModel):
    role: str | None = None
    content: str | None = None


class OpenAIStreamChoice(BaseModel):
    delta: OpenAIStreamDelta
    finish_reason: FinishReason | None
    index: int | None = None


class OpenAIStreamResponse(BaseModel):
    created: int
    model: str
    choices: list[OpenAIStreamChoice]


class OpenAIGenerationParams(BaseModel):
    temperature: float = Field(default=1.0, ge=0.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    n: int = Field(
        default=1,
        ge=1,
        le=1,
    )
    stop: str | list[str] | None = None
    max_tokens: int | None = Field(default=None, ge=1)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: dict[int, int] | None = None


class OpenAIChatCompletionRequest(OpenAIGenerationParams):
    model: str
    messages: list[OpenAIMessage]
    stream: bool


class NotebookStreamResponse(BaseModel):
    completion: str
    time: float
    tokens_per_second: float
    input_tokens: int
    completion_tokens: int
    total_tokens: int
    responses: list[OpenAIStreamResponse]

    def __repr__(self):
        s = self.completion
        if len(s) > 20:
            s = s[:20] + f" + {len(s) - 120} chars ... "
        return textwrap.dedent(
            f"""
        Response(
            completion={s}, 
            time={self.time:.02f}s, 
            speed={self.tokens_per_second:.02f} tokens/second, 
            completion_tokens={self.completion_tokens}, 
            input_tokens={self.input_tokens}, 
            total_tokens={self.total_tokens}
        )"""
        )


class OpenAI(LLM):
    model_type: str = "openai"

    def __init__(
        self,
        model: OpenAIModelEnum = OpenAIModelEnum.chatgpt_0613,
        api_key: str = settings.OPENAI_API_KEY,
        api_base: str | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        try:
            # TODO: tiktoken is not yet updated to support the latest chatgpt
            if model.startswith("gpt-3.5"):
                self.tokenizer = tiktoken.encoding_for_model(model.chatgpt_0301)
            else:
                self.tokenizer = tiktoken.encoding_for_model(model.gpt4_0314)
        except KeyError:
            warnings.warn("Warning: model not found. Using cl100k_base encoding.")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    @property
    def user_start(self):
        return "<|im_start|>user\n"

    @property
    def user_end(self):
        return "<|im_end|>"

    @property
    def assistant_start(self):
        return "<|im_start|>assistant\n"

    @property
    def assistant_end(self):
        return self.user_end

    @property
    def system_start(self):
        return "<|im_start|>system\n"

    @property
    def system_end(self):
        return self.user_end

    @property
    def default_system_prompt(self):
        return "You are a helpful assistant."

    def _num_tokens_from_messages(self, messages: list[OpenAIMessage]) -> int:
        """Taken from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        Returns the number of tokens used by a list of messages."""
        if self.model.startswith("gpt-3.5"):
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif self.model.startswith("gpt-4"):
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                "num_tokens_from_messages() is not implemented for "
                f"model {self.model}. See "
                "https://github.com/openai/openai-python/blob/main/chatml.md"
                " for information on how messages are converted to tokens."
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.dict().items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def _num_tokens_from_string(self, value: str):
        return len(self.tokenizer.encode(value))

    def num_tokens(self, inp: list[OpenAIMessage] | str):
        if isinstance(inp, str):
            return self._num_tokens_from_string(inp)
        return self._num_tokens_from_messages(inp)

    def prompt_to_messages(self, prompt: str):
        messages = []

        # if not prompt.rstrip().endswith(self.assistant_start):
        #     msg = (
        #         "When calling OpenAI chat models you must generate only directly"
        #         " inside the assistant role! The OpenAI API does not currently"
        #         " support partial assistant prompting."
        #     )
        #     raise ValueError(msg)

        pattern = r"<\|im_start\|>(\w+)(.*?)(?=<\|im_end\|>|$)"
        matches = re.findall(pattern, prompt, re.DOTALL)

        if not matches:
            return [{"role": "user", "content": prompt.strip()}]

        for match in matches:
            role, content = match
            content = content.strip()  # should we do this?
            messages.append({"role": role, "content": content})

        return [OpenAIMessage(**m) for m in messages]

    @retry(
        retry=retry_if_exception_type(openai.error.RateLimitError),
        wait=wait_random(min=0.1, max=2),
    )
    async def agenerate(
        self,
        prompt_or_messages: str | list[OpenAIMessage],
        params: OpenAIGenerationParams | None = None,
    ) -> LLMResponse:
        params = params or OpenAIGenerationParams()
        if isinstance(prompt_or_messages, str):
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            messages = prompt_or_messages
        request = OpenAIChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=False,
            **params.dict(exclude_unset=True),
        )
        async with aiohttp.ClientSession() as sess:
            openai.aiosession.set(sess)
            try:
                r = await openai.ChatCompletion.acreate(
                    **request.dict(exclude_unset=True),
                    api_key=self.api_key,
                    api_base=self.api_base,
                )
            finally:
                await openai.aiosession.get().close()  # type: ignore
        out = OpenAIResponse(**r)
        response = LLMResponse(
            content=out.choices[0].message.content,
            model_type=self.model_type,
            model_name=out.model,
            created_at=out.created,
            tokens_prompt=out.usage.prompt_tokens,
            tokens_completion=out.usage.completion_tokens,
            tokens_total=out.usage.total_tokens,
            finish_reason=out.choices[0].finish_reason,
            role=out.choices[0].message.role,
        )
        return response

    def generate(
        self,
        prompt_or_messages: str | list[OpenAIMessage],
        params: OpenAIGenerationParams | None = None,
    ) -> LLMResponse:
        return asyncio.get_event_loop().run_until_complete(
            self.agenerate(prompt_or_messages=prompt_or_messages, params=params)
        )

    @retry(
        retry=retry_if_exception_type(openai.error.RateLimitError),
        wait=wait_random(min=0.1, max=2),
    )
    async def astream(
        self,
        prompt_or_messages: str | list[OpenAIMessage],
        params: OpenAIGenerationParams | None = None,
    ) -> AsyncGenerator[OpenAIStreamDelta, None]:
        params = params or OpenAIGenerationParams()
        if isinstance(prompt_or_messages, str):
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            messages = prompt_or_messages
        request = OpenAIChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=True,
            **params.dict(exclude_unset=True),
        )
        async with aiohttp.ClientSession() as sess:
            openai.aiosession.set(sess)
            try:
                chunks = await openai.ChatCompletion.acreate(
                    **request.dict(exclude_unset=True),
                    api_key=self.api_key,
                    api_base=self.api_base,
                )
                async for chunk in chunks:
                    delta = OpenAIStreamResponse(**chunk)
                    yield delta
            finally:
                await openai.aiosession.get().close()  # type: ignore

    @retry(
        retry=retry_if_exception_type(openai.error.RateLimitError),
        wait=wait_random(min=0.1, max=2),
    )
    def stream(
        self,
        prompt_or_messages: str | list[OpenAIMessage],
        params: OpenAIGenerationParams | None = None,
    ) -> Generator[OpenAIStreamDelta, None, None]:
        params = params or OpenAIGenerationParams()
        if isinstance(prompt_or_messages, str):
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            messages = prompt_or_messages
        request = OpenAIChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=True,
            **params.dict(exclude_unset=True),
        )
        chunks = openai.ChatCompletion.create(
            **request.dict(exclude_unset=True),
            api_key=self.api_key,
            api_base=self.api_base,
        )
        for chunk in chunks:
            delta = OpenAIStreamResponse(**chunk)
            yield delta

    async def notebook_stream(
        self,
        prompt_or_messages: str | list[OpenAIMessage],
        params: OpenAIGenerationParams | None = None,
        width: int = 70,
    ) -> NotebookStreamResponse:
        from IPython import display

        r = []
        text = ""
        start_time = time.time()
        input_tokens = self.num_tokens(prompt_or_messages)
        completion_tokens = 0
        async for x in self.astream(
            prompt_or_messages=prompt_or_messages, params=params
        ):
            text += x.choices[0].delta.content
            _text = "\n".join(textwrap.wrap(text, width=width))
            display.clear_output(wait=False)
            print(_text, flush=True)
            r.append(x)
            completion_tokens += 1
        total_time = time.time() - start_time
        total_tokens = input_tokens + completion_tokens
        tokens_per_second = total_tokens / (total_time + 1e-3)

        return NotebookStreamResponse(
            completion=text,
            time=total_time,
            tokens_per_second=tokens_per_second,
            input_tokens=input_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            responses=r,
        )

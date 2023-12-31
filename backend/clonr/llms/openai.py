import asyncio
import textwrap
import time
import uuid
from functools import wraps
from typing import AsyncGenerator, Callable, Generator

import aiohttp
import openai
from fastapi import status
from fastapi.exceptions import HTTPException
from loguru import logger
from opentelemetry import metrics
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.settings import settings
from clonr._grammar import parse_prompt
from clonr.tokenizer import Tokenizer

from .base import LLM
from .callbacks import LLMCallback
from .schemas import (
    ChatCompletionRequest,
    FinishReason,
    GenerationParams,
    LLMResponse,
    Message,
    NotebookStreamResponse,
    OpenAIModelEnum,
    OpenAIResponse,
    OpenAIStreamResponse,
)

meter = metrics.get_meter(settings.BACKEND_APP_NAME)

exc_meter = meter.create_counter(
    name="llm_exceptions_total",
    description="Total count of exceptions raised by path and exception type",
)
reqs_in_progress_meter = meter.create_up_down_counter(
    name="llm_requests_in_progress",
    description="OpenAI or other LLM requests currently in progress",
)


def retry_decorator(fn: Callable):
    @retry(
        retry=retry_if_exception_type(
            (
                openai.error.RateLimitError,
                openai.error.APIConnectionError,
                openai.error.ServiceUnavailableError,
                openai.error.APIError,
                openai.error.Timeout,
            )
        ),
        wait=wait_exponential(min=1, max=3),
        stop=stop_after_attempt(2),
    )
    def original(self, *args, **kwargs):
        return fn(self, *args, **kwargs)

    @wraps(original)
    def wrapped(self, *args, **kwargs):
        attributes = dict(model=self.model, model_type=self.model_type)
        try:
            reqs_in_progress_meter.add(amount=1, attributes=attributes)
            return original(self, *args, **kwargs)
        except RetryError as e:
            try:
                e.reraise()
            except openai.error.Timeout as e2:
                logger.error(e2)
                exception_type = type(e2).__name__
                exc_meter.add(
                    amount=1, attributes={**attributes, exception_type: exception_type}
                )
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out",
                )
            except openai.error.RateLimitError as e2:
                logger.error(e2)
                exc_meter.add(
                    amount=1, attributes={**attributes, exception_type: exception_type}
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Servers are currently overloaded. Please try again later.",
                )
            except Exception as e2:
                logger.error(e2)
                exc_meter.add(
                    amount=1, attributes={**attributes, exception_type: exception_type}
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error",
                )
            finally:
                reqs_in_progress_meter.add(amount=-1, attributes=attributes)

    return wrapped


class OpenAI(LLM):
    model_type: str = "openai"
    is_chat_model: bool = True

    def __init__(
        self,
        model: OpenAIModelEnum = OpenAIModelEnum.chatgpt,
        api_key: str = "",
        api_base: str | None = None,
        tokenizer: Tokenizer | None = None,
        callbacks: list[LLMCallback] | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.tokenizer = tokenizer or Tokenizer.from_openai(model)
        self.callbacks = callbacks or []

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

    @property
    def context_length(self) -> int:
        match self.model:
            case OpenAIModelEnum.chatgpt:
                return 4096
            case OpenAIModelEnum.chatgpt_16k:
                return 16_384
            case OpenAIModelEnum.gpt4:
                return 8192
            case OpenAIModelEnum.gpt4_32k:
                return 32_768
            case _:
                raise TypeError(self.model)

    def _num_tokens_from_messages(self, messages: list[Message]) -> int:
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
            for key, value in message.model_dump().items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def _num_tokens_from_string(self, value: str) -> int:
        return len(self.tokenizer.encode(value))

    def num_tokens(self, inp: list[Message] | str) -> int:
        if isinstance(inp, str):
            return self._num_tokens_from_string(inp)
        return self._num_tokens_from_messages(inp)

    @classmethod
    def prompt_to_messages(cls, prompt: str) -> list[Message]:
        message_dicts = parse_prompt(prompt=prompt)
        messages = [
            Message(role=x["role"], content=x["content"]) for x in message_dicts
        ]
        return messages

    @classmethod
    def messages_to_prompt(cls, messages: list[Message]) -> str:
        return "\n".join(m.to_prompt(cls) for m in messages)

    @retry_decorator
    async def agenerate(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
        **kwargs,
    ) -> LLMResponse:
        params = params or GenerationParams()
        # NOTE (Jonny): This will be picked up callbacks, and it serves to place a unique ID on each
        # LLM call so that we can go back and trace it through logs (defends against async messing up order)
        kwargs["id"] = kwargs.get("id", str(uuid.uuid4()))
        kwargs["http_retry_attempt"] = (
            self.agenerate.retry.statistics["attempt_number"] - 1
        )

        for c in self.callbacks:
            await c.on_generate_start(self, prompt_or_messages, params, **kwargs)

        if isinstance(prompt_or_messages, str):
            input_prompt = prompt_or_messages
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            input_prompt = self.messages_to_prompt(prompt_or_messages)
            messages = prompt_or_messages
        request = ChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=False,
            **params.model_dump(exclude_unset=True),
        )

        start_time = time.time()
        async with aiohttp.ClientSession() as sess:
            openai.aiosession.set(sess)
            try:
                r = await openai.ChatCompletion.acreate(
                    **request.model_dump(exclude_unset=True),
                    api_key=self.api_key,
                    api_base=self.api_base,
                )
            finally:
                await openai.aiosession.get().close()  # type: ignore
        total_time = 1e-7 + time.time() - start_time

        out = OpenAIResponse(**r)
        response = LLMResponse(
            content=out.choices[0].message.content,
            model_type=self.model_type,
            model_name=out.model,
            created_at=out.created,
            usage=out.usage,
            duration=round(total_time, 3),
            finish_reason=FinishReason(out.choices[0].finish_reason),
            role=out.choices[0].message.role,
            tokens_per_second=round((out.usage.total_tokens) / total_time, 2),
            input_prompt=input_prompt,
        )

        for c in self.callbacks:
            await c.on_generate_end(self, response, **kwargs)

        return response

    def generate(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
    ) -> LLMResponse:
        return asyncio.get_event_loop().run_until_complete(
            self.agenerate(prompt_or_messages=prompt_or_messages, params=params)
        )

    @retry_decorator
    async def astream(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
        **kwargs,
    ) -> AsyncGenerator[OpenAIStreamResponse, None]:
        params = params or GenerationParams()

        for c in self.callbacks:
            await c.on_stream_start(self, prompt_or_messages, params, **kwargs)

        if isinstance(prompt_or_messages, str):
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            messages = prompt_or_messages
        request = ChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=True,
            **params.model_dump(exclude_unset=True),
        )
        async with aiohttp.ClientSession() as sess:
            openai.aiosession.set(sess)
            try:
                chunks = await openai.ChatCompletion.acreate(
                    **request.model_dump(exclude_unset=True),
                    api_key=self.api_key,
                    api_base=self.api_base,
                )
                async for chunk in chunks:
                    delta = OpenAIStreamResponse(**chunk)

                    for c in self.callbacks:
                        await c.on_token_received(self, delta=delta, **kwargs)

                    yield delta
            finally:
                await openai.aiosession.get().close()  # type: ignore

        for c in self.callbacks:
            await c.on_stream_end(self, **kwargs)

    @retry_decorator
    def stream(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
    ) -> Generator[OpenAIStreamResponse, None, None]:
        params = params or GenerationParams()
        if isinstance(prompt_or_messages, str):
            messages = self.prompt_to_messages(prompt=prompt_or_messages)
        else:
            messages = prompt_or_messages
        request = ChatCompletionRequest(
            model=self.model,
            messages=messages,
            stream=True,
            **params.model_dump(exclude_unset=True),
        )
        chunks = openai.ChatCompletion.create(
            **request.model_dump(exclude_unset=True),
            api_key=self.api_key,
            api_base=self.api_base,
        )
        for chunk in chunks:
            delta = OpenAIStreamResponse(**chunk)
            yield delta

    async def notebook_stream(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
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
            duration=total_time,
            tokens_per_second=tokens_per_second,
            input_tokens=input_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            responses=r,
        )

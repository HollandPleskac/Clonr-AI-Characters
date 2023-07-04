import textwrap
import time

from clonr.tokenizer import Tokenizer

from .openai import OpenAI, OpenAIModelEnum, OpenAIStreamResponse
from .schemas import FinishReason, GenerationParams, LLMResponse, Message


class MockLLM(OpenAI):
    model_type: str = "mock"
    _counter: int = 0
    chat_model: bool = True

    def __init__(self, response: str = "mock response"):
        self.response = response
        self.tokenizer = Tokenizer.from_openai("gpt-3.5-turbo")

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
        return 4000

    async def agenerate(self, *args, **kwargs) -> LLMResponse:
        return self.generate(*args, **kwargs)

    def generate(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
    ) -> LLMResponse:
        self._counter += 1
        st = time.time()
        content = self.response
        content = self.tokenizer.decode(
            self.tokenizer.encode(content)[: params.max_tokens]
        )
        prompt = prompt_or_messages
        if not isinstance(prompt, str):
            prompt = " ".join([x["content"] for x in prompt])
        prompt_tokens = self.tokenizer.length(prompt)
        completion_tokens = self.tokenizer.length(content)
        total_tokens = prompt_tokens + completion_tokens
        return LLMResponse(
            content=content,
            model_type=self.model_type,
            model_name="MockModel",
            created_at=round(time.time()),
            usage={
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "prompt_tokens": prompt_tokens,
            },
            finish_reason="length",
            role="assistant",
            time=1 + time.time() - st,
        )

    async def astream(self, *args, **kwargs) -> LLMResponse:
        for x in self.stream():
            yield x

    def stream(self, *args, **kwargs) -> LLMResponse:
        self._counter += 1
        for ch in "ABC":
            yield OpenAIStreamResponse(
                created=round(time.time()),
                model="MockModel",
                choices=[
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": f" ResponseToken{self._counter}{ch}",
                            "finish_reason": FinishReason.length if ch == "C" else None,
                        },
                    }
                ],
            )

    async def notebook_stream(
        self, *args, **kwargs
    ) -> tuple[list[OpenAIStreamResponse], str]:
        from IPython import display

        r = []
        text = ""
        async for x in self.astream():
            text += x.choices[0].delta.content
            _text = "\n".join(textwrap.wrap(text, width=70))
            display.clear_output(wait=False)
            print(_text, flush=True)
            r.append(x)
        return r, text

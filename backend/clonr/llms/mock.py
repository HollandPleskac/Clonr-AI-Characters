import textwrap
import time

from .base import LLMResponse, LLM, FinishReason
from .openai import OpenAIStreamResponse, OpenAI


class MockLLM(OpenAI):
    model_type: str = "mock"
    _counter: int = 0

    def __init__(self):
        pass

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

    async def agenerate(self, *args, **kwargs) -> LLMResponse:
        return self.generate()

    def generate(self, *args, **kwargs) -> LLMResponse:
        self._counter += 1
        content = f"Mock response {self._counter}"
        return LLMResponse(
            content=content,
            model_type=self.model_type,
            model_name="MockModel",
            created_at=round(time.time()),
            tokens_prompt=3,
            tokens_completion=2,
            tokens_total=5,
            finish_reason="length",
            role="assistant",
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
                            "content": f"ResponseToken{self._counter}{ch}",
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

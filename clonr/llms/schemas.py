import textwrap
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol

from pydantic import BaseModel, Field, validator


class OpenAIModelEnum(str, Enum):
    chatgpt: str = "gpt-3.5-turbo"
    chatgpt_0301: str = "gpt-3.5-turbo-0301"
    chatgpt_0613: str = "gpt-3.5-turbo-0613"
    chatgpt_16k: str = "gpt-3.5-turbo-16k"
    gpt4: str = "gpt-4"
    gpt4_32k: str = "gpt-4-32k"
    gpt4_0314: str = "gpt-4-0314"
    gpt4_32k_0314: str = "gpt-4-32k-0314"


class FinishReason(str, Enum):
    stop: str = "stop"
    length: str = "length"
    content_filter: str = "content_filter"
    null: str | None = "null"


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


# JSON stuff
# ChatCompletion Schemas
class RoleEnum(str, Enum):
    system: str = "system"
    user: str = "user"
    assistant: str = "assistant"


class Message(BaseModel):
    role: RoleEnum
    content: str

    def to_prompt(self, llm):
        match self.role:
            case RoleEnum.system:
                start = llm.system_start
                end = llm.system_end
            case RoleEnum.user:
                start = llm.user_start
                end = llm.user_end
            case RoleEnum.assistant:
                start = llm.assistant_start
                end = llm.assistant_end
        return f"{start}{self.content}{end}"


class Choice(BaseModel):
    message: Message
    finish_reason: str
    index: int


class OpenAIResponse(BaseModel):
    model: str
    created: int
    usage: Usage
    choices: list[Choice]


class StreamDelta(BaseModel):
    role: str | None = None
    content: str | None = None


class StreamChoice(BaseModel):
    delta: StreamDelta
    finish_reason: FinishReason | None
    index: int | None = None


class OpenAIStreamResponse(BaseModel):
    created: int
    model: str
    choices: list[StreamChoice]


class GenerationParams(BaseModel):
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


class ChatCompletionRequest(GenerationParams):
    model: str
    messages: list[Message]
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


class LLMResponse(BaseModel):
    content: str
    model_type: str
    model_name: str
    created_at: int
    usage: Usage
    time: float
    finish_reason: FinishReason | None = None
    role: str | None = None
    tokens_per_second: float | None = None

    @validator("tokens_per_second", always=True)
    def compute_tok_per_sec(cls, v, values):
        if v is not None:
            return v
        return round((values["usage"].total_tokens) / values["time"], 2)

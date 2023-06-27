from abc import ABC, abstractproperty
from enum import Enum

from pydantic import BaseModel


class LLM(ABC):
    @abstractproperty
    def user_start(self):
        pass

    @abstractproperty
    def user_end(self):
        pass

    @abstractproperty
    def assistant_start(self):
        pass

    @abstractproperty
    def assistant_end(self):
        pass

    @abstractproperty
    def system_start(self):
        pass

    @abstractproperty
    def system_end(self):
        pass

    @abstractproperty
    def default_system_prompt(self):
        pass


class FinishReason(str, Enum):
    stop: str = "stop"
    length: str = "length"
    content_filter: str = "content_filter"
    null: str | None = "null"


class LLMResponse(BaseModel):
    content: str
    model_type: str
    model_name: str
    created_at: int
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    finish_reason: FinishReason | None = None
    role: str | None = None

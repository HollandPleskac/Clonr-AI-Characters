from abc import ABC, abstractproperty, abstractmethod
from .schemas import Message, GenerationParams, LLMResponse


class LLM(ABC):
    is_chat_model: bool
    model: str
    model_type: str

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

    @abstractproperty
    def context_length(self) -> int:
        pass

    @abstractmethod
    async def agenerate(
        self,
        prompt_or_messages: str | list[Message],
        params: GenerationParams | None = None,
        **kwargs,
    ) -> LLMResponse:
        pass

    @abstractmethod
    def num_tokens(self, inp: list[Message] | str) -> int:
        pass

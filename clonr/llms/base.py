from abc import ABC, abstractproperty


class LLM(ABC):
    is_chat_model: bool

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

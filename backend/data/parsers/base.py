from abc import ABC, abstractmethod

from data.core.document import Document


class ParserException(Exception):
    pass


class Parser(ABC):
    @abstractmethod
    def extract(self, *args, **kwargs) -> Document | list[Document]:
        pass

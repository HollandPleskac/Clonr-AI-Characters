from abc import ABC, abstractmethod

from clonr.data_structures import Document


class ParserException(Exception):
    pass


class Parser(ABC):
    @abstractmethod
    def extract(self, *args, **kwargs) -> Document | list[Document]:
        pass

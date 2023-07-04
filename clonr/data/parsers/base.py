from abc import ABC, abstractmethod

from clonr.data.data_structures import Document


class ParserException(Exception):
    pass


class Parser(ABC):
    def extract(self, *args, **kwargs) -> Document | list[Document]:
        return self._extract(*args, **kwargs)

from abc import ABC, abstractmethod

from clonr.data_structures import Document


class ParserException(Exception):
    pass


class Parser(ABC):
    def extract(self, *args, **kwargs) -> Document | list[Document]:
        return self._extract(*args, **kwargs)


# TODO (Jonny): add web crawlers using trafilatura return_links=True to parse a website.
# TODO (Jonny): make the web stuff async. not sure if it matters too much overall though.
# TODO (Jonny): caching on web requests with redis and a TTL to prevent throttling?

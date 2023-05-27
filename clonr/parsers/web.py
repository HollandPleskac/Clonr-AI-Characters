try:
    import trafilatura  # noqa: F401
except ImportError:
    raise ImportError(
        "`trafilatura` package not found, please run `pip install trafilatura`"
    )
from loguru import logger

from clonr.data_structures import Document

from .base import Parser, ParserException


class BasicWebParser(Parser):
    def extract(self, urls: str | list[str]) -> Document | list[Document]:
        if not isinstance(urls, list):
            return self.extract([urls])[0]
        documents = []
        for url in urls:
            logger.info(f"Fetching from url: {url}")
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                if self.error_on_missing:
                    raise ParserException(f"Failed to get string from url: {url}")
                continue
            response = trafilatura.extract(downloaded)
            if not response:
                if self.error_on_missing:
                    raise ParserException(f"Failed to parse page: {url}")
                continue
            documents.append(Document(content=response))
        return documents

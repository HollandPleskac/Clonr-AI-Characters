try:
    import trafilatura  # noqa: F401
except ImportError:
    raise ImportError(
        "`trafilatura` package not found, please run `pip install trafilatura`"
    )
from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache


class BasicWebParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def extract(self, url: str) -> Document:
        logger.info(f"Fetching from url: {url}")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ParserException(f"Failed to get string from url: {url}")
        response = trafilatura.extract(downloaded)
        if not response:
            raise ParserException(f"Failed to parse page: {url}")
        return Document(content=response)

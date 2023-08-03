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
    def extract(self, url: str, type: str = "web") -> Document:
        logger.info(f"Attempting to parse text from url: {url}")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            msg = f"Failed to get string from url: {url}"
            logger.error(msg)
            raise ParserException(msg)
        if not (response := trafilatura.extract(downloaded)):
            msg = f"Failed to parse page: {url}"
            logger.error(msg)
            raise ParserException(msg)
        logger.info("✅ Extracted from url.")
        return Document(content=response, url=url, type=type)

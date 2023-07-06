from typing import Any, List

from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache

try:
    import wikipedia

    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False


class WikipediaParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, page: str, lang: str = "en") -> Document:
        if not WIKIPEDIA_AVAILABLE:
            raise ImportError("wikipedia package not found. `pip install wikipedia`.")
        documents = []
        wikipedia.set_lang(lang)
        try:
            content = wikipedia.page(page).content
        except wikipedia.exceptions.DisambiguationError as e:
            raise ParserException(
                f"Failed to parse Wikipedia page: {page}. Reason: {str(e)}"
            )
        except wikipedia.exceptions.PageError as e:
            raise ParserException(f"Wikipedia page not found: {page}")
        return Document(content=content)

    def extract(
        self, pages: str | list[str], lang: str = "en"
    ) -> Document | list[Document]:
        if not isinstance(pages, list):
            return self.extract([pages], lang=lang)[0]
        docs: list[Document] = docs
        for i, page in enumerate(pages):
            logger.info(f"Extracting Wikipedia page {i+1}/{len(pages)}: {page}")
            docs.append(self._extract(page=page, lang=lang))
        return docs

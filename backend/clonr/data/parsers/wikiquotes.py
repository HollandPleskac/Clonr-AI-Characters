from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache

try:
    import wikiquote

    WIKIQUOTE_AVAILABLE = True
except ImportError:
    WIKIQUOTE_AVAILABLE = False


class WikiQuotesParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, character_name: str):
        if not WIKIQUOTE_AVAILABLE:
            raise ImportError("wikiquote package not found. `pip install wikiquote`.")
        try:
            quotes = wikiquote.quotes(character_name, max_quotes=10)
        except (
            wikiquote.utils.DisambiguationPageException,
            wikiquote.utils.NoSuchPageException,
        ):
            raise ParserException(f"No results found for {character_name}.")

        unique_quotes = list(dict.fromkeys(quotes))
        return Document(content="\n\n".join(unique_quotes))

    def extract(self, character_name: str):
        logger.info(
            f"Attempting to extract Wikiquotes, character_name: {character_name}"
        )
        r = self._extract(character_name)
        logger.info("✅ Extracted for character name.")
        return r

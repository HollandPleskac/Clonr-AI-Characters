from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Monologue
from clonr.text_splitters import SentenceSplitterChars
from clonr.utils.shared import instance_level_lru_cache

try:
    import wikiquote

    WIKIQUOTE_AVAILABLE = True
except ImportError:
    WIKIQUOTE_AVAILABLE = False

# this is by character size
SPLITTER = SentenceSplitterChars(max_chunk_size=256, chunk_overlap=0, min_chunk_size=32)


# TODO (Jonny): add a text-splitter to downsize big quotes. splitting in non-english is tough
# so just check the limit then language?
class WikiQuotesParser(Parser):
    @instance_level_lru_cache(maxsize=None)
    def _extract(self, character_name: str, max_quotes: int) -> list[Monologue]:
        if not WIKIQUOTE_AVAILABLE:
            raise ImportError("wikiquote package not found. `pip install wikiquote`.")
        try:
            raw_quotes: list[str] = wikiquote.quotes(
                character_name, max_quotes=max_quotes
            )
        except (
            wikiquote.utils.DisambiguationPageException,
            wikiquote.utils.NoSuchPageException,
        ):
            raise ParserException(f"No results found for {character_name}.")

        unique_quotes = list(dict.fromkeys(raw_quotes))
        quotes = [
            segment
            for q in unique_quotes
            for segment in SPLITTER.split(q)
            if len(segment) < 256
        ]
        monologues = [Monologue(content=q.strip(), source="wikiquotes") for q in quotes]
        return monologues

    def extract(self, character_name: str, max_quotes: int = 2_000) -> list[Monologue]:
        logger.info(
            f"Attempting to extract Wikiquotes, character_name: {character_name}"
        )
        r = self._extract(character_name=character_name, max_quotes=max_quotes)
        logger.info(f"✅ Extracted wikiquotes for {character_name}.")
        return r

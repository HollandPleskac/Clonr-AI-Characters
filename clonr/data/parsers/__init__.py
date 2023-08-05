from .base import Parser, ParserException
from .fandom import FandomParser, FullURLParser
from .web import BasicWebParser
from .wiki import WikipediaParser
from .yt_transcript import YoutubeTranscriptParser
from .wikiquotes import WikiQuotesParser


def url_to_doc(url: str):
    for parser in [
        WikipediaParser,
        FandomParser,
        YoutubeTranscriptParser,
        BasicWebParser,
        FullURLParser,
    ]:
        try:
            return parser().extract(url=url)
        except Exception:
            pass
    raise ParserException(f"Unable to parse url: {url}")

import re
from dataclasses import dataclass

from loguru import logger

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache

try:
    import wikipedia

    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False


@dataclass
class ParsedURL:
    title: str | None
    lang: str
    pageid: str | None


# (Jonny): this library sucks frfr. not sure what to do with it.
class WikipediaParser(Parser):
    def _parse_url(self, url: str) -> ParsedURL:
        if r := re.findall(r"https://(\w{2,})\.wikipedia\.org/wiki/(\w+)", url):
            lang, title = r[0]
            return ParsedURL(title=title, lang=lang, pageid=None)
        elif r := re.findall(
            r"https://(\w{2,})\.wikipedia.org/w/index\.php?title=(\w+)&oldid=(\d+).*",
            url,
        ):
            lang, title, pageid = r[0]
            return ParsedURL(title=title, lang=lang, pageid=pageid)
        elif r := re.findall(r"https://(\w{2,})\.wikipedia\.org/wiki?curid=(\d+)", url):
            lang, pageid = r[0]
            return ParsedURL(title=None, lang=lang, pageid=pageid)
        msg = "Invalid Wikipedia page url"
        logger.error(msg)
        raise ParserException(msg)

    @instance_level_lru_cache(maxsize=None)
    def _extract(
        self,
        title: str | None = None,
        pageid: str | None = None,
        lang: str = "en",
    ) -> Document:
        if not WIKIPEDIA_AVAILABLE:
            raise ImportError("wikipedia package not found. `pip install wikipedia`.")
        wikipedia.set_lang(lang)
        try:
            page = wikipedia.page(title=title, pageid=pageid, auto_suggest=False)
            content = page.content
            content = re.sub(r"\s*\<s\>\s*", " ", content)
        except wikipedia.exceptions.DisambiguationError as e:
            raise ParserException(
                f"Failed to parse Wikipedia page: {page}. Reason: {str(e)}"
            )
        except wikipedia.exceptions.PageError:
            raise ParserException(f"Wikipedia page not found: {page}")
        return Document(content=content)

    def extract(
        self,
        *,
        url: str | None = None,
        title: str | None = None,
        pageid: str | None = None,
        lang: str = "en",
        type: str = "wikipedia",
    ) -> Document:
        if url is None and title is None and pageid is None:
            raise ValueError("Must provide one of url, title, or pageid")
        logger.info(
            f"Attempting to extract Wikipedia page. Title: {title}. PageID: {pageid}. url: {url}"
        )
        if url is not None:
            r = self._parse_url(url=url)
            title = r.title
            pageid = r.pageid
            lang = r.lang
        doc = self._extract(title=title, pageid=pageid, lang=lang)
        logger.info("✅ Extracted wikipedia page.")
        doc.type = type
        return doc

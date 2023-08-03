from .base import Parser, ParserException
from .fandom import FandomParser, JonnyURLParser
from .web import BasicWebParser
from .wiki import WikipediaParser
from .yt_transcript import YoutubeTranscriptParser


def url_to_doc(url: str):
    for parser in [
        WikipediaParser,
        FandomParser,
        YoutubeTranscriptParser,
        BasicWebParser,
        JonnyURLParser,
    ]:
        try:
            return parser().extract(url=url)
        except Exception:
            pass
    raise ParserException(f"Unable to parse url: {url}")


# import re
# from urllib.parse import urlparse

# class URLParseError(Exception):
#     pass

# def is_valid_url(url: str):
#     r = urlparse(url=url)
#     suffixes = [
#         'fandom.com',
#         'wikipedia.com',
#         'wikiquotes.com',
#         'youtube.com',
#         'facebook.com',
#         'instagram.com',
#         'reddit.com',
#         'twitter.com'
#     ]
#     if r.scheme != 'https':
#         raise URLParseError(f"Invalid scheme: {r.scheme}")
#     if r.params:
#         raise URLParseError(f"URL Params not allowed: {r.params}")
#     if r.query:
#         raise URLParseError(f"URL query params not allowed: {r.query}")
#     for suffix in suffixes:
#         if r.netloc.endswith(suffix):
#             return True
#     raise URLParseError(f"Invalid domain: {r.netloc}")

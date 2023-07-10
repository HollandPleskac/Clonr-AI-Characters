import re

from loguru import logger
from pydantic import BaseModel

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document
from clonr.utils.shared import instance_level_lru_cache

try:
    from youtube_transcript_api import YouTubeTranscriptApi

    YOUTUBE_TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_API_AVAILABLE = False


DEFAULT_LANGUAGES = ["en"]


class Caption(BaseModel):
    text: str
    start: float
    duration: float


class YoutubeTranscriptParser(Parser):
    """This does not do speaker diarization!
    It just extracts the captions from a video"""

    def parse_video_id(self, yt_link: str) -> str:
        patterns = [
            r"^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)",
            r"^https?://(?:www\.)?youtube\.com/embed/([\w-]+)",
            r"^https?://(?:www\.)?youtube\.com/shorts/([\w-]+)",
            r"^https?://youtu\.be/([\w-]+)",
        ]
        for pattern in patterns:
            if match := re.search(pattern, yt_link):
                return match.group(1)
        msg = "Invalid Youtube page url"
        logger.error(msg)
        raise ParserException(msg)

    @instance_level_lru_cache(maxsize=None)
    def extract_captions_from_link(
        self,
        link: str,
        languages: tuple[str] | None = None,
    ) -> list[Caption]:
        if not YOUTUBE_TRANSCRIPT_API_AVAILABLE:
            msg = "youtube-transcript-api package not found. `pip install youtube-transcript-api`"
            raise ImportError(msg)
        if languages is None:
            languages = DEFAULT_LANGUAGES
        video_id = self.parse_video_id(link)
        try:
            response = YouTubeTranscriptApi.get_transcript(
                video_id, languages=languages
            )
            captions = [Caption(**x) for x in response]
        except Exception as e:
            raise ParserException(
                f"Failed to retrieve transcript for YouTube video: {link}. Reason: {str(e)}"
            )
        return captions

    def _extract_link(self, link: str, languages: tuple[str] | None = None) -> Document:
        captions = self.extract_captions_from_link(link=link, languages=languages)
        transcript = "\n".join(x.text for x in captions)
        return Document(content=transcript, url=link, type="youtube")

    def extract(
        self,
        url: str,
        languages: tuple[str] | None = None,
    ) -> Document:
        logger.info(f"Attempting to extracting transcript from link: {url}")
        doc = self._extract_link(link=url, languages=languages)
        logger.info(f"✅ Extracted transcript from link: {url}")
        return doc


def test_this():
    import textwrap
    from difflib import SequenceMatcher

    url = "https://www.youtube.com/watch?v=WYiGfhxxkYk"
    expected = textwrap.dedent(
        """
        the federal election will be held on
        saturday the 21st of may so make sure
        you know where and how to vote
        your vote will help shape australia find
        out more at
        aec.gov.u authorised by the electoral
        commissioner canberra
    """
    ).strip()
    computed = YoutubeTranscriptParser().extract(url).content
    assert SequenceMatcher(None, expected, computed.ratio()) > 0.95

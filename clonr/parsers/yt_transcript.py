import re
from typing import Any, List, Optional

from clonr.data_structures import Document
from clonr.parsers.base import Parser, ParserException


class YoutubeTranscriptParser(Parser):
    @staticmethod
    def _extract_video_id(yt_link) -> Optional[str]:
        patterns = [
            r"^https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)",
            r"^https?://(?:www\.)?youtube\.com/embed/([\w-]+)",
            r"^https?://youtu\.be/([\w-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, yt_link)
            if match:
                return match.group(1)

        return None

    def extract(
        self,
        ytlinks: str | list[str],
        languages: Optional[list[str]] = ["en"],
        **load_kwargs: Any,
    ) -> Document | list[Document]:
        if not isinstance(ytlinks, list):
            return self.extract([ytlinks], languages=languages, **load_kwargs)[0]

        documents = []
        for link in ytlinks:
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
            except ImportError:
                raise ImportError(
                    "Please install the `youtube-transcript-api` package: `pip install youtube-transcript-api`"
                )

            video_id = self._extract_video_id(link)
            if not video_id:
                raise ParserException(
                    f"Failed to extract YouTube video ID from link: {link}"
                )

            try:
                srt = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            except Exception as e:
                raise ParserException(
                    f"Failed to retrieve transcript for YouTube video: {link}. Reason: {str(e)}"
                )

            transcript = ""
            for chunk in srt:
                transcript += chunk["text"] + "\n"

            documents.append(Document(content=transcript))

        return documents

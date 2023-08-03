from typing import List

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document

try:
    import snscrape.modules.instagram as snsinstagram

    SNSCRAPE_INSTAGRAM_AVAILABLE = True
except ImportError:
    SNSCRAPE_INSTAGRAM_AVAILABLE = False


class InstagramUserParser(Parser):
    def extract(self, username: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_INSTAGRAM_AVAILABLE:
            msg = "snscrape.modules.instagram not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsinstagram.InstagramUserScraper(username).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]


class InstagramHashtagParser(Parser):
    def extract(self, hashtag: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_INSTAGRAM_AVAILABLE:
            msg = "snscrape.modules.instagram not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsinstagram.InstagramHashtagScraper(hashtag).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]


class InstagramLocationParser(Parser):
    def extract(self, location_id: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_INSTAGRAM_AVAILABLE:
            msg = "snscrape.modules.instagram not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsinstagram.InstagramLocationScraper(location_id).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]

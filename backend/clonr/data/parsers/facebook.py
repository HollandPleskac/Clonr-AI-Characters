from typing import List

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document

try:
    import snscrape.modules.facebook as snsfacebook

    SNSCRAPE_FACEBOOK_AVAILABLE = True
except ImportError:
    SNSCRAPE_FACEBOOK_AVAILABLE = False


class FacebookUserParser(Parser):
    def extract(self, username: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_FACEBOOK_AVAILABLE:
            msg = "snscrape.modules.facebook not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsfacebook.FacebookUserScraper(username).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]


class FacebookCommunityParser(Parser):
    def extract(self, username: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_FACEBOOK_AVAILABLE:
            msg = "snscrape.modules.facebook not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsfacebook.FacebookCommunityScraper(username).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]


class FacebookGroupParser(Parser):
    def extract(self, group: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_FACEBOOK_AVAILABLE:
            msg = "snscrape.modules.facebook not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsfacebook.FacebookGroupScraper(group).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.content)

        return [Document(content=attributes_container)]

from typing import List

from clonr.data.parsers.base import Parser
from clonr.data_structures import Document

try:
    import snscrape.modules.reddit as snsreddit

    SNSCRAPE_REDDIT_AVAILABLE = True
except ImportError:
    SNSCRAPE_REDDIT_AVAILABLE = False


class RedditUserParser(Parser):
    def extract(self, author: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_REDDIT_AVAILABLE:
            msg = "snscrape.modules.reddit not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(snsreddit.RedditUserScraper(author).get_items()):
            if i >= num_posts:
                break
            attributes_container.append(submission.selftext)

        return [Document(content=attributes_container)]


class RedditSubredditParser(Parser):
    def extract(self, author: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_REDDIT_AVAILABLE:
            msg = "snscrape.modules.reddit not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsreddit.RedditSubredditScraper(author).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.selftext)

        return [Document(content=attributes_container)]


class RedditSearchParser(Parser):
    def extract(self, query: str, num_posts: int) -> List[Document]:
        if not SNSCRAPE_REDDIT_AVAILABLE:
            msg = "snscrape.modules.reddit not found. Please install snscrape using `pip install snscrape`."
            raise ImportError(msg)

        attributes_container = []
        for i, submission in enumerate(
            snsreddit.RedditSearchScraper(query).get_items()
        ):
            if i >= num_posts:
                break
            attributes_container.append(submission.selftext)

        return [Document(content=attributes_container)]

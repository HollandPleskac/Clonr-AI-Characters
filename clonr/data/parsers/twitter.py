from typing import List

from clonr.data.parsers.base import Parser, ParserException
from clonr.data_structures import Document

try:
    import snscrape.modules.twitter as sntwitter

    SNSCRAPE_TWITTER_AVAILABLE = True
except ImportError:
    SNSCRAPE_TWITTER_AVAILABLE = False


class TwitterSearchParser(Parser):
    def extract(self, query: str, num_tweets: int) -> List[Document]:
        if not SNSCRAPE_TWITTER_AVAILABLE:
            msg = "snscrape.modules.twitter not found. `pip install snscrape`"
            raise ImportError(msg)
        attributes_container = []
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i > num_tweets:
                break
            attributes_container.append(tweet.rawContent)
        return [Document(content=attributes_container)]


class TwitterUserParser(Parser):
    def extract(self, user: str, num_tweets: int) -> List[Document]:
        if not SNSCRAPE_TWITTER_AVAILABLE:
            msg = "snscrape.modules.twitter not found. `pip install snscrape`"
            raise ImportError(msg)
        attributes_container = []
        for i, tweet in enumerate(sntwitter.TwitterUserScraper(user).get_items()):
            if i > num_tweets:
                break
            attributes_container.append(tweet.rawContent)
        return [Document(content=attributes_container)]


class TwitterHashtagParser(Parser):
    def extract(self, hashtag: str, num_tweets: int) -> List[Document]:
        if not SNSCRAPE_TWITTER_AVAILABLE:
            msg = "snscrape.modules.twitter not found. `pip install snscrape`"
            raise ImportError(msg)
        attributes_container = []
        for i, tweet in enumerate(sntwitter.TwitterHashtagScraper(hashtag).get_items()):
            if i > num_tweets:
                break
            attributes_container.append(tweet.rawContent)
        return [Document(content=attributes_container)]


class TwitterTweetParser(Parser):
    def extract(self, tweet_id: str, num_tweets: int) -> List[Document]:
        if not SNSCRAPE_TWITTER_AVAILABLE:
            msg = "snscrape.modules.twitter not found. `pip install snscrape`"
            raise ImportError(msg)
        attributes_container = []
        for i, tweet in enumerate(sntwitter.TwitterTweetScraper(tweet_id).get_items()):
            if i > num_tweets:
                break
            attributes_container.append(tweet.rawContent)
        return [Document(content=attributes_container)]

"""RSS Feed module."""
import typing

import feedparser

from rss.converter import Converter
from rss.post import Post


class RSSFeed:
    """Represents a public rss feed."""

    def __init__(self, url: str, name: str, converter: Converter):
        """Initialise the feed."""
        self.url = url
        self.name = name
        self.converter = converter

    def posts(self) -> typing.Generator[Post, None, None]:
        """Yield the posts of this rss feed."""
        feed = feedparser.parse(self.url)

        for post in feed.entries:
            yield Post(
                link=post.link,
                title=post.title,
                author=post.author,
                content=post.summary,
                content_enctype=post.summary_detail.type,
                converter=self.converter,
            )

    def posts_raw(self) -> feedparser.util.FeedParserDict:
        """Return the raw feedparser entries."""
        return feedparser.parse(self.url).entries

    def __str__(self):
        """Return the name of the feed, or the url if no name is set."""
        return self.name if self.name else self.url

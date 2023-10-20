from typing import Iterable

import feedparser

from rss.converter import Converter
from rss.post import Post


class RSSFeed:
    """Represents a public rss feed."""

    def __init__(self, url: str, name: str, converter: Converter):
        self.url = url
        self.name = name
        self.converter = converter

    def posts(self) -> Iterable[Post]:
        """Yields the posts of this rss feed."""
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

    def posts_raw(self) -> Iterable:
        """Returns the raw feedparser entries"""
        return feedparser.parse(self.url).entries

    def __str__(self):
        return self.name if self.name else self.url

"""RSS Post module."""
from rss.converter import Converter


class Post:
    """Represents a post from rss feeds."""

    def __init__(
        self,
        link: str,
        title: str,
        author: str,
        content: str,
        content_enctype: str,
        converter: Converter,
    ):
        """Initialise the post."""
        self.link = link
        self.title = title
        self.author = author
        self.raw_content = content
        self.content_enctype = content_enctype
        self.converter = converter

    def render_content(self) -> str:
        """Return the rendered content of this post."""
        return self.converter.convert(self.raw_content)  # type: ignore

    def __str__(self):
        """Return the title of the post."""
        return self.title

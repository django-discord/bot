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
        self.link = link
        self.title = title
        self.author = author
        self.raw_content = content
        self.content_enctype = content_enctype
        self.converter = converter

    def render_content(self):
        return self.converter.convert(self.raw_content)

    def __str__(self):
        return self.title

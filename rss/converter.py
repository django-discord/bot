"""HTML to markdown converter."""
import importlib

from bs4.element import Tag
from markdownify import MarkdownConverter


class Converter(MarkdownConverter):
    """General converter for converting from HTML to Discord flavour markdown."""

    def convert_img(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        """Return the image source from a tag.

        Discord doesn't display images using the default markdown way,
        it will expand links which can be displayed as an image.
        This converter simply returns the src of the image tag.
        If the image is supposed to be an emoji, the Django forum will set its class to
        'emoji', in that case the emoji code is returned.
        Note that the emoji code may not exist, or be called something else in Discord.
        """
        if "emoji" in el.attrs.get("class", ""):
            return el.attrs.get("alt")
        return el.attrs.get("src")

    def convert_p(self, el: Tag, text: str, convert_as_inline: bool) -> str:
        """Convert a paragraph tag to one newlines, rather than two."""
        return super().convert_p(el, text, convert_as_inline).removesuffix("\n")


def load_converter(path: str) -> type[Converter]:
    """Return the loaded converter from its dot path."""
    module_path, class_name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module_path), class_name)

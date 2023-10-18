import importlib

from markdownify import MarkdownConverter


class Converter(MarkdownConverter):
    """General converter for converting from HTML to markdown which is displayable in discord."""

    def convert_img(self, el, text, convert_as_inline):
        """Discord doesn't display images using the default markdown way, it will expand links which can be displayed as an image.
        This converter simply returns the src of the image tag.
        If the image is supposed to be an emoji the django forum will set its class to 'emoji', in that case the emoji code is returned.
        Note that the emoji code may not exist, or be called something else in discord.
        """
        if "emoji" in el.attrs.get("class", ""):
            return el.attrs.get("alt")
        return el.attrs.get("src")

    def convert_p(self, *args, **kwargs):
        """The paragraph is interpreted as two newlines, this will only result in poor formatting down the
        line. One newline will be omitted for that reason."""
        return super().convert_p(*args, **kwargs).removesuffix("\n")


def load_converter(path) -> Converter.__class__:
    """Returns the loaded converter from its dot path."""
    module_path, class_name = path.rsplit(".", 1)
    converter = getattr(importlib.import_module(module_path), class_name)

    if not issubclass(converter, Converter):
        raise LookupError(f"{converter} is not a subclass of {Converter.__class__}")

    return converter

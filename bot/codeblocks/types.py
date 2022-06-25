from __future__ import annotations

from typing import NamedTuple

import hikari
from codeblocks.constants import Language
from markup import services as markdown_services


class Codeblock(
    NamedTuple(
        "Codeblock",
        [
            ("content", str),
            ("length", int),
        ],
    )
):
    @classmethod
    def from_message(cls, message: hikari.Message) -> Codeblock:
        return cls(
            content=message.content,
            length=len(message.content.split("\n")),
        )


class MarkdownCodeblock(
    NamedTuple(
        "MarkdownCodeblock",
        [
            ("content", str),
        ],
    )
):
    @classmethod
    def set_content(cls, content: str, language: Language) -> MarkdownCodeblock:
        return cls(
            content=markdown_services.codeblock(text=content, language=language),
        )

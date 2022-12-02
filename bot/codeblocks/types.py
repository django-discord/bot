from __future__ import annotations

from typing import NamedTuple, Optional

import hikari
from codeblocks.constants import Language
from markup import services as markdown_services


class Codeblock(
    NamedTuple(
        "Codeblock",
        [
            ("content", Optional[str]),
            ("length", int),
        ],
    )
):
    @classmethod
    def from_message(cls, message: hikari.Message) -> Codeblock:
        return cls(
            content=message.content,
            length=len(message.content.split("\n"))
            if message.content is not None
            else 0,
        )


class MarkdownCodeblock(
    NamedTuple(
        "MarkdownCodeblock",
        [
            ("content", Optional[str]),
        ],
    )
):
    @classmethod
    def set_content(cls, content: str, language: Language) -> MarkdownCodeblock:
        return cls(
            content=markdown_services.codeblock(text=content, language=language),
        )

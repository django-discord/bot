from typing import Optional

from codeblocks.constants import Language


def bold(text: str) -> str:
    return f"**{text}**"


def italics(text: str) -> str:
    return f"*{text}*"


def inline_code(text: str) -> str:
    return f"`{text}`"


def codeblock(text: str, language: Language) -> Optional[str]:
    try:
        return f"```{language.get_markdown_name()}\n{text}\n```"
    except AttributeError:
        pass
    return None

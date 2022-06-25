import abc
import ast
import logging
from typing import Optional, Union

import bs4
import guesslang
import hikari
from codeblocks.constants import LANGUAGE_GUESS_TRESHOLD, Language
from codeblocks.types import Codeblock, MarkdownCodeblock
from codeblocks.utils import black_string

logger = logging.getLogger(__name__)
_LOG_PREFIX = "[CODEBLOCK-PARSER]"


class CodeblockParser(abc.ABC):
    def __init__(self, message: hikari.Message) -> None:
        self.codeblock = Codeblock.from_message(message=message)

    def validate_and_format(self):
        return MarkdownCodeblock.set_content(
            content=self.format_code(self.codeblock.content),
            language=self.validate_and_get_language(),
        )

    @abc.abstractmethod
    def validate_and_get_language(self):
        pass

    @abc.abstractmethod
    def format_code(self, content: str) -> str:
        pass


class PythonParser(CodeblockParser):
    def validate_and_get_language(self):
        if self.is_valid_python(self.codeblock.content):
            return Language.PYTHON

    def format_code(self, content: str) -> str:
        return black_string(content)

    @classmethod
    def is_valid_python(cls, content: str) -> bool:
        logger.info(f"{_LOG_PREFIX} Checking if message is valid python code.")
        try:
            content = content.replace("\x00", "")
            tree = ast.parse(content)
        except SyntaxError:
            return False
        return not all(isinstance(node, ast.Expr) for node in tree.body)


class HTMLParser(CodeblockParser):
    def validate_and_get_language(self):
        logger.info(f"{_LOG_PREFIX} Checking if message is valid html code.")
        if self.is_valid_html(content=self.codeblock.content):
            return Language.HTML

    @classmethod
    def is_valid_html(cls, content: str) -> bool:
        logger.info(f"{_LOG_PREFIX} Checking if message is valid html code.")
        return bool(bs4.BeautifulSoup(content, "html.parser").find())

    def format_code(self, content: str) -> str:
        return content


class JavascriptParser(CodeblockParser):
    def validate_and_get_language(self):
        if self.is_javascript_code(content=self.codeblock.content):
            return Language.JAVASCRIPT

    def format_code(self, content: str) -> str:
        return content

    @classmethod
    def is_javascript_code(cls, content: str) -> Optional[bool]:
        logger.info(f"{_LOG_PREFIX} Checking if message is valid javascript code.")
        guess = guesslang.Guess()
        if (
            dict(guess.probabilities(content))[Language.JAVASCRIPT.value]
            > LANGUAGE_GUESS_TRESHOLD
        ):
            return guess.language_name(content) in Language.choices()


def get_parser(
    message: hikari.Message,
) -> Optional[Union[HTMLParser, PythonParser, JavascriptParser]]:
    if PythonParser.is_valid_python(content=message.content):
        logger.info(f"{_LOG_PREFIX} Message is unformatted python code.")
        return PythonParser(message=message)
    elif HTMLParser.is_valid_html(content=message.content):
        logger.info(f"{_LOG_PREFIX} Message is unformatted html code.")
        return HTMLParser(message=message)
    elif JavascriptParser.is_javascript_code(content=message.content):
        logger.info(f"{_LOG_PREFIX} Message is unformatted javascript code.")
        return JavascriptParser(message=message)
    else:
        logger.info(f"{_LOG_PREFIX} Message is not valid code, no action necessary.")
        return


def should_parse_message(content: str) -> bool:
    return not (_is_codeblock(content=content) or _is_inline_block(content=content))


def _is_codeblock(content: str):
    return content.startswith("```") and content.endswith("```")


def _is_inline_block(content: str):
    return content.startswith("`") and content.endswith("`")

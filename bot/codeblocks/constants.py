import enum

from codeblocks.utils import black_string


class Language(enum.Enum):
    PYTHON = "Python"
    HTML = "HTML"
    JAVASCRIPT = "JavaScript"
    NONE = ""

    @classmethod
    def choices(cls):
        return [lang.value for lang in cls if lang.value]

    def get_markdown_name(self):
        _mapping = {"Python": "py", "HTML": "html", "JavaScript": "js"}
        return _mapping.get(self.value)


_EXAMPLE_CODE = black_string("def add_one(foo: int) -> int: return foo + 1")
_ESCAPED_CODEBLOCK = f"\`\`\`python\n{_EXAMPLE_CODE}\n\`\`\`"


def get_escaped_codeblock():
    return _ESCAPED_CODEBLOCK


def get_example_code():
    return _EXAMPLE_CODE


LANGUAGE_GUESS_TRESHOLD = 0.5

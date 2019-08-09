"""
An implementation of the C preprocessor. However, rather than generating code,
the purpose of this preprocessor is to determine the relationship between compilation units.
"""

import re
import string
from enum import Enum, unique, auto
from typing import Optional, List, NamedTuple, Iterable


class UnknownTokenError(Exception):
    def __init__(self, line_number: int, column_number: int, token: str):
        self.line_number = line_number
        self.column_number = column_number
        self.token = token

    def __str__(self):
        return f"Unknown token \"{self.token}\" on line {self.line_number}, {self.column_number}"


@unique
class TokenType(Enum):
    DIRECTIVE = auto()
    IDENTIFIER = auto()
    INTEGER_CONST = auto()
    CHAR_CONST = auto()
    STRING = auto()
    FILENAME = auto()
    DEFINED = auto()
    ELLIPSIS = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    EQUAL = auto()
    AND = auto()
    OR = auto()
    TOKEN_CONCATINATION = auto()
    LPARAN = auto()
    RPARAN = auto()
    COMMA = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    NOT = auto()
    TOKEN_STRINGIFICATION = auto()


TOKEN_MAP = (
    (TokenType.STRING,                  re.compile(r'^(".*")')),
    (TokenType.FILENAME,                re.compile(r'^(<.*>)')),
    (TokenType.INTEGER_CONST,           re.compile(r"^(\d+)")),
    (TokenType.CHAR_CONST,              re.compile(r"^('.')")),
    (TokenType.DEFINED,                 "defined"),
    (TokenType.ELLIPSIS,                "..."),
    (TokenType.LESS_THAN_OR_EQUAL,      "<="),
    (TokenType.GREATER_THAN_OR_EQUAL,   ">="),
    (TokenType.EQUAL,                   "=="),
    (TokenType.AND,                     "&&"),
    (TokenType.OR,                      "||"),
    (TokenType.TOKEN_CONCATINATION,     "##"),
    (TokenType.LPARAN,                  "("),
    (TokenType.RPARAN,                  ")"),
    (TokenType.COMMA,                   ","),
    (TokenType.LESS_THAN,               "<"),
    (TokenType.GREATER_THAN,            ">"),
    (TokenType.NOT,                     "!"),
    (TokenType.TOKEN_STRINGIFICATION,   "#"),
    (TokenType.IDENTIFIER,              re.compile(r"^(\w+)"))
)


class Token(NamedTuple):
    token_type: TokenType
    line: int
    col: int
    text: str


def _tokenize_line(line: str, line_number: int) -> Optional[List[Token]]:
    if not line.startswith("#"):
        return None

    try:
        current_index = line.index(" ", 1)
        line_tokens = [Token(TokenType.DIRECTIVE, line_number, 1, line[1:current_index])]
    except ValueError:
        return [Token(TokenType.DIRECTIVE, line_number, 1, line[1:])]

    while current_index < len(line):
        if line[current_index].isspace():
            current_index += 1
            continue

        token = None

        for token_type, matcher in TOKEN_MAP:
            if type(matcher) is str:
                if line.startswith(matcher, current_index):
                    token = Token(token_type, line_number, current_index, matcher)
                    break
            else:
                line_slice = line[current_index:]
                re_match = matcher.match(line_slice)
                if re_match:
                    token = Token(token_type, line_number, current_index, re_match.group(0))
                    break

        if token:
            line_tokens.append(token)
            current_index += len(token.text)
        else:
            raise UnknownTokenError(line_number, current_index, line[current_index])

    return line_tokens


def tokenize_lines(source_lines: Iterable[str], skip_c=True) -> Iterable[List[Token]]:
    """
    Takes a source file split into lines and returns a generator that tokeninzes it.
    If `skip_c` is true, C code (lines which do not start with "#") are ignored.
    """
    for i, line in enumerate(source_lines):
        line_tokens = _tokenize_line(line, i)
        if line_tokens or (not line_tokens and not skip_c):
            yield line_tokens



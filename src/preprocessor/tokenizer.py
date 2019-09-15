import re
from enum import Enum, unique, auto
from typing import NamedTuple
from ..useful import StringCursor


class UnknownTokenError(Exception):
    """Exception thrown when an unknown token is encountered during tokenization"""
    def __init__(self, line_number: int, column_number: int, token: str):
        self.line_number = line_number
        self.column_number = column_number
        self.token = token

    def __str__(self):
        return f"Unknown token \"{self.token}\" on line {self.line_number}: {self.column_number}"


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


# List of 2-tuples, pairing the TokenType with a way to match it. Sorted in order of priority.
TOKEN_MAP = (
    (TokenType.STRING,                  re.compile(r'^(".*")')),
    (TokenType.FILENAME,                re.compile(r'^(<\s*\S*\s*>)')),
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
    """A simple class storing the token, its type, and its metadata"""
    token_type: TokenType
    line: int
    col: int
    text: str


def _tokenize_directive(cursor: StringCursor, line_numer: int) -> Token:
    if cursor.peak() != "#":
        raise UnknownTokenError
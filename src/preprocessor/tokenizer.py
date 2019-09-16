import re
import string
from enum import Tuple, Enum, unique, auto
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


def _tokenize_directive(cursor: StringCursor, line_number: int) -> Optional[Token]:
    if cursor.peak() != "#":
        raise UnknownTokenError(line_number, 0, cursor.peak())

    directive_str = cursor.read_until(set(string.whitespace))
    return Token(TokenType.DIRECTIVE, line_number, 1, directive_str[1:])


def _read_next_token(cursor: StringCursor, line_number: int) -> Token:
    for token_type, matcher in TOKEN_MAP:
        match = cursor.read_match(matcher)

        if match:
            return Token(token_type, line_number, cursor.)


def tokenize_line(cursor: StringCursor, line_number: int) -> Tuple[List[Token], int]:
    """Tokenizes a line, following escaped newlines. Returns the tokens and the number of lines read"""
    line_offset = 1
    return_tokens = []

    try:
        return_tokens.append(_tokenize_directive(cursor, line_number))
    except UnknownTokenError:
        cursor.read_until("\n")
    
    while(cursor.peak() != "\n" and not cursor.done()):
        cursor.read_until(lambda s: s[0] not in set(string.whitespace))



    return (return_tokens, line_offset)

def tokenize_file(file: str) -> List[Token]:
    cursor = StringCursor(file)
    return_tokens = []
    line_counter = 0

    while(not cursor.done()):


    return return_tokens
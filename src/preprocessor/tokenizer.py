import re
from enum import Enum, unique, auto
from typing import List, Optional, Tuple
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
    NOT_EQUAL = auto()
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


VALUE_TOKENS = {
    TokenType.IDENTIFIER, TokenType.CHAR_CONST, TokenType.INTEGER_CONST
}

RTL_OPS = {
    TokenType.NOT, TokenType.DEFINED
}

OPERATOR_TOKENS = {
    TokenType.NOT, TokenType.DEFINED, TokenType.EQUAL, TokenType.NOT_EQUAL,
    TokenType.GREATER_THAN_OR_EQUAL, TokenType.LESS_THAN_OR_EQUAL, TokenType.GREATER_THAN,
    TokenType.LESS_THAN, TokenType.AND, TokenType.OR
}

# List of 2-tuples, pairing the TokenType with a way to match it. Sorted in order of priority.
TOKEN_MAP = (
    (TokenType.STRING,                  re.compile(r'^"(.*)"')),
    (TokenType.FILENAME,                re.compile(r'^<(\s*\S*\s*)>')),
    (TokenType.INTEGER_CONST,           re.compile(r"^(\d+)")),
    (TokenType.CHAR_CONST,              re.compile(r"^('.')")),
    (TokenType.DEFINED,                 re.compile(r"defined")),
    (TokenType.ELLIPSIS,                re.compile(r"\.\.\.")),
    (TokenType.LESS_THAN_OR_EQUAL,      re.compile(r"<=")),
    (TokenType.GREATER_THAN_OR_EQUAL,   re.compile(r">=")),
    (TokenType.EQUAL,                   re.compile(r"==")),
    (TokenType.NOT_EQUAL,               re.compile(r"!=")),
    (TokenType.AND,                     re.compile(r"&&")),
    (TokenType.OR,                      re.compile(r"\|\|")),
    (TokenType.TOKEN_CONCATINATION,     re.compile(r"##")),
    (TokenType.LPARAN,                  re.compile(r"\(")),
    (TokenType.RPARAN,                  re.compile(r"\)")),
    (TokenType.COMMA,                   re.compile(r",")),
    (TokenType.LESS_THAN,               re.compile(r"<")),
    (TokenType.GREATER_THAN,            re.compile(r">")),
    (TokenType.NOT,                     re.compile(r"!")),
    (TokenType.TOKEN_STRINGIFICATION,   re.compile(r"#")),
    (TokenType.IDENTIFIER,              re.compile(r"^(\w+)"))
)


class Token():
    """A simple class storing the token, its type, and its metadata"""
    def __init__(self, token_type: TokenType, line: int, col: int, match: re.Match):
        self.token_type = token_type
        self.line = line
        self.col = col
        self.match = match

    def __repr__(self):
        return f"Token(token_type={self.token_type}, line={self.line}, col={self.line}, match={self.match})"

    @property
    def error_str(self):
        """Returns a string representation for use in error text."""
        return f"\"{self.token_type}\" at {self.line}, {self.col}"


def _tokenize_directive(cursor: StringCursor, line_number: int) -> Optional[Token]:
    directive_match = cursor.read_match(r"#(\S*)")

    if not directive_match:
        raise UnknownTokenError(line_number, 0, cursor.peak())

    return Token(TokenType.DIRECTIVE, line_number, 1, directive_match)


def _read_next_token(cursor: StringCursor, line_number: int) -> Token:
    """Reads a token from cursor. Assumes the cursor is currently on a non-whitespace character."""
    for token_type, matcher in TOKEN_MAP:
        match = cursor.read_match(matcher)

        if match:
            column = cursor.position - len(match.group())
            return Token(token_type, line_number, column, match)

    raise UnknownTokenError(line_number, cursor.position, cursor.unread_slice)


def tokenize_line(cursor: StringCursor, line_number: int) -> Tuple[List[Token], int]:
    """Tokenizes a logical line, following escaped newlines. Returns the tokens and the number of lines read"""
    line_offset = 0
    return_tokens = []

    try:
        return_tokens.append(_tokenize_directive(cursor, line_number))
    except UnknownTokenError:
        cursor.read_until("\n")

    while(cursor.peak() != "\n" and not cursor.done()):
        StringCursor.read_whitespace(cursor)
        return_tokens.append(_read_next_token(cursor, line_number + line_offset))
        StringCursor.read_whitespace(cursor)

        if cursor.peak(2) == "\\\n":
            cursor.read(2)
            line_offset += 1

    return (return_tokens, line_offset + 1)


def tokenize_file(file: str) -> List[List[Token]]:
    cursor = StringCursor(file)
    return_tokens = []
    line_counter = 0

    while(not cursor.done()):
        tokens, lines = tokenize_line(cursor, line_counter)
        return_tokens.append(tokens)
        line_counter += lines

    return return_tokens

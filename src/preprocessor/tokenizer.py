from enum import Enum, auto
from typing import Optional, List
import re


class TokenType(Enum):
    WHITESPACE = 0
    GENERIC = 1
    STRING_LITERAL = auto()
    NUM_LITERAL = auto()
    DIRECTIVE = auto()
    IDENTIFIER = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    OP_LT = auto()
    OP_GT = auto()
    OP_EQ = auto()
    OP_NEQ = auto()
    OP_LTE = auto()
    OP_GTE = auto()
    OP_NOT = auto()
    OP_DEFINED = auto()
    OP_JOIN = auto()
    OP_CONCAT = auto()


TOKEN_MAP = (
    (re.compile(r"\s"),             TokenType.WHITESPACE),
    (re.compile(r"#(\S*)"),         TokenType.DIRECTIVE),
    (re.compile(r"\".*\""),         TokenType.STRING_LITERAL),
    (re.compile(r"(\d.?\d?)+"),     TokenType.NUM_LITERAL),
    (re.compile(r"defined"),        TokenType.OP_DEFINED),
    (re.compile(r"=="),             TokenType.OP_EQ),
    (re.compile(r"!="),             TokenType.OP_NEQ),
    (re.compile(r"<="),             TokenType.OP_LTE),
    (re.compile(r">="),             TokenType.OP_GTE),
    (re.compile(r"##"),             TokenType.OP_CONCAT)
    (re.compile(r"<"),              TokenType.OP_LT),
    (re.compile(r">"),              TokenType.OP_GT),
    (re.compile(r"("),              TokenType.LPAREN),
    (re.compile(r")"),              TokenType.RPAREN),
    (re.compile(r","),              TokenType.COMMA),
    (re.compile(r"#"),              TokenType.OP_JOIN),
    (re.compile(r"[a-zA-Z]\w+"),    TokenType.IDENTIFIER),
    (re.compile(r"\S+"),            TokenType.GENERIC)
)


class Token():
    def __init__(self, type: TokenType, value: Optional[re.Match] = None, col: int = 0, line: int = 0):
        self.type = type
        self.value = value
        self.col = col
        self.line = line


def tokenize_line(line: str, line_num: int = 0) -> List[Token]:
    cursor = 0
    rv: List[Token] = []

    while cursor < len(line):
        for regex, token_type in TOKEN_MAP:
            match = regex.match(line, cursor)

            if match is not None:
                rv.append(Token(token_type, match, cursor, line_num))
                cursor += len(match.group(0))
                break

        raise Exception("This should never be reached.")

    return rv

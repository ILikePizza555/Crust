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
    OP_AND = auto()
    OP_OR = auto()
    OP_DEFINED = auto()
    OP_JOIN = auto()
    OP_CONCAT = auto()


LITERAL_TYPES = {TokenType.STRING_LITERAL, TokenType.NUM_LITERAL}
VALUE_TYPES = {TokenType.STRING_LITERAL, TokenType.NUM_LITERAL, TokenType.IDENTIFIER}
COMPARISON_OPERATOR_TYPES = {
    TokenType.OP_GT, TokenType.OP_LT, TokenType.OP_EQ, TokenType.OP_NEQ, TokenType.OP_GTE, TokenType.OP_LTE
}
BOOLEAN_OPERATOR_TYPES = {TokenType.OP_AND, TokenType.OP_OR}
UNARY_BOOLEAN_OPERATOR_TYPES = {TokenType.OP_NOT, TokenType.OP_DEFINED}
TOKEN_OPERATOR_TYPES = {TokenType.OP_JOIN, TokenType.OP_CONCAT}
OPERATOR_TYPES = COMPARISON_OPERATOR_TYPES | BOOLEAN_OPERATOR_TYPES | SINGLE_BOOLEAN_OPERATOR_TYPES | TOKEN_OPERATOR_TYPES


TOKEN_MAP = (
    (re.compile(r"\s"),             TokenType.WHITESPACE),
    (re.compile(r"#(\S*)"),         TokenType.DIRECTIVE),
    (re.compile(r"\".*\""),         TokenType.STRING_LITERAL),
    (re.compile(r"(\d+)(\S?)(\d*)"), TokenType.NUM_LITERAL),
    (re.compile(r"defined"),        TokenType.OP_DEFINED),
    (re.compile(r"=="),             TokenType.OP_EQ),
    (re.compile(r"!="),             TokenType.OP_NEQ),
    (re.compile(r"<="),             TokenType.OP_LTE),
    (re.compile(r">="),             TokenType.OP_GTE),
    (re.compile(r"&&"),             TokenType.OP_AND),
    (re.compile(r"||"),             TokenType.OP_OR),
    (re.compile(r"##"),             TokenType.OP_CONCAT),
    (re.compile(r"<"),              TokenType.OP_LT),
    (re.compile(r">"),              TokenType.OP_GT),
    (re.compile(r"\("),             TokenType.LPAREN),
    (re.compile(r"\)"),             TokenType.RPAREN),
    (re.compile(r","),              TokenType.COMMA),
    (re.compile(r"#"),              TokenType.OP_JOIN),
    (re.compile(r"!"),              TokenType.OP_NOT),
    (re.compile(r"[a-zA-Z]\w+"),    TokenType.IDENTIFIER),
    (re.compile(r"\S+"),            TokenType.GENERIC)
)


class Token():
    def __init__(self, ttype: TokenType, value: Optional[re.Match] = None, col: int = 0, line: int = 0):
        self.type = ttype
        self.value = value
        self.col = col
        self.line = line

    def __eq__(self, o):
        return (self.type == o.type and
                self.value == o.value and
                self.col == o.col and
                self.line == o.line)

    def __repr__(self):
        return f"Token(ttype: {self.type}, value: {self.value}, col: {self.col}, line: {self.line})"


def tokenize_line_iter(line: str, line_num: int = 0):
    cursor = 0

    while cursor < len(line):
        match_generator = ((regex.match(line, cursor), token_type) for regex, token_type in TOKEN_MAP)
        match, token_type = next(x for x in match_generator if x[0] is not None)

        if match is not None:
            y = Token(token_type, match, cursor, line_num)
            cursor += len(match.group(0))
            yield y
        else:
            raise Exception("This should never happen. Unknown tokens are Generic.")


def tokenize_line(line: str, line_num: int = 0) -> List[Token]:
    return list(tokenize_line_iter(line, line_num))

"""
An implementation of the C preprocessor. However, rather than generating code,
the purpose of this preprocessor is to determine the relationship between compilation units.
"""

import re
import string
from enum import Enum, unique
from typing import Optional, List, NamedTuple, Iterable

DIRECTIVE_RE = re.compile(r"^#(?P<directive>\S*)(?: (.*))?")
INT_CONST_RE = re.compile(r"^(\d+)")
CHAR_CONST_RE = re.compile(r"^('.')")
IDENTIFIER_RE = re.compile(r"^(\w\D+)")


class UnknownTokenError(Exception):
    def __init__(self, line_number: int, column_number: int, token: str):
        self.line_number = line_number
        self.column_number = column_number
        self.token = token

    def __str__(self):
        return f"Unknown token \"{self.token}\" on line {self.line_number}, {self.column_number}"


@unique
class TokenType(Enum):
    DIRECTIVE = 0
    IDENTIFIER = 1
    INTEGER_CONST = 2
    CHAR_CONST = 3
    LPARAN = "("
    RPARAN = ")"
    QUOTE = "\""
    COMMA = ","
    LESS_THAN = "<"
    GREATER_THAN = ">"
    EQUAL = "=="
    NOT = "!"
    AND = "&&"
    OR = "||"
    DEFINED = "defined"
    ELLIPSIS = "..."
    TOKEN_STRINGIFICATION = "#"
    TOKEN_CONCATINATION = "##"


class Token(NamedTuple):
    token_type: TokenType
    line: int
    col: int
    text: str


def _tokenize_line(line: str, line_number: int) -> Optional[List[Token]]:
    if not line.startswith("#"):
        return None

    current_index = line.index(" ", 1)
    line_tokens = [Token(TokenType.DIRECTIVE, line_number, 1, line[1:current_index])]

    while current_index < len(line):
        if line[current_index].isspace():
            current_index += 1
            continue

        token = None

        # Fixed-length tokens
        for name, member in TokenType.__members__.items():
            # Skip over non-string members, they're for regex
            if type(member.value) is not str:
                continue

            if line.startswith(member.value, current_index):
                token = Token(member, line_number, current_index, member.value)
                break

        # Check if a token has been found, if it has, skip over regex
        if token:
            line_tokens.append(token)
            current_index += len(token.text)
            continue

        # Run the regex searches for variable-length tokens
        re_match = INT_CONST_RE.match(line, pos=current_index)
        if re_match:
            token = Token(TokenType.INTEGER_CONST, line_number, current_index, re_match.group(0))

        re_match = CHAR_CONST_RE.match(line, pos=current_index)
        if re_match:
            token = Token(TokenType.CHAR_CONST, line_number, current_index, re_match.group(0))

        re_match = IDENTIFIER_RE.match(line, pos=current_index)
        if re_match:
            token = Token(TokenType.IDENTIFIER, line_number, current_index, re_match.group(0))

        if token:
            line_tokens.append(token)
            current_index += len(token.text)
        else:
            raise UnknownTokenError(line_number, current_index, line[current_index])

    return line_tokens


def tokenize_lines(source_lines: Iterable[str]) -> List[List[Token]]:
    """
    Takes a source file split into lines and tokeninzes it.
    C code (lines which do not start with "#") are ignored.
    """
    pass
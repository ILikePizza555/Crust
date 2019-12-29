from typing import Union, Iterable, Dict, List, Optional, Set
from .tokenizer import TokenType, Token


Literal = Union[str, int, float]
IdentifierTable = Dict[str, Literal]


def parse_literal(literal_token: Token) -> Literal:
    """Parses a token of type num into a python object"""
    if literal_token.type is TokenType.STRING_LITERAL:
        return literal_token.match.group(0)
    elif literal_token.type is TokenType.NUM_LITERAL:
        try:
            return int(literal_token.match.group(0))
        except ValueError:
            return float(literal_token.match.group(0))
    else:
        raise ValueError("primitive_token.type not set to a literal")


def expect_token(token: Token, expectation: Union[TokenType, Iterable[TokenType], Set[TokenType]]) -> Token:
    if type(expectation) is not set:
        try:
            expectation = set(expectation)
        except TypeError:
            expectation = {expectation, }

    if token.type not in expectation:
        raise ValueError("Expected {token} to be of type {expected}")

    return token

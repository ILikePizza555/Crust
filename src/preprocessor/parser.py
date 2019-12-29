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


class IncludeDirective:
    @classmethod
    def from_tokens(cls, tokens: List[Token], identifier_table: IdentifierTable):
        path = expect_token(tokens[0], {TokenType.STRING_LITERAL, TokenType.IDENTIFIER})

        if path.type is TokenType.STRING_LITERAL:
            return cls(path.value.group(1), path.value.group(0).startswith("\""))

        raise NotImplementedError("Parsing include from identifier is not yet implemented")

    def __init__(self, path: str, expanded: bool):
        self.path = path
        self.expanded = expanded


def parse_line(tokens: List[Token], identifier_table: IdentifierTable):
    directive = expect_token(tokens[0], TokenType.DIRECTIVE)

    if directive.value.group(1) == "include":
        return IncludeDirective.from_tokens(tokens[1:], identifier_table)
    
    raise NotImplementedError(f"Parsing directive {directive.value.group(1)} is not yet implemented")
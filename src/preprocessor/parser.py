from typing import Union, Iterable, Dict, List, Optional, Set, Iterator
from itertools import takewhile
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


def parse_identifier_list(tokens: Iterable[Token]) -> Iterable[Token]:
    """
    Parses an expression of LPAREN (IDENTIFIER COMMA)* RPAREN
    """

    expect_token(tokens[0], TokenType.LPAREN)
    cursor = 1
    rv = []

    while cursor < len(tokens):
        rv.append(expect_token(tokens[cursor]), TokenType.IDENTIFIER)
        n = expect_token(tokens[cursor + 1], {TokenType.COMMA, TokenType.RPAREN})

        if n.type is TokenType.RPAREN:
            break

        cursor += 2

    return rv


def expect_token(token: Token, expectation: Union[TokenType, Iterable[TokenType], Set[TokenType]]) -> Token:
    if type(expectation) is not set:
        try:
            expectation = set(expectation)
        except TypeError:
            expectation = {expectation, }

    if token.type not in expectation:
        raise ValueError("Expected {token} to be of type {expected}")

    return token


def peek_token(tokens: List[Token], expectation: Union[TokenType, Set[TokenType]], i: int = 0) -> bool:
    """Looks at the type of the ith token in the list and compares it to expected set."""
    if type(expectation) is not set:
        expectation = {expectation, }
    
    return tokens[i].type in expectation


class IncludeDirective:
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        first = expect_token(tokens[0], {TokenType.STRING_LITERAL, TokenType.OP_LT, TokenType.IDENTIFIER})

        if first.type is TokenType.IDENTIFIER:
            raise NotImplementedError("Include directives from identifiers are not yet implemented")

        if first.type is TokenType.OP_LT:
            path_tokens: Iterator[Token] = takewhile(lambda t: t.type != TokenType.OP_GT, tokens[1:])
            path = "".join(t.value.group() for t in path_tokens)

            if len(path) == 0:
                raise Exception("Cannot have empty path")

            return cls(path, False)
        elif first.type is TokenType.STRING_LITERAL:
            return cls(first.value.group(1), True)

    def __init__(self, path: str, expanded: bool):
        self.path = path
        self.expanded = expanded

    def __repr__(self):
        return f"IncludeDirective(path={self.path}, expanded={self.expanded})"

    def __eq__(self, o):
        return self.path == o.path and self.expanded == o.expanded


def parse_line(tokens: List[Token]):
    directive = expect_token(tokens[0], TokenType.DIRECTIVE)

    if directive.value.group(1) == "include":
        return IncludeDirective.from_tokens(tokens[1:])
    
    raise NotImplementedError(f"Parsing directive {directive.value.group(1)} is not yet implemented")
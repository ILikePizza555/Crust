"""
Defines objects and functions that act on tokens.

Note that the primary purpose of the parser to is *organize* tokens, not evaluate them.
"""
from typing import Union, Iterable, Dict, List, Set, Iterator
from itertools import takewhile
from .tokenizer import TokenType, Token


Literal = Union[str, int, float]
IdentifierTable = Dict[str, Literal]


def parse_identifier_list(tokens: Iterable[Token]) -> Iterable[Token]:
    """
    Parses an expression of LPAREN (IDENTIFIER COMMA)* RPAREN
    """

    expect_token(tokens[0], TokenType.LPAREN)
    cursor = 1
    rv = []

    while cursor < len(tokens):
        rv.append(expect_token(tokens[cursor], TokenType.IDENTIFIER))
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
        raise ValueError(f"Expected {token} to be of type {expectation}")

    return token


def peek_token(tokens: List[Token], expectation: Union[TokenType, Set[TokenType]], i: int = 0) -> bool:
    """Looks at the type of the ith token in the list and compares it to expected set."""
    if type(expectation) is not set:
        expectation = {expectation, }

    return tokens[i].type in expectation


class IncludeDirective:
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        first = expect_token(tokens[0], {TokenType.STRING_LITERAL, TokenType.OP_LT})

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


class DifferedIncludeDirective:
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        return cls(expect_token(tokens[0], TokenType.IDENTIFIER).value.group())

    def __init__(self, identifier: str):
        self.identifier = identifier


class ObjectMacro:
    """
    Mapping of a sequence of tokens to an identifier
    """
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        identifier = expect_token(tokens[0], TokenType.IDENTIFIER)
        return cls(identifier.value.group(), tokens[1:])

    def __init__(self, identifier: str, tokens: List[Token]):
        self.identifier = identifier
        self.tokens = tokens

    def __repr__(self):
        return f"ObjectMacro(identifier={self.identifier}, tokens={self.tokens})"

    def __eq__(self, o):
        return self.identifier == o.identifier and self.tokens == o.tokens


class FunctionMacro:
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        identifer = expect_token(tokens[0], TokenType.IDENTIFIER)
        params = parse_identifier_list(tokens[1:])
        expression = tokens[2 + 2 * len(params):]

        return cls(identifer.value.group(), tuple(t.value.group() for t in params), expression)

    def __init__(self, identifier: str, params: Iterable[str], expression: Iterable[Token]):
        self.identifier = identifier
        self.params = params
        self.expression = expression

    def __repr__(self):
        return f"FunctionMacro(identifier={self.identifier}, params={self.params}, expression={self.expression})"

    def __eq__(self, o):
        return self.identifier == o.identifier and self.params == o.params and self.expression == o.expression


ASTObject = Union[IncludeDirective, DifferedIncludeDirective, ObjectMacro, FunctionMacro]


def parse_line(tokens: List[Token]) -> ASTObject:
    directive = expect_token(tokens[0], TokenType.DIRECTIVE)

    if directive.value.group(1) == "include":
        if tokens[1].type is TokenType.IDENTIFIER:
            return DifferedIncludeDirective.from_tokens(tokens[1:])
        return IncludeDirective.from_tokens(tokens[1:])
    if directive.value.group(1) == "define":
        if tokens[2].type is TokenType.LPAREN:
            return FunctionMacro.from_tokens(tokens[1:])
        return ObjectMacro.from_tokens(tokens[1:])

    raise NotImplementedError(f"Parsing directive {directive.value.group(1)} is not yet implemented")
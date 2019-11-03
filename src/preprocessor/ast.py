"""
Contains class definitions that make up an AST
"""
from typing import Union, List, Optional, Set
from .exceptions import UnexpectedTokenError, UnknownPreprocessorDirectiveError, PreprocessorSyntaxError
from .tokenizer import Token, TokenType
from .shunting_yard import shunting_yard_algorithmn


def _expect_token(tokens: List[Token], expected_types: Set[TokenType], pos: int = 0) -> Token:
    """
    Asserts that the `pos` token in the list is one of `expected_types`.
    If it is, it is removed from the list and returned
    """
    peek = tokens[pos]

    if peek.token_type not in expected_types:
        raise UnexpectedTokenError(peek, expected_types)

    return tokens.pop(pos)


def _expect_directive(tokens: List[Token], name: str, pos: int = 0) -> Token:
    peek = tokens[pos]

    if peek.token_type is not TokenType.DIRECTIVE:
        raise UnexpectedTokenError(peek, {TokenType.DIRECTIVE})

    if peek.match.group(1) != name:
        raise UnknownPreprocessorDirectiveError(peek.line, peek.match.group(1))

    return tokens.pop(pos)


class Expression:
    """
    Class representation of an expression
    """

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        output_stack = shunting_yard_algorithmn(tokens)
        return cls(output_stack)

    def __init__(self, expression_stack: List[Token]):
        self.expression_stack = expression_stack


class ObjectMacro:
    """
    Class representation of an object macro
    """

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """
        Parses the following syntax:
        IDENTIFIER TOKENS*
        """
        name_token = _expect_token(tokens, {TokenType.IDENTIFIER, })
        remainder = tokens

        return cls(name_token.match.group(), remainder)

    def __init__(self, identifier: str, value: List[Token]):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return f"ObjectMacro(identifier={self.identifier}, value={self.value})"

    def __eq__(self, o):
        return self.identifier == o.identifier and self.value == o.value


class FunctionMacro:
    """
    Class representation of a function macro
    """
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """
        Parses the following syntax:
        IDENTIFIER (IDENTIFIER [, IDENTIFIER]*) TOKENS*
        """
        identifier = _expect_token(tokens, {TokenType.IDENTIFIER, })
        _expect_token(tokens, {TokenType.LPARAN, })
        parameters = []

        while tokens:
            parameters.append(_expect_token(tokens, {TokenType.IDENTIFIER, }))

            try:
                e = _expect_token(tokens, {TokenType.COMMA, TokenType.RPARAN})
            except IndexError:
                raise PreprocessorSyntaxError(identifier.line, 0, "Expected comma or closing parenthesis.")

            if e.token_type == TokenType.RPARAN:
                break

        return cls(
            identifier.match.group(),
            [x.match.group() for x in parameters],
            tokens
        )

    def __init__(self, identifier: str, parameters: List[str], value: List[Token]):
        self.identifier = identifier
        self.parameters = parameters
        self.value = value

    def __repr__(self):
        return f"FunctionMacro(identifier={self.identifier}, parameters={self.parameters}, value={self.value})"

    def __eq__(self, other):
        return (
            self.identifier == other.identifier and
            self.parameters == other.parameters and
            self.value == other.value
        )


class EvaluatedInclude:
    """
    Class representation of a normal include directive.
    """

    @classmethod
    def from_tokens(cls, token_list: List[Token]) -> "EvaluatedInclude":
        parameter_tok = _expect_token(token_list, {TokenType.FILENAME, TokenType.STRING})

        return cls(parameter_tok.match.group(1), parameter_tok.token_type is TokenType.STRING)

    def __init__(self, include_path: str, expanded_include: bool):
        self.include_path = include_path
        self.expanded_include = expanded_include

    def __eq__(self, other):
        return (
            self.include_path == other.include_path and
            self.expanded_include == other.expanded_include
        )

    def __repr__(self):
        return f"EvaluatedInclude(include_path={self.include_path}, expanded_include={self.expanded_include})"


class DeferedInclude:
    """
    Include directive that uses an indentifier as it's parameter. We don't know what it includes
    until we can evaluate the identifier.
    """
    def __init__(self, identifier: Token):
        self.identifier = identifier


class ConditionalBranch:
    """
    Pairs an optional expression with children nodes
    """
    def __init__(self, children: List[any], condition: Optional[Expression]):
        self.children = children
        self.condition = condition


ASTObject = Union[Expression, ObjectMacro, FunctionMacro, EvaluatedInclude, DeferedInclude, ConditionalBranch]

from typing import List, Set
from .tokenizer import Token, TokenType, VALUE_TOKENS, COMPARISON_OP_TOKENS


class PreprocessorSyntaxError(Exception):
    def __init__(self, line_number, column_number, message):
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        return f"Syntax error on line {self.line_number}, {self.column_number}: {self.message}"


def _expect_token(tokens: List[Token], expected_types: Set[TokenType], pos: int = 0) -> Token:
    """
    Asserts that the `pos` token in the list is one of `expected_types`.
    If it is, it is removed from the list and returned
    """
    peek = tokens[pos]

    if peek.token_type not in expected_types:
        raise PreprocessorSyntaxError(peek.line, peek.col, f"Expected one of {expected_types}")

    return tokens.pop(pos)


class ComparisonExpression:
    """
    Represents an expression that compares two values together.

    Reads all tokens of the form:
    (CONST | IDENTIFIER) (== or <= or >= or < or >) (CONST | IDENTIFIER)
    """
    @classmethod
    def from_tokens(cls, token_list: List[Token]) -> "ComparisonExpression":
        lhs = _expect_token(token_list, VALUE_TOKENS)
        op = _expect_token(token_list, COMPARISON_OP_TOKENS)
        rhs = _expect_token(token_list, VALUE_TOKENS)

        return cls(op, lhs, rhs)

    def __init__(self, op: Token, lhs: Token, rhs: Token):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs


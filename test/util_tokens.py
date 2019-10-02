from typing import List
from src.preprocessor.tokenizer import Token, TokenType


def assert_token_equals(actual: Token, type: TokenType, line=None, col=None, matched=None):
    """Helper function to test token equality"""
    assert actual.token_type is type

    if line is not None:
        assert actual.line == line

    if col is not None:
        assert actual.col == col

    if matched is not None:
        assert actual.match.group() == matched


def assert_token_lists_equal(actual: List[Token], expected: List[dict]):
    assert len(actual) == len(expected)

    for a, e in zip(actual, expected):
        assert_token_equals(a, **e)

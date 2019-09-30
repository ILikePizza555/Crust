import pytest
from typing import Tuple
from .test_preprocessor_tokenizer import assert_token_lists_equal
from src.useful import StringCursor
from src.preprocessor.tokenizer import tokenize_line, TokenType
from src.preprocessor.parser import Expression


EXPRESSION_TEST_DATA = (
    (
        "identifier is an expression",
        "# FOOBAR",
        ((TokenType.IDENTIFIER, "FOOBAR"),)
    ),
    (
        "single operator expression",
        "# 45 <= 51",
        (
            (TokenType.INTEGER_CONST, "45"), (TokenType.INTEGER_CONST, "51"), (TokenType.LESS_THAN_OR_EQUAL, "<=")
        )
    ),
    (
        "multi operator expression",
        "# 45 <= 51 && defined FOOBAR",
        (
            (TokenType.INTEGER_CONST, "45"), (TokenType.INTEGER_CONST, "51"),
            (TokenType.LESS_THAN_OR_EQUAL, "<="),
            (TokenType.IDENTIFIER, "FOOBAR"),
            (TokenType.DEFINED, "defined")
        )
    ),
    (
        "complex expression",
        "# ! (defined FOOBAR || !(FOOBAR2 == 1 && FOOBAR3 <= 0)) && FOOBAR3 >= 45",
        (
            (TokenType.IDENTIFIER, "FOOBAR"), (TokenType.DEFINED, "defined"),
            (TokenType.IDENTIFIER, "FOOBAR2"), (TokenType.INTEGER_CONST, "1"), (TokenType.EQUAL, "=="),
            (TokenType.IDENTIFIER, "FOOBAR3"), (TokenType.INTEGER_CONST, "0"), (TokenType.LESS_THAN_OR_EQUAL, "<="),
            (TokenType.AND, "&&"), (TokenType.NOT, "!"),
            (TokenType.OR, "||"), (TokenType.NOT, "!"),
            (TokenType.IDENTIFIER, "FOOBAR3"), (TokenType.INTEGER_CONST, "45"), (TokenType.GREATER_THAN_OR_EQUAL, ">="),
            (TokenType.AND, "&&")
        )
    )
)


def map_expression_data(data: Tuple[str, str, Tuple[Tuple[TokenType, str]]]):
    tokens = tokenize_line(StringCursor(data[1]), 0)[0]
    expected_stack = tuple({"type": s[0], "matched": s[1]} for s in data[2])
    return (tokens, expected_stack)


@pytest.mark.parametrize(
    "test_tokens, expected_stack",
    argvalues=[map_expression_data(data) for data in EXPRESSION_TEST_DATA],
    ids=[data[0] for data in EXPRESSION_TEST_DATA])
def test_expression_from_tokens(test_tokens, expected_stack):
    actual = Expression.from_tokens(test_tokens)

    assert_token_lists_equal(actual.expression_stack, expected_stack)
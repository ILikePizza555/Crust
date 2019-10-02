import pytest
from .util_testdata import TestData, test_data_to_names, test_data_to_parameters
from .util_tokens import assert_token_lists_equal, tokenize_string
from src.preprocessor.parser import Expression, ObjectMacro
from src.preprocessor.tokenizer import TokenType, Token


EXPRESSION_TEST_DATA = (
    TestData(
        "identifier is an expression",
        tokenize_string("# FOOBAR"),
        ((TokenType.IDENTIFIER, "FOOBAR"),)
    ),
    TestData(
        "single operator expression",
        tokenize_string("# 45 <= 51"),
        (
            (TokenType.INTEGER_CONST, "45"), (TokenType.INTEGER_CONST, "51"), (TokenType.LESS_THAN_OR_EQUAL, "<=")
        )
    ),
    TestData(
        "multi operator expression",
        tokenize_string("# 45 <= 51 && defined FOOBAR"),
        (
            (TokenType.INTEGER_CONST, "45"), (TokenType.INTEGER_CONST, "51"),
            (TokenType.LESS_THAN_OR_EQUAL, "<="),
            (TokenType.IDENTIFIER, "FOOBAR"),
            (TokenType.DEFINED, "defined"),
            (TokenType.AND, "&&")
        )
    ),
    TestData(
        "complex expression",
        tokenize_string("# ! (defined FOOBAR || !(FOOBAR2 == 1 && FOOBAR3 <= 0)) && FOOBAR3 >= 45"),
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


@pytest.mark.parametrize(
    "test_tokens, expected_stack",
    argvalues=test_data_to_parameters(EXPRESSION_TEST_DATA),
    ids=test_data_to_names(EXPRESSION_TEST_DATA))
def test_expression_from_tokens(test_tokens, expected_stack):
    actual = Expression.from_tokens(test_tokens)

    assert_token_lists_equal(actual.expression_stack, expected_stack)


def test_objectmacro_tokens():
    TEST_DATA = TestData(
        "normal",
        tokenize_string("# FOOBAR 64")[1:],
        ObjectMacro("FOOBAR", [Token(TokenType.INTEGER_CONST, 0, 9, "64")])
    )

    actual = ObjectMacro.from_tokens(TEST_DATA.input_data)
    assert actual == TEST_DATA.expected

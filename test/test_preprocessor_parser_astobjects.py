import pytest
from .util_testdata import TestData, convert_to_names, convert_to_parameters
from .util_tokens import MockToken, assert_token_lists_equal, tokenize_string
from src.preprocessor.parser import Expression, ObjectMacro, FunctionMacro, EvaluatedInclude, PreprocessorSyntaxError
from src.preprocessor.tokenizer import TokenType


EXPRESSION_TEST_DATA = (TestData.of_mock_tokens(*x) for x in (
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
            (TokenType.DEFINED, "defined"),
            (TokenType.AND, "&&")
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
))


@pytest.mark.parametrize(
    "test_tokens, expected_stack",
    argvalues=convert_to_parameters(EXPRESSION_TEST_DATA),
    ids=convert_to_names(EXPRESSION_TEST_DATA))
def test_expression_from_tokens(test_tokens, expected_stack):
    actual = Expression.from_tokens(test_tokens)

    assert_token_lists_equal(actual.expression_stack, expected_stack)


def test_objectmacro_tokens():
    TEST_DATA = TestData(
        "normal",
        tokenize_string("# FOOBAR 64"),
        ObjectMacro("FOOBAR", [MockToken(TokenType.INTEGER_CONST, "64", 0, 9)])
    )

    actual = ObjectMacro.from_tokens(TEST_DATA.input_data)
    assert actual == TEST_DATA.expected


def test_functionmacro_tokens():
    TEST_DATA = TestData(
        "normal",
        tokenize_string("# FOO(BAR, BAZ) BAR,BAZ"),
        FunctionMacro("FOO", ["BAR", "BAZ"], [MockToken(*x) for x in (
                (TokenType.IDENTIFIER, "BAR"), (TokenType.COMMA, ","), (TokenType.IDENTIFIER, "BAZ")
            )]
        )
    )

    actual = FunctionMacro.from_tokens(TEST_DATA.input_data)
    assert actual == TEST_DATA.expected


def test_functionmacro_tokens_incomplete():
    input_data = tokenize_string("# FOO(BAR, BAZ, ERROR")

    with pytest.raises(PreprocessorSyntaxError):
        FunctionMacro.from_tokens(input_data)


EVALUATED_INCLUDE_TEST_DATA = (
    TestData(
        "unexpanded",
        tokenize_string("#include <stdio.h>"),
        EvaluatedInclude("stdio.h", False)
    ),
    TestData(
        "expanded",
        tokenize_string("#include \"localprojectfile.h\""),
        EvaluatedInclude("localprojectfile.h", True)
    )
)


@pytest.mark.parametrize(
    "input_tokens,expected",
    argvalues=convert_to_parameters(EVALUATED_INCLUDE_TEST_DATA),
    ids=convert_to_names(EVALUATED_INCLUDE_TEST_DATA)
)
def test_evaluatedinclude_tokens(input_tokens, expected):
    actual = EvaluatedInclude.from_tokens(input_tokens)
    assert actual == expected

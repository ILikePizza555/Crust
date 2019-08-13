import pytest # NOQA
from src.preprocessor import Token, TokenType, _parse_include, _parse_identifier_list, CallExpression, Macro

TOK_LPARAN = Token(TokenType.LPARAN, 0, 0, "(")
TOK_RPARAN = Token(TokenType.RPARAN, 0, 0, ")")
TOK_COMMA = Token(TokenType.COMMA, 0, 0, ",")

PARSE_INCLUDE_TEST_DATA = [
    ("system import", [Token(TokenType.FILENAME, 0, 0, "<stdio.h>")], (None, "stdio.h")),
    ("local import", [Token(TokenType.STRING, 0, 0, "\"local_file.h\"")], ("local_file.h", None))]


@pytest.mark.parametrize(
    "tokens,expected",
    argvalues=[x[1:3] for x in PARSE_INCLUDE_TEST_DATA],
    ids=[x[0] for x in PARSE_INCLUDE_TEST_DATA]
)
def test_parse_include(tokens, expected):
    actual = _parse_include(tokens)
    assert actual == expected


@pytest.mark.xfail(reason="Currently not supported")
def test_parse_include_with_macro_replacement():
    TOKENS = [Token(TokenType.IDENTIFIER, 0, 0, "TEST_MACRO")]
    MACRO_TABLE = {"TEST_MACRO": "<stdio.h>"}

    actual = _parse_include(TOKENS, MACRO_TABLE)
    assert actual == (None, "stdio.h")


IDLIST_TEST_DATA = [
    ("Empty list", [], [Token(TokenType.LPARAN, 0, 0, "("), Token(TokenType.RPARAN, 0, 0, ")")]),
    ("Two entry List", ["ID1", "ID2"], [
        TOK_LPARAN,
        Token(TokenType.IDENTIFIER, 0, 0, "ID1"),
        Token(TokenType.COMMA, 0, 0, ","),
        Token(TokenType.IDENTIFIER, 0, 0, "ID2"),
        TOK_RPARAN
    ])
]


@pytest.mark.parametrize(
    "expected,tokens",
    argvalues=[x[1:3] for x in IDLIST_TEST_DATA],
    ids=[x[0] for x in IDLIST_TEST_DATA]
)
def test_parse_identifier_list(expected, tokens):
    actual = _parse_identifier_list(tokens)
    assert actual == expected


PARSE_CALLEXPR_TEST_DATA = [
    ("No arguments", CallExpression("TEST_CALL", []), [
        Token(TokenType.IDENTIFIER, 0, 0, "TEST_CALL"),
        TOK_LPARAN,
        TOK_RPARAN
    ]),
    ("One argument", CallExpression("TEST_CALL", [Token(TokenType.IDENTIFIER, 0, 0, "TEST_PARAM")]), [
        Token(TokenType.IDENTIFIER, 0, 0, "TEST_CALL"),
        TOK_LPARAN,
        Token(TokenType.IDENTIFIER, 0, 0, "TEST_PARAM"),
        TOK_RPARAN
    ]),
    ("Several arguments",
        CallExpression("TEST_CALL", [
                Token(TokenType.INTEGER_CONST, 0, 0, "42069"),
                Token(TokenType.IDENTIFIER, 0, 0, "Trans Girls are good girls")
            ]
        ),
        [
            Token(TokenType.IDENTIFIER, 0, 0, "TEST_CALL"),
            TOK_LPARAN,
            Token(TokenType.INTEGER_CONST, 0, 0, "42069"),
            TOK_COMMA,
            Token(TokenType.IDENTIFIER, 0, 0, "Trans Girls are good girls"),
            TOK_RPARAN
        ]),
    ("Nested calls", 
        CallExpression("TEST_NESTED", [
                Token(TokenType.CHAR_CONST, 0, 0, "'c'"),
                CallExpression("TEST_NESTED2", [Token(TokenType.IDENTIFIER, 0, 0, "NESTED_ARG")])
            ]
        ),
        [
            Token(TokenType.IDENTIFIER, 0, 0, "TEST_NESTED"),
            TOK_LPARAN,
            Token(TokenType.CHAR_CONST, 0, 0, "'c'"),
            TOK_COMMA,
            Token(TokenType.IDENTIFIER, 0, 0, "TEST_NESTED2"),
            TOK_LPARAN,
            Token(TokenType.IDENTIFIER, 0, 0, "NESTED_ARG"),
            TOK_RPARAN,
            TOK_RPARAN
        ])
]


@pytest.mark.parametrize(
    "expected,tokens",
    argvalues=[x[1:3] for x in PARSE_CALLEXPR_TEST_DATA],
    ids=[x[0] for x in PARSE_CALLEXPR_TEST_DATA]
)
def test_parse_call_expression(expected, tokens):
    actual = CallExpression.from_tokens(tokens)
    assert actual == expected


PARSE_MACRO_TEST_DATA = [
    ("Simple macro", Macro("TEST_MACRO", Token(TokenType.INTEGER_CONST, 0, 0, "1234")), [
        Token(TokenType.IDENTIFIER, 0, 0, "TEST_MACRO"),
        Token(TokenType.INTEGER_CONST, 0, 0, "1234")
    ])
]


@pytest.mark.parametrize(
    "expected,tokens",
    argvalues=[x[1:3] for x in PARSE_MACRO_TEST_DATA],
    ids=[x[0] for x in PARSE_MACRO_TEST_DATA]
)
def test_parse_macro(expected, tokens):
    actual = Macro.from_tokens(tokens)
    assert actual == expected

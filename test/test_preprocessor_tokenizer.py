import pytest # NOQA
from src.preprocessor.tokenizer import tokenize_line, Token, TokenType, _tokenize_directive, UnknownTokenError
from src.useful import StringCursor


def assert_token_equals(token: Token, type: TokenType, line: int, col: int, matched: str):
    """Helper function to test token equality"""
    assert token.token_type is type
    assert token.line == line
    assert token.col == col
    assert token.match.group() == matched


def assert_token_lists_equal(actual: list, expected: list):
    assert len(actual) == len(expected)

    for a, e in zip(actual, expected):
        assert_token_equals(a, *e)


def test_tokenize_directive_valid_input():
    cursor = StringCursor("#include <iostream>")
    actual = _tokenize_directive(cursor, 0)

    assert_token_equals(actual, TokenType.DIRECTIVE, 0, 1, "#include")
    assert cursor.position == 8


def test_tokenize_directive_null():
    cursor = StringCursor("# the rest of this should not be read")
    actual = _tokenize_directive(cursor, 0)

    assert_token_equals(actual, TokenType.DIRECTIVE, 0, 1, "#")
    assert cursor.position == 1


def test_tokenize_directive_error():
    cursor = StringCursor("this input throws an error")
    with pytest.raises(UnknownTokenError):
        _tokenize_directive(cursor, 0)


test_data = [
    ("Null directive", "#\n", 0, [(TokenType.DIRECTIVE, 0, 1, "#")]),
    ("No parameter directive", "#pragma\n", 0, [(TokenType.DIRECTIVE, 0, 1, "#pragma")]),
    ("Integer constant", "#define TEST_INT 1234\n", 4, [
        (TokenType.DIRECTIVE, 4, 1, "#define"),
        (TokenType.IDENTIFIER, 4, 8, "TEST_INT"),
        (TokenType.INTEGER_CONST, 4, 17, "1234")
    ]),
    ("Character constant", "#define TEST_CHAR 's'\n", 5, [
        (TokenType.DIRECTIVE, 5, 1, "#define"),
        (TokenType.IDENTIFIER, 5, 8, "TEST_CHAR"),
        (TokenType.CHAR_CONST, 5, 18, "'s'")
    ]),
    ("Function macro", "#define FMACRO(name) typedef struct name##_s name##_t\n", 6, [
        (TokenType.DIRECTIVE, 6, 1, "#define"),
        (TokenType.IDENTIFIER, 6, 8, "FMACRO"),
        (TokenType.LPARAN, 6, 14, "("),
        (TokenType.IDENTIFIER, 6, 15, "name"),
        (TokenType.RPARAN, 6, 19, ")"),
        (TokenType.IDENTIFIER, 6, 21, "typedef"),
        (TokenType.IDENTIFIER, 6, 29, "struct"),
        (TokenType.IDENTIFIER, 6, 36, "name"),
        (TokenType.TOKEN_CONCATINATION, 6, 40, "##"),
        (TokenType.IDENTIFIER, 6, 42, "_s"),
        (TokenType.IDENTIFIER, 6, 45, "name"),
        (TokenType.TOKEN_CONCATINATION, 6, 49, "##"),
        (TokenType.IDENTIFIER, 6, 51, "_t")
    ]),
    ("Conditional statement", "#if X <= 5\n", 7, [
        (TokenType.DIRECTIVE, 7, 1, "#if"),
        (TokenType.IDENTIFIER, 7, 4, "X"),
        (TokenType.LESS_THAN_OR_EQUAL, 7, 6, "<="),
        (TokenType.INTEGER_CONST, 7, 9, "5")
    ]),
    ("Include statement", "#include <stdio.h>\n", 8, [
        (TokenType.DIRECTIVE, 8, 1, "#include"),
        (TokenType.FILENAME, 8, 9, "<stdio.h>")
    ]),
    ("Conditionals aren't files", "#pragma 34 <= TEST_1 || TEST_2 > 55\n", 9, [
        (TokenType.DIRECTIVE, 9, 1, "#pragma"),
        (TokenType.INTEGER_CONST, 9, 8, "34"),
        (TokenType.LESS_THAN_OR_EQUAL, 9, 11, "<="),
        (TokenType.IDENTIFIER, 9, 14, "TEST_1"),
        (TokenType.OR, 9, 21, "||"),
        (TokenType.IDENTIFIER, 9, 24, "TEST_2"),
        (TokenType.GREATER_THAN, 9, 31, ">"),
        (TokenType.INTEGER_CONST, 9, 33, "55")
    ])
]


@pytest.mark.parametrize(
    "line_str,line_number,expected",
    argvalues=[x[1:4] for x in test_data],
    ids=[x[0] for x in test_data])
def test_tokenize_line(line_str, line_number, expected):
    cursor = StringCursor(line_str)

    actual_list, line_offset = tokenize_line(cursor, line_number)
    assert_token_lists_equal(actual_list, expected)


def test_tokenize_line_escaped_line_endings():
    cursor = StringCursor("#define TEST_LIST a, \\\n\tb, \\\n\tc\n")
    actual_list, line_offset = tokenize_line(cursor, 0)

    expected_list = [
        (TokenType.DIRECTIVE, 0, 1, "#define"),
        (TokenType.IDENTIFIER, 0, 8, "TEST_LIST"),
        (TokenType.IDENTIFIER, 0, 18, "a"),
        (TokenType.COMMA, 0, 19, ","),
        (TokenType.IDENTIFIER, 1, 24, "b"),
        (TokenType.COMMA, 1, 25, ","),
        (TokenType.IDENTIFIER, 2, 30, "c")
    ]

    assert_token_lists_equal(actual_list, expected_list)
    assert line_offset == 3
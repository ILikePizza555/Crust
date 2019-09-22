import pytest # NOQA
from src.preprocessor.tokenizer import tokenize_line, Token, TokenType, _tokenize_directive, UnknownTokenError
from src.useful import StringCursor


def test_tokenize_directive_valid_input():
    cursor = StringCursor("#include <iostream>")
    actual = _tokenize_directive(cursor, 0)

    assert actual == Token(TokenType.DIRECTIVE, 0, 1, "include")
    assert cursor.position == 8


def test_tokenize_directive_null():
    cursor = StringCursor("# the rest of this should not be read")
    actual = _tokenize_directive(cursor, 0)

    assert actual == Token(TokenType.DIRECTIVE, 0, 1, "")
    assert cursor.position == 1


def test_tokenize_directive_error():
    cursor = StringCursor("this input throws an error")
    with pytest.raises(UnknownTokenError):
        _tokenize_directive(cursor, 0)


test_data = [
    ("Null directive", "#\n", 0, [Token(TokenType.DIRECTIVE, 0, 1, "")]),
    ("No parameter directive", "#pragma\n", 0, [Token(TokenType.DIRECTIVE, 0, 1, "pragma")]),
    ("Integer constant", "#define TEST_INT 1234\n", 4, [
        Token(TokenType.DIRECTIVE, 4, 1, "define"),
        Token(TokenType.IDENTIFIER, 4, 8, "TEST_INT"),
        Token(TokenType.INTEGER_CONST, 4, 17, "1234")
    ]),
    ("Character constant", "#define TEST_CHAR 's'\n", 5, [
        Token(TokenType.DIRECTIVE, 5, 1, "define"),
        Token(TokenType.IDENTIFIER, 5, 8, "TEST_CHAR"),
        Token(TokenType.CHAR_CONST, 5, 18, "'s'")
    ]),
    ("Function macro", "#define FMACRO(name) typedef struct name##_s name##_t\n", 6, [
        Token(TokenType.DIRECTIVE, 6, 1, "define"),
        Token(TokenType.IDENTIFIER, 6, 8, "FMACRO"),
        Token(TokenType.LPARAN, 6, 14, "("),
        Token(TokenType.IDENTIFIER, 6, 15, "name"),
        Token(TokenType.RPARAN, 6, 19, ")"),
        Token(TokenType.IDENTIFIER, 6, 21, "typedef"),
        Token(TokenType.IDENTIFIER, 6, 29, "struct"),
        Token(TokenType.IDENTIFIER, 6, 36, "name"),
        Token(TokenType.TOKEN_CONCATINATION, 6, 40, "##"),
        Token(TokenType.IDENTIFIER, 6, 42, "_s"),
        Token(TokenType.IDENTIFIER, 6, 45, "name"),
        Token(TokenType.TOKEN_CONCATINATION, 6, 49, "##"),
        Token(TokenType.IDENTIFIER, 6, 51, "_t")
    ]),
    ("Conditional statement", "#if X <= 5\n", 7, [
        Token(TokenType.DIRECTIVE, 7, 1, "if"),
        Token(TokenType.IDENTIFIER, 7, 4, "X"),
        Token(TokenType.LESS_THAN_OR_EQUAL, 7, 6, "<="),
        Token(TokenType.INTEGER_CONST, 7, 9, "5")
    ]),
    ("Include statement", "#include <stdio.h>\n", 8, [
        Token(TokenType.DIRECTIVE, 8, 1, "include"),
        Token(TokenType.FILENAME, 8, 9, "<stdio.h>")
    ]),
    ("Conditionals aren't files", "#pragma 34 <= TEST_1 || TEST_2 > 55\n", 9, [
        Token(TokenType.DIRECTIVE, 9, 1, "pragma"),
        Token(TokenType.INTEGER_CONST, 9, 8, "34"),
        Token(TokenType.LESS_THAN_OR_EQUAL, 9, 11, "<="),
        Token(TokenType.IDENTIFIER, 9, 14, "TEST_1"),
        Token(TokenType.OR, 9, 21, "||"),
        Token(TokenType.IDENTIFIER, 9, 24, "TEST_2"),
        Token(TokenType.GREATER_THAN, 9, 31, ">"),
        Token(TokenType.INTEGER_CONST, 9, 33, "55")
    ])
]


@pytest.mark.parametrize(
    "line_str,line_number,expected",
    argvalues=[x[1:4] for x in test_data],
    ids=[x[0] for x in test_data])
def test_tokenize_line(line_str, line_number, expected):
    cursor = StringCursor(line_str)

    actual, line_offset = tokenize_line(cursor, line_number)
    assert actual == expected


def test_tokenize_line_escaped_line_endings():
    cursor = StringCursor("#define TEST_LIST a, \\\n\tb, \\\n\tc\n")
    actual, line_offset = tokenize_line(cursor, 0)

    assert actual == [
        Token(TokenType.DIRECTIVE, 0, 1, "define"),
        Token(TokenType.IDENTIFIER, 0, 8, "TEST_LIST"),
        Token(TokenType.IDENTIFIER, 0, 18, "a"),
        Token(TokenType.COMMA, 0, 19, ","),
        Token(TokenType.IDENTIFIER, 1, 24, "b"),
        Token(TokenType.COMMA, 1, 25, ","),
        Token(TokenType.IDENTIFIER, 2, 30, "c")]
    assert line_offset == 3
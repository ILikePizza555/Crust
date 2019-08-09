import pytest # NOQA
from src.preprocessor import _tokenize_line, Token, TokenType


test_data = [
    ("Empty String", "", 0, None),
    ("Null directive", "#", 0, [Token(TokenType.DIRECTIVE, 0, 1, "")]),
    ("No parameter directive", "#pragma", 0, [Token(TokenType.DIRECTIVE, 0, 1, "pragma")]),
    ("Integer constant", "#define TEST_INT 1234", 4, [
        Token(TokenType.DIRECTIVE, 4, 1, "define"),
        Token(TokenType.IDENTIFIER, 4, 8, "TEST_INT"),
        Token(TokenType.INTEGER_CONST, 4, 17, "1234")
    ]),
    ("Character constant", "#define TEST_CHAR 's'", 5, [
        Token(TokenType.DIRECTIVE, 5, 1, "define"),
        Token(TokenType.IDENTIFIER, 5, 8, "TEST_CHAR"),
        Token(TokenType.CHAR_CONST, 5, 18, "'s'")
    ]),
    ("Function macro", "#define FMACRO(name) typedef struct name##_s name##_t", 6, [
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
    ("Conditional statement", "#if X <= 5", 7, [
        Token(TokenType.DIRECTIVE, 7, 1, "if"),
        Token(TokenType.IDENTIFIER, 7, 4, "X"),
        Token(TokenType.LESS_THAN_OR_EQUAL, 7, 6, "<="),
        Token(TokenType.INTEGER_CONST, 7, 9, "5")
    ]),
    ("Include statement", "#include <stdio.h>", 8, [
        Token(TokenType.DIRECTIVE, 8, 1, "include"),
        Token(TokenType.FILENAME, 8, 9, "<stdio.h>")
    ])
]


@pytest.mark.parametrize(
    "line_str,line_num,expected",
    argvalues=[x[1:4] for x in test_data],
    ids=[x[0] for x in test_data])
def test_tokenizer(line_str, line_num, expected):
    actual = _tokenize_line(line_str, line_num)
    assert actual == expected

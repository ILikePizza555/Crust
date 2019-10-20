import pytest # NOQA
from pathlib import Path
from src.preprocessor.tokenizer import tokenize_line, tokenize_file, TokenType, _tokenize_directive, UnknownTokenError
from src.useful import StringCursor
from .util_tokens import MockToken, assert_token_equals, assert_token_lists_equal


def test_tokenize_directive_valid_input():
    cursor = StringCursor("#include <iostream>")
    actual = _tokenize_directive(cursor, 0)
    EXPECTED = MockToken(TokenType.DIRECTIVE, "#include", 0, 1)

    assert_token_equals(actual, EXPECTED)
    assert cursor.position == 8


def test_tokenize_directive_null():
    cursor = StringCursor("# the rest of this should not be read")
    actual = _tokenize_directive(cursor, 0)
    EXPECTED = MockToken(TokenType.DIRECTIVE, "#", 0, 1)

    assert_token_equals(actual, EXPECTED)
    assert cursor.position == 1


def test_tokenize_directive_error():
    cursor = StringCursor("this input throws an error")
    with pytest.raises(UnknownTokenError):
        _tokenize_directive(cursor, 0)


test_data = [
    ("Null directive", "#\n", 0, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 0,
            "col": 1,
            "match": "#"
        },
    ))),
    ("No parameter directive", "#pragma\n", 0, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 0,
            "col": 1,
            "match": "#pragma"
        },
    ))),
    ("Integer constant", "#define TEST_INT 1234\n", 4, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 4,
            "col": 1,
            "match": "#define"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 4,
            "col": 8,
            "match": "TEST_INT"
        },
        {
            "token_type": TokenType.INTEGER_CONST,
            "line": 4,
            "col": 17,
            "match": "1234"
        }
    ))),
    ("Character constant", "#define TEST_CHAR 's'\n", 5, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 5,
            "col": 1,
            "match": "#define"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 5,
            "col": 8,
            "match": "TEST_CHAR"
        },
        {
            "token_type": TokenType.CHAR_CONST,
            "line": 5,
            "col": 18,
            "match": "'s'"
        }
    ))),
    ("Function macro", "#define FMACRO(name) typedef struct name##_s name##_t\n", 6, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 6,
            "col": 1,
            "match": "#define"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 8,
            "match": "FMACRO"
        },
        {
            "token_type": TokenType.LPARAN,
            "line": 6,
            "col": 14,
            "match": "("
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 15,
            "match": "name"
        },
        {
            "token_type": TokenType.RPARAN,
            "line": 6,
            "col": 19,
            "match": ")"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 21,
            "match": "typedef"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 29,
            "match": "struct"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 36,
            "match": "name"
        },
        {
            "token_type": TokenType.TOKEN_CONCATINATION, 
            "line": 6, 
            "col": 40,
            "match": "##"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 42,
            "match": "_s"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 45,
            "match": "name"
        },
        {
            "token_type": TokenType.TOKEN_CONCATINATION,
            "line": 6,
            "col": 49,
            "match": "##"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 51,
            "match": "_t"
        }
    ))),
    ("Conditional statement", "#if X <= 5\n", 7, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 7,
            "col": 1,
            "match": "#if"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 7,
            "col": 4,
            "match": "X"
        },
        {
            "token_type": TokenType.LESS_THAN_OR_EQUAL,
            "line": 7,
            "col": 6,
            "match": "<="
        },
        {
            "token_type": TokenType.INTEGER_CONST,
            "line": 7,
            "col": 9,
            "match": "5"
        }
    ))),
    ("Include statement", "#include <stdio.h>\n", 8, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 8,
            "col": 1,
            "match": "#include"
        },
        {
            "token_type": TokenType.FILENAME,
            "line": 8,
            "col": 9,
            "match": "<stdio.h>"
        }
    ))),
    ("Conditionals aren't files", "#pragma 34 <= TEST_1 || TEST_2 > 55\n", 9, tuple(MockToken(**x) for x in (
        {
            "token_type": TokenType.DIRECTIVE,
            "line": 9,
            "col": 1,
            "match": "#pragma"
        },
        {
            "token_type": TokenType.INTEGER_CONST,
            "line": 9,
            "col": 8,
            "match": "34"
        },
        {
            "token_type": TokenType.LESS_THAN_OR_EQUAL,
            "line": 9,
            "col": 11,
            "match": "<="
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 9,
            "col": 14,
            "match": "TEST_1"
        },
        {
            "token_type": TokenType.OR,
            "line": 9,
            "col": 21,
            "match": "||"
        },
        {
            "token_type": TokenType.IDENTIFIER,
            "line": 9,
            "col": 24,
            "match": "TEST_2"
        },
        {
            "token_type": TokenType.GREATER_THAN,
            "line": 9,
            "col": 31,
            "match": ">"
        },
        {
            "token_type": TokenType.INTEGER_CONST,
            "line": 9,
            "col": 33,
            "match": "55"
        }
    )))
]


@pytest.mark.parametrize(
    "line_str,line_number,expected",
    argvalues=[x[1:4] for x in test_data],
    ids=[x[0] for x in test_data])
def test_tokenize_line(line_str, line_number, expected):
    cursor = StringCursor(line_str)

    actual_list, line_offset = tokenize_line(cursor, line_number)
    assert_token_lists_equal(actual_list, expected)


LINE_ENDINGS_TEST_DATA = tuple(MockToken(**x) for x in (
    {
        "token_type": TokenType.DIRECTIVE,
        "line": 0,
        "col": 1,
        "match": "#define"
    },
    {
        "token_type": TokenType.IDENTIFIER,
        "line": 0,
        "col": 8,
        "match": "TEST_LIST"
    },
    {
        "token_type": TokenType.IDENTIFIER,
        "line": 0,
        "col": 18,
        "match": "a"
    },
    {
        "token_type": TokenType.COMMA,
        "line": 0,
        "col": 19,
        "match": ","
    },
    {
        "token_type": TokenType.IDENTIFIER,
        "line": 1,
        "col": 24,
        "match": "b"
    },
    {
        "token_type": TokenType.COMMA,
        "line": 1,
        "col": 25,
        "match": ","
    },
    {
        "token_type": TokenType.IDENTIFIER,
        "line": 2,
        "col": 30,
        "match": "c"
    }
))


def test_tokenize_line_escaped_line_endings():
    cursor = StringCursor("#define TEST_LIST a, \\\n\tb, \\\n\tc\n")
    actual_list, line_offset = tokenize_line(cursor, 0)

    assert_token_lists_equal(actual_list, LINE_ENDINGS_TEST_DATA)
    assert line_offset == 3


FILE_TEST_DATA = {
    "path": Path("./test/data/tokenizer/main.h"),
    "expected_lines": 7
}


def test_tokenize_file():
    tokens = tokenize_file(FILE_TEST_DATA["path"])
    assert len(tokens) == FILE_TEST_DATA["expected_lines"]
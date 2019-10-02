import pytest # NOQA
from src.preprocessor.tokenizer import tokenize_line, TokenType, _tokenize_directive, UnknownTokenError
from src.useful import StringCursor
from .util_tokens import assert_token_equals, assert_token_lists_equal


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
    ("Null directive", "#\n", 0, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 0,
            "col": 1,
            "matched": "#"
        }
    ]),
    ("No parameter directive", "#pragma\n", 0, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 0,
            "col": 1,
            "matched": "#pragma"
        }
    ]),
    ("Integer constant", "#define TEST_INT 1234\n", 4, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 4,
            "col": 1,
            "matched": "#define"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 4,
            "col": 8,
            "matched": "TEST_INT"
        },
        {
            "type": TokenType.INTEGER_CONST,
            "line": 4,
            "col": 17,
            "matched": "1234"
        }
    ]),
    ("Character constant", "#define TEST_CHAR 's'\n", 5, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 5,
            "col": 1,
            "matched": "#define"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 5,
            "col": 8,
            "matched": "TEST_CHAR"
        },
        {
            "type": TokenType.CHAR_CONST,
            "line": 5,
            "col": 18,
            "matched": "'s'"
        }
    ]),
    ("Function macro", "#define FMACRO(name) typedef struct name##_s name##_t\n", 6, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 6,
            "col": 1,
            "matched": "#define"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 8,
            "matched": "FMACRO"
        },
        {
            "type": TokenType.LPARAN,
            "line": 6,
            "col": 14,
            "matched": "("
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 15,
            "matched": "name"
        },
        {
            "type": TokenType.RPARAN,
            "line": 6,
            "col": 19,
            "matched": ")"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 21,
            "matched": "typedef"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 29,
            "matched": "struct"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 36,
            "matched": "name"
        },
        {
            "type": TokenType.TOKEN_CONCATINATION, 
            "line": 6, 
            "col": 40,
            "matched": "##"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 42,
            "matched": "_s"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 45,
            "matched": "name"
        },
        {
            "type": TokenType.TOKEN_CONCATINATION,
            "line": 6,
            "col": 49,
            "matched": "##"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 6,
            "col": 51,
            "matched": "_t"
        }
    ]),
    ("Conditional statement", "#if X <= 5\n", 7, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 7,
            "col": 1,
            "matched": "#if"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 7,
            "col": 4,
            "matched": "X"
        },
        {
            "type": TokenType.LESS_THAN_OR_EQUAL,
            "line": 7,
            "col": 6,
            "matched": "<="
        },
        {
            "type": TokenType.INTEGER_CONST,
            "line": 7,
            "col": 9,
            "matched": "5"
        }
    ]),
    ("Include statement", "#include <stdio.h>\n", 8, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 8,
            "col": 1,
            "matched": "#include"
        },
        {
            "type": TokenType.FILENAME,
            "line": 8,
            "col": 9,
            "matched": "<stdio.h>"
        }
    ]),
    ("Conditionals aren't files", "#pragma 34 <= TEST_1 || TEST_2 > 55\n", 9, [
        {
            "type": TokenType.DIRECTIVE,
            "line": 9,
            "col": 1,
            "matched": "#pragma"
        },
        {
            "type": TokenType.INTEGER_CONST,
            "line": 9,
            "col": 8,
            "matched": "34"
        },
        {
            "type": TokenType.LESS_THAN_OR_EQUAL,
            "line": 9,
            "col": 11,
            "matched": "<="
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 9,
            "col": 14,
            "matched": "TEST_1"
        },
        {
            "type": TokenType.OR,
            "line": 9,
            "col": 21,
            "matched": "||"
        },
        {
            "type": TokenType.IDENTIFIER,
            "line": 9,
            "col": 24,
            "matched": "TEST_2"
        },
        {
            "type": TokenType.GREATER_THAN,
            "line": 9,
            "col": 31,
            "matched": ">"
        },
        {
            "type": TokenType.INTEGER_CONST,
            "line": 9,
            "col": 33,
            "matched": "55"
        }
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


LINE_ENDINGS_TEST_DATA = [
    {
        "type": TokenType.DIRECTIVE,
        "line": 0,
        "col": 1,
        "matched": "#define"
    },
    {
        "type": TokenType.IDENTIFIER,
        "line": 0,
        "col": 8,
        "matched": "TEST_LIST"
    },
    {
        "type": TokenType.IDENTIFIER,
        "line": 0,
        "col": 18,
        "matched": "a"
    },
    {
        "type": TokenType.COMMA,
        "line": 0,
        "col": 19,
        "matched": ","
    },
    {
        "type": TokenType.IDENTIFIER,
        "line": 1,
        "col": 24,
        "matched": "b"
    },
    {
        "type": TokenType.COMMA,
        "line": 1,
        "col": 25,
        "matched": ","
    },
    {
        "type": TokenType.IDENTIFIER,
        "line": 2,
        "col": 30,
        "matched": "c"
    }
]


def test_tokenize_line_escaped_line_endings():
    cursor = StringCursor("#define TEST_LIST a, \\\n\tb, \\\n\tc\n")
    actual_list, line_offset = tokenize_line(cursor, 0)

    assert_token_lists_equal(actual_list, LINE_ENDINGS_TEST_DATA)
    assert line_offset == 3
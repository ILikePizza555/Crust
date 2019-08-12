import pytest # NOQA
from src.preprocessor import Token, TokenType, _parse_include

PARSE_INCLUDE_TEST_DATA = [
    ("system import", [Token(TokenType.FILENAME, 0, 0, "<stdio.h>")], (None, "stdio.h"))
    ("local import", [Token(TokenType.STRING, 0, 0, "\"local_file.h\"")], ("local_file.h", None))]


@pytest.mark.parametrize(
    "tokens,expected",
    [x[1:3] for x in PARSE_INCLUDE_TEST_DATA],
    [x[0] for x in PARSE_INCLUDE_TEST_DATA]
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
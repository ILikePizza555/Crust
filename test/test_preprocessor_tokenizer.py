import pytest # NOQA
from .utilities import NamedTestMatrix
from src.preprocessor.tokenizer import Token, TokenType, tokenize_line

SINGLE_TOKEN_TESTS = NamedTestMatrix(
    ("input_str", "expected_type"),
    (
        ("whitespace",  "\t",       TokenType.WHITESPACE),
        ("directive",   "#define",  TokenType.DIRECTIVE),
        ("string",      "\"uwu\"",  TokenType.STRING_LITERAL),
        ("int",         "42069",    TokenType.NUM_LITERAL),
        ("dec",         "3.141",    TokenType.NUM_LITERAL),
        ("defined",     "defined",  TokenType.OP_DEFINED),
        ("equality",    "==",       TokenType.OP_EQ),
        ("not equal",   "!=",       TokenType.OP_NEQ),
        ("less than",   "<",        TokenType.OP_LT),
        ("grea than",   ">",        TokenType.OP_GT),
        ("not",         "!",        TokenType.OP_NOT),
        ("identifier",  "UWU2",     TokenType.IDENTIFIER),
        ("generic",     "~",        TokenType.GENERIC)
    )
)
@pytest.mark.parametrize(SINGLE_TOKEN_TESTS.arg_names, SINGLE_TOKEN_TESTS.arg_values, ids=SINGLE_TOKEN_TESTS.test_names)
def test_single_tokens(input_str, expected_type):
    actual = tokenize_line(input_str)
    assert len(actual) == 1
    assert actual[0].type == expected_type


def test_tokenize_line():
    actual = tokenize_line("#define uwu 420")
    expected = [
        (TokenType.DIRECTIVE, "#define"), (TokenType.WHITESPACE, " "),
        (TokenType.IDENTIFIER, "uwu"), (TokenType.WHITESPACE, " "), (TokenType.NUM_LITERAL, "420")]

    for a, e in zip(actual, expected):
        assert a.type == e[0]
        assert a.value.group(0) == e[1]

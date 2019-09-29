import pytest # NOQA
from .test_preprocessor_tokenizer import assert_token_equals
from src.useful import StringCursor
from src.preprocessor.tokenizer import tokenize_line, TokenType
from src.preprocessor.parser import _expect_directive, _expect_token, UnexpectedTokenError, UnknownPreprocessorDirectiveError


TEST_TOKENS = tuple(tokenize_line(StringCursor('#define MAC(FOO, BAR) "dir/"##FOO#BAR'), 0)[0])


def test_simple_expect_token():
    actual = _expect_token(list(TEST_TOKENS[1:]), {TokenType.IDENTIFIER, })

    assert_token_equals(actual, TokenType.IDENTIFIER, matched="MAC")


def test_expect_token_failure():
    with pytest.raises(UnexpectedTokenError):
        _expect_token(list(TEST_TOKENS), {TokenType.INTEGER_CONST})


def test_simple_expect_directive():
    actual = _expect_directive(list(TEST_TOKENS), "define")

    assert_token_equals(actual, TokenType.DIRECTIVE, matched="#define")


def test_expect_directive_failure_on_unexpected_directive():
    with pytest.raises(UnknownPreprocessorDirectiveError):
        _expect_directive(list(TEST_TOKENS), "pragma")
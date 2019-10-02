import re
from src.preprocessor.tokenizer import Token, TokenType
from .util_tokens import MockToken


def test_token_equality():
    """This test asserts that MockToken's equality operator works correctly."""
    tok = Token(TokenType.DIRECTIVE, 3, 4, re.match(r"#(\S*)", "#test"))
    m_tok = MockToken(TokenType.DIRECTIVE, "#test", 3, 4)
    om_tok = MockToken(TokenType.IDENTIFIER, "NOTEQUAL", 6, 9)

    assert m_tok == tok
    assert om_tok != tok

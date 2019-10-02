from typing import List, Optional
from src.preprocessor.tokenizer import Token, TokenType, tokenize_line
from src.useful import StringCursor


class MockToken():
    def __init__(self, token_type: TokenType, match: Optional[str] = None, line: Optional[int] = None, col: Optional[int] = None):
        self.token_type = token_type
        self.match = match
        self.line = line
        self.col = col

    def __repr__(self):
        return f"MockToken(token_type={self.token_type}, matched={self.match}, line={self.line}, col={self.col})"

    def __eq__(self, other):
        if type(other) is MockToken:
            return (self.token_type == other.token_type and
                    self.match == other.match and
                    self.line == other.line and
                    self.col == other.col)
        elif type(other) is Token:
            return (self.token_type == other.token_type and
                    (self.match is None or self.match == other.match.group()) and
                    (self.line is None or self.line == other.line) and
                    (self.col is None or self.col == other.col))


def assert_token_equals(actual: Token, expected: MockToken):
    """Helper function to test token equality"""
    assert actual.token_type is expected.token_type

    if expected.line is not None:
        assert actual.line == expected.line

    if expected.col is not None:
        assert actual.col == expected.col

    if expected.match is not None:
        assert actual.match.group() == expected.match


def assert_token_lists_equal(actual: List[Token], expected: List[MockToken]):
    assert len(actual) == len(expected)

    for a, e in zip(actual, expected):
        assert_token_equals(a, e)


def tokenize_string(s: str, line_number: int = 0, cut_directive: bool = True) -> List[Token]:
    tokens, _ = tokenize_line(StringCursor(s), line_number)

    if cut_directive and tokens[0].token_type is TokenType.DIRECTIVE:
        tokens.pop(0)
    
    return tokens

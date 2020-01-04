import pytest
from src.preprocessor.parser import IncludeDirective, parse_line
from src.preprocessor.tokenizer import tokenize_line, TokenType
from .utilities import NamedTestMatrix


PARSE_LINE_TEST_MATRIX = NamedTestMatrix(
    ("line,expected"),
    (
        ("normal include",              "#include <stdio.h>",        IncludeDirective("stdio.h", False))
        ("normal include with path",    "#include <linux/x.h>",      IncludeDirective("linux/x.h", False))
        ("expanded include",            "#include \"waluigi.h\"",    IncludeDirective("waluigi.h", True))
    )
)
@pytest.mark.parameterize(PARSE_LINE_TEST_MATRIX.arg_names, PARSE_LINE_TEST_MATRIX.arg_values, ids=PARSE_LINE_TEST_MATRIX.test_names)
def test_parse_line(line, expected):
    tokens = list(filter(lambda t: t.type is not TokenType.WHITESPACE, tokenize_line(line)))
    actual = parse_line(tokens)
    assert actual == expected

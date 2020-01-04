from src.preprocessor.parser import IncludeDirective, parse_line
from src.preprocessor.tokenizer import tokenize_line
from .utilities import NamedTestMatrix


PARSE_LINE_TEST_MATRIX = NamedTestMatrix(
    ("line,expected"),
    (
        ("normal include",              tokenize_line("#include <stdio.h>"),        IncludeDirective("stdio.h", False))
        ("normal include with path",    tokenize_line("#include <linux/x.h>"),      IncludeDirective("linux/x.h", False))
        ("expanded include",            tokenize_line("#include \"waluigi.h\""),    IncludeDirective("waluigi.h", True))
    )
)
def test_parse_line(line, expected):
    actual = parse_line(line)
    assert actual == expected

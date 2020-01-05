import pytest
from src.preprocessor.parser import IncludeDirective, parse_line, ObjectMacro, FunctionMacro
from src.preprocessor.tokenizer import tokenize_line, TokenType
from .utilities import NamedTestMatrix


PARSE_INCLUDE_MATRIX = NamedTestMatrix(
    ("line", "expected"),
    (
        ("normal include",              "#include <stdio.h>",        IncludeDirective("stdio.h", False)),
        ("normal include with path",    "#include <linux/x.h>",      IncludeDirective("linux/x.h", False)),
        ("expanded include",            "#include \"waluigi.h\"",    IncludeDirective("waluigi.h", True)),
    )
)
@pytest.mark.parametrize(PARSE_INCLUDE_MATRIX.arg_names, PARSE_INCLUDE_MATRIX.arg_values, ids=PARSE_INCLUDE_MATRIX.test_names)
def test_parse_include(line, expected):
    tokens = list(filter(lambda t: t.type is not TokenType.WHITESPACE, tokenize_line(line)))
    actual = parse_line(tokens)
    assert actual == expected


def test_parse_object_macro():
    tokens = list(filter(lambda t: t.type is not TokenType.WHITESPACE, tokenize_line("#define DRUG_NUMBER 420")))
    actual = parse_line(tokens)

    assert isinstance(actual, ObjectMacro)
    assert actual.identifier == "DRUG_NUMBER"
    assert [t.value.group() for t in actual.tokens] == ["420"]


def test_parse_function_macro():
    tokens = list(filter(lambda t: t.type is not TokenType.WHITESPACE, tokenize_line("#define A(B, C, D, E, F, G) B + C")))
    actual = parse_line(tokens)

    assert isinstance(actual, FunctionMacro)
    assert actual.identifier == "A"
    assert actual.params == ("B", "C", "D", "E", "F", "G")
    assert [t.value.group() for t in actual.expression] == ["B", "+", "C"]

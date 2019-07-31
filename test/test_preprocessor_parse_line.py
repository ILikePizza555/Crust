import pytest # NOQA
from src.preprocessor import parse_line, Directives, PreProcessorParseError


def test_simple_import():
    result = parse_line("#include <stdio.h>")
    assert result == (Directives.INCLUDE, "<stdio.h>")


def test_invalid_directive():
    input_line = "#invalid_directive_please_error"

    with pytest.raises(PreProcessorParseError):
        parse_line(input_line)


def test_object_macro():
    result = parse_line("#define PI 3.1415")

    assert result == (Directives.DEFINE, "PI", "3.1415")


def test_function_macro():
    result = parse_line("#define str(s) #s")

    assert result == (Directives.DEFINE, "str", ["s"], "#s")

"""
An implementation of the C preprocessor. However, rather than generating code,
the purpose of this preprocessor is to determine the relationship between compilation units.
"""

import re
import string
from enum import Enum, auto
from typing import Optional

LINE_RE = re.compile(r"#(?P<directive>\S*)(?: (?P<expression>.*))?")
OBJECT_MACRO_RE = re.compile(r"^(?:#define )?(?P<identifier>[^\s\(\)\#]*) (?P<tokens>.*)")
FUNCTION_MACRO_RE = re.compile(r"^(?:#define )?(?P<identifier>\S*)(?P<args>\(.*\)) (?P<tokens>.*)")
CONSTANT_COMPARISON_EXPR_RE = re.compile(r"^(?P<p_1>\w+) ?(?P<operator>[=<>!]+) ?(?P<p_2>.*)")


class PreProcessorParseError(Exception):
    """Thrown when the preprocessor parser encounters an error"""

    def __init__(self, line, reason):
        self.line = line
        self.reason = reason


class MatchError(Exception):
    """Thrown when a regex match fails (say for an expression). This is intended to be caught."""
    pass


class UnknownTokenError(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "Unknown token: " + self.token


class Directives(Enum):
    INCLUDE = auto()
    DEFINE = auto()
    IF = auto()
    IFDEF = auto()
    IFNDEF = auto()
    ELIF = auto()
    ELSE = auto()
    ENDIF = auto()
    PRAGMA = auto()


class ComparisonOperators(Enum):
    EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()

    @staticmethod
    def from_string(cls, operator_string: str) -> "ComparisonOperators":
        return {
            "==": cls.EQUAL,
            "<": cls.LESS_THAN,
            ">": cls.GREATER_THAN,
            "<=": cls.LESS_THAN_OR_EQUAL,
            ">=": cls.GREATER_THAN_OR_EQUAL
        }[operator_string]


class ComparisonExpression():
    @staticmethod
    def from_expr(cls, expr: str) -> "ComparisonExpression":
        expr_match = CONSTANT_COMPARISON_EXPR_RE.match(expr)
        if not expr_match:
            raise MatchError()

        try:
            operator_string = expr_match.group("operator")
            operator_value = ComparisonOperators.from_string(operator_string)
        except KeyError:
            raise UnknownTokenError(operator_string)

        left_parameter = expr_match("p_1")
        right_parameter = expr_match("p_2")

        return cls(operator_value, left_parameter, right_parameter)

    def __init__(self, op: ComparisonOperators, left_parameter: str, right_parameter: str):
        self.op = op
        self.left_parameter = left_parameter
        self.right_parameter = right_parameter


def parse_line(line: str) -> Optional[tuple]:
    line_match = LINE_RE.match(line)

    if not line_match:
        return None

    try:
        # Enum determines valid directives
        directive = Directives[line_match.group("directive").upper()]
        expr = line_match.group("expression")
    except KeyError:
        raise PreProcessorParseError(line, "Invalid preprocessor directive: " + line_match.group("directive"))

    if directive is Directives.DEFINE:
        # Need to figure out if this is an object macro or a function macro
        expr_match = OBJECT_MACRO_RE.match(expr)
        if expr_match is not None:
            return (directive, expr_match.group("identifier"), expr_match.group("tokens"))

        expr_match = FUNCTION_MACRO_RE.match(expr)
        if expr_match is not None:
            args_list = [x.strip() for x in expr_match.group("args").strip(string.whitespace + "()").split(",")]
            return (directive, expr_match.group("identifier"), args_list, expr_match.group("tokens"))

        raise PreProcessorParseError(line, "Invalid Macro Definition")
    elif directive is Directives.IF or directive is Directives.ELIF:
        # TODO: Need to implement full expression parsing, allowing for logical and arithmetic operators
        try:
            comp_expr = ComparisonExpression.from_expr(expr)
            return (directive, comp_expr)
        except MatchError:
            raise PreProcessorParseError(line, "Invalid expression")
        except UnknownTokenError as e:
            raise PreProcessorParseError(line, str(e))
    else:
        return (directive, expr)



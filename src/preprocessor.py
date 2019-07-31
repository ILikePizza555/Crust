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


class PreProcessorParseError(Exception):
    """Thrown when the preprocessor parser encounters an error"""

    def __init__(self, line, reason):
        self.line = line
        self.reason = reason


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
    else:
        return (directive, expr)

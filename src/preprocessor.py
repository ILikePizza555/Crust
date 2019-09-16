"""
An implementation of the C preprocessor. However, rather than generating code,
the purpose of this preprocessor is to determine the relationship between compilation units.
"""

from typing import Optional, List, NamedTuple, Iterable, Tuple, Union

class PreprocessorSyntaxError(Exception):
    def __init__(self, line_number, column_number, message):
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        return f"Syntax error on line {self.line_number}, {self.column_number}: {self.message}"


def tokenize_lines(source_lines: Iterable[str], skip_c=True) -> Iterable[List[Token]]:
    """
    Takes a source file split into lines and returns a generator that tokeninzes it.
    If `skip_c` is true, C code (lines which do not start with "#") are ignored.
    """
    for i, line in enumerate(source_lines):
        line_tokens = _tokenize_line(line, i)
        if line_tokens or (not line_tokens and not skip_c):
            yield line_tokens


class ImportTable(NamedTuple):
    """
    A pair of lists containing the names of files the file imports.
    The list in which the filename is contained defines the context.
    """
    local: List[str] = []
    system: List[str] = []

    def append_entry(self, entry: Tuple[Optional[str], Optional[str]]):
        if entry[0]:
            self.local.append(entry[0])

        if entry[1]:
            self.system.append(entry[1])


def _assert_token_type(token: Token, token_type: TokenType):
    """Helper function that asserts the first token in the list is of the given type without removing it"""
    if token.token_type is not token_type:
        raise PreprocessorSyntaxError(token.line, token.col, f"Expected {token_type}")


def _expect_token(tokens: List[Token], token_type: TokenType, pos: int = 0) -> Token:
    """
    Asserts that the `pos` token in the list is of `token_type`.
    If it is, it is removed from the list and returned
    """
    peek = tokens[pos]
    _assert_token_type(peek, token_type)
    return tokens.pop(0)


def _parse_include(tokens: List[Token], macro_table={}):
    peek = tokens[0]

    if peek.token_type is TokenType.FILENAME:
        tok = tokens.pop(0)
        return (None, tok.text.strip("<> "))
    elif peek.token_type is TokenType.STRING:
        tok = tokens.pop(0)
        return (tok.text.strip("\" "), None)
    elif peek.token_type is TokenType.IDENTIFIER:
        raise NotImplementedError("Macro resolution is not supported yet.")
    else:
        raise PreprocessorSyntaxError(peek.line, peek.col, "Expected a filename, string, or identifier.")


def _parse_identifier_list(tokens: List[Token]) -> List[str]:
    _expect_token(tokens, TokenType.LPARAN)

    identifier_list = []

    while tokens[0].token_type is not TokenType.RPARAN:
        identifier_list.append(_expect_token(tokens, TokenType.IDENTIFIER).text)

        if tokens[0].token_type is TokenType.COMMA:
            tokens.pop(0)

    # Consume the RPARAN
    tokens.pop(0)

    return identifier_list


class CallExpression:
    @classmethod
    def from_tokens(cls, tokens):
        calling_name = _expect_token(tokens, TokenType.IDENTIFIER).text
        _expect_token(tokens, TokenType.LPARAN)

        calling_arguments = []

        while tokens[0].token_type is not TokenType.RPARAN:
            peek: Token = tokens[0]

            if peek.token_type is TokenType.INTEGER_CONST or peek.token_type is TokenType.CHAR_CONST:
                calling_arguments.append(tokens.pop(0))
                peek = None
            elif peek.token_type is TokenType.IDENTIFIER and tokens[1].token_type is not TokenType.LPARAN:
                calling_arguments.append(tokens.pop(0))
                peek = None
            elif peek.token_type is TokenType.IDENTIFIER and tokens[1].token_type is TokenType.LPARAN:
                calling_arguments.append(CallExpression.from_tokens(tokens))
            else:
                raise PreprocessorSyntaxError(peek.line, peek.col, "Expected an expression")

            if tokens[0].token_type is TokenType.COMMA:
                tokens.pop(0)
            elif tokens[0].token_type is not TokenType.RPARAN:
                raise PreprocessorSyntaxError(tokens[0].line, tokens[0].col, "Expected ',' or ')'")

        tokens.pop(0)
        return cls(calling_name, calling_arguments)

    def __init__(self, name: str, arguments: list):
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"CallExpression(name={self.name}, arguments={self.arguments})"

    def __eq__(self, other):
        return self.name == other.name and self.arguments == other.arguments


class Macro:
    """Class representation of a Macro"""
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        macro_name = _expect_token(tokens, TokenType.IDENTIFIER).text
        macro_params = None
        macro_value = []

        if tokens[0].token_type is TokenType.LPARAN:
            macro_params = _parse_identifier_list(tokens)

        while tokens:
            if len(tokens) >= 2 and tokens[0].token_type is TokenType.IDENTIFIER and tokens[1].token_type is TokenType.LPARAN:
                macro_value.append(CallExpression.from_tokens(tokens))

            macro_value.append(tokens.pop(0))

        return cls(macro_name, macro_value, macro_params)

    def __init__(self, name: str, value: Union[list, Token], parameters: Optional[list] = None):
        self.name = name
        self.parameters = parameters

        if type(value) is not list:
            self.value: list = [value]
        else:
            self.value: list = value

    def __repr__(self):
        return f"Macro(name={self.name}, parameters={self.parameters}, value={self.value}"

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value and self.parameters == other.parameters


def execute_tokens(tokens: Iterable[List[Token]], macro_table=None):
    if not macro_table:
        macro_table = {}

    imports = ImportTable()

    for token_line in tokens:
        directive = _expect_token(token_line, TokenType.DIRECTIVE)

        if directive.text.upper() == "INCLUDE":
            imports.append_entry(_parse_include(token_line, macro_table))
        elif directive.text.upper() == "DEFINE":
            new_macro = Macro.from_tokens(token_line)
            macro_table[new_macro.name] = new_macro

    return (macro_table, imports)


def run_file(file_string: str, macro_table=None):
    if macro_table is None:
        macro_table = {}

    lines = file_string.replace("\\\n", " ").splitlines()
    tokens = tokenize_lines(lines)

    return execute_tokens(tokens, macro_table)

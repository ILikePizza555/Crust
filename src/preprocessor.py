"""
An implementation of the C preprocessor. However, rather than generating code,
the purpose of this preprocessor is to determine the relationship between compilation units.
"""

from typing import Optional, List, NamedTuple, Iterable, Tuple, Union


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

from typing import List, Set, Optional, Union, Callable, Tuple
from .tokenizer import Token, TokenType, VALUE_TOKENS, RTL_OPS, OPERATOR_TOKENS
from .shunting_yard import shunting_yard_algorithmn

class PreprocessorSyntaxError(Exception):
    def __init__(self, line_number, column_number, message):
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        return f"Syntax error on line {self.line_number}, {self.column_number}: {self.message}"


class UnexpectedTokenError(Exception):
    """Thrown when the preprocessor encounters an unexpected token"""
    def __init__(self, unexpected_token: Token, expected_set: Set[Token]):
        self.unexpected_token = unexpected_token
        self.expected_set = expected_set

    def __str__(self):
        return f"Unexpected token {self.unexpected_token.error_str}. Expected one of {self.expected_set}"


class UnknownPreprocessorDirectiveError(Exception):
    def __init__(self, line_number: int, directive: str):
        self.line_number = line_number
        self.directive = directive

    def __str__(self):
        return f"Unknown directive on line {self.line_number}, '{self.directive}'."


def _expect_token(tokens: List[Token], expected_types: Set[TokenType], pos: int = 0) -> Token:
    """
    Asserts that the `pos` token in the list is one of `expected_types`.
    If it is, it is removed from the list and returned
    """
    peek = tokens[pos]

    if peek.token_type not in expected_types:
        raise UnexpectedTokenError(peek, expected_types)

    return tokens.pop(pos)


def _expect_directive(tokens: List[Token], name: str, pos: int = 0) -> Token:
    peek = tokens[pos]

    if peek.token_type is not TokenType.DIRECTIVE:
        raise UnexpectedTokenError(peek, {TokenType.DIRECTIVE})

    if peek.match.group(1) != name:
        raise UnknownPreprocessorDirectiveError(peek.line, peek.match.group(1))

    return tokens.pop(pos)


class Expression:
    """
    Class representation of an expression
    """

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        output_stack = shunting_yard_algorithmn(tokens)
        return cls(output_stack)

    def __init__(self, expression_stack: List[Token]):
        self.expression_stack = expression_stack


class ObjectMacro:
    """
    Class representation of an object macro
    """

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """
        Parses the following syntax:
        IDENTIFIER TOKENS*
        """
        name_token = _expect_token(tokens, {TokenType.IDENTIFIER, })
        remainder = tokens

        return cls(name_token.match.group(), remainder)

    def __init__(self, identifier: str, value: List[Token]):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return f"ObjectMacro(identifier={self.identifier}, value={self.value})"

    def __eq__(self, o):
        return self.identifier == o.identifier and self.value == o.value


class FunctionMacro:
    """
    Class representation of a function macro
    """
    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """
        Parses the following syntax:
        IDENTIFIER (IDENTIFIER [, IDENTIFIER]*) TOKENS*
        """
        identifier = _expect_token(tokens, {TokenType.IDENTIFIER, })
        _expect_token(tokens, {TokenType.LPARAN, })
        parameters = []

        while tokens:
            parameters.append(_expect_token(tokens, {TokenType.IDENTIFIER, }))

            try:
                e = _expect_token(tokens, {TokenType.COMMA, TokenType.RPARAN})
            except IndexError:
                raise PreprocessorSyntaxError(identifier.line, 0, "Expected comma or closing parenthesis.")

            if e.token_type == TokenType.RPARAN:
                break

        return cls(
            identifier.match.group(),
            [x.match.group() for x in parameters],
            tokens
        )

    def __init__(self, identifier: str, parameters: List[str], value: List[Token]):
        self.identifier = identifier
        self.parameters = parameters
        self.value = value

    def __repr__(self):
        return f"FunctionMacro(identifier={self.identifier}, parameters={self.parameters}, value={self.value})"

    def __eq__(self, other):
        return (
            self.identifier == other.identifier and
            self.parameters == other.parameters and
            self.value == other.value
        )


class EvaluatedInclude:
    """
    Class representation of a normal include directive.
    """

    @classmethod
    def from_tokens(cls, token_list: List[Token]) -> "EvaluatedInclude":
        parameter_tok = _expect_token(token_list, {TokenType.FILENAME, TokenType.STRING})

        return cls(parameter_tok.match.group(1), parameter_tok.token_type is TokenType.STRING)

    def __init__(self, include_path: str, expanded_include: bool):
        self.include_path = include_path
        self.expanded_include = expanded_include

    def __eq__(self, other):
        return (
            self.include_path == other.include_path and
            self.expanded_include == other.expanded_include
        )

    def __repr__(self):
        return f"EvaluatedInclude(include_path={self.include_path}, expanded_include={self.expanded_include})"


class DeferedInclude:
    """
    Include directive that uses an indentifier as it's parameter. We don't know what it includes
    until we can evaluate the identifier.
    """
    def __init__(self, identifier: Token):
        self.identifier = identifier


class ConditionalBranch:
    """
    Pairs an optional expression with children nodes
    """
    def __init__(self, children: List[any], condition: Optional[Expression]):
        self.children = children
        self.condition = condition


ASTObject = Union[Expression, ObjectMacro, FunctionMacro, EvaluatedInclude, DeferedInclude, ConditionalBranch]


class ParserBase():
    def __init__(self, token_lines: List[List[Token]]):
        self._lines = token_lines
        self._current_line = 0
        self.parse_methods: dict[str, Callable[None, ASTObject]] = dict()

    def peak_current_line(self) -> List[Token]:
        """Returns the current line without incrementing the line counter"""
        return self._lines[self._current_line]

    def get_current_line_number(self) -> int:
        """Returns the line number of the the current token."""
        return self.peak_current_line()[0].line

    def read_next_lines(self, n: int):
        """Returns the next n lines and increments the line counter."""
        self._current_line = min(self._current_line + n, len(self._lines))
        return self._lines[self._current_line - n:self._current_line]

    def read_current_line(self):
        """Returns the next line and increments the line counter."""
        ret = self.read_next_lines(1)
        return ret[0] if ret else []

    def peek_directive(self) -> str:
        """Looks at the current line's directive and returns it."""
        peek_directive_tok = self.peak_current_line()[0]
        assert peek_directive_tok.token_type is TokenType.DIRECTIVE
        return peek_directive_tok.match.group(1)

    def _parse_ignore(self):
        self.read_current_line()
        return None

    @property
    def done(self):
        return self._current_line >= len(self._lines)

    def parse_next(self) -> Optional[ASTObject]:
        try:
            if not self.done:
                parse_method = self.parse_methods[self.peek_directive()]
                return parse_method()
        except KeyError:
            raise UnknownPreprocessorDirectiveError(self.get_current_line_number(), self.peek_directive())

    def parse_lines(self) -> List[ASTObject]:
        object_return = []

        while not self.done:
            object_return.append(self.parse_next())

        return object_return


class Parser(ParserBase):
    def __init__(self, token_lines: List[List[Token]]):
        super(Parser, self).__init__(token_lines)

        # TODO: Make this into some sort of decorator functionality
        self.parse_methods.update({
            "include": self.parse_include_line,
            "define": self.parse_define_line,
            "if": self.parse_if_block,
            "ifdef": self.parse_if_block,
            "ifndef": self.parse_if_block,
            "pragma": self._parse_ignore
        })

    def parse_include_line(self) -> Union[EvaluatedInclude, DeferedInclude]:
        current_line = self.read_current_line()
        _expect_directive(current_line, "include")

        param = _expect_token(current_line, {TokenType.IDENTIFIER, TokenType.STRING, TokenType.FILENAME})

        try:
            return EvaluatedInclude.from_tokens([param])
        except PreprocessorSyntaxError:
            return DeferedInclude(param)

    def parse_define_line(self) -> Union[FunctionMacro, ObjectMacro]:
        current_line = self.read_current_line()
        _expect_directive(current_line, "define")

        # TODO: Better syntax error handling
        try:
            return FunctionMacro.from_tokens(current_line[:])
        except UnexpectedTokenError:
            return ObjectMacro.from_tokens(current_line)

    def parse_conditional_line(self) -> Tuple[str, Union[Expression, Token, None]]:
        current_line = self.read_current_line()
        directive = _expect_token(current_line, {TokenType.DIRECTIVE, })
        directive_str = directive.match.group(1).upper()

        if directive_str in {"IF", "ELIF"}:
            return (directive_str, Expression.from_tokens(current_line))
        elif directive_str in {"IFDEF", "IFNDEF"}:
            return (directive_str, current_line.pop(0))
        else:
            return (directive_str, None)

    def parse_if_block(self) -> List[ConditionalBranch]:
        block_markers = [(x[1], x[2]) for x in self._read_conditional_block() if x[0] == 1]
        block_ranges = ((a[1], b[1]) for a, b in zip(block_markers, block_markers[1:]))
        branches: List[ConditionalBranch] = []

        for begin, end in block_ranges:
            line_type, value = self.parse_conditional_line()
            children: List[ASTObject] = []

            while self._current_line < end:
                children.append(self.parse_next())

            if self.peek_directive() == "endif":
                self.read_current_line()

            branches.append(ConditionalBranch(children, value))

        return branches

    def _read_conditional_block(self) -> List[Tuple[int, str, int]]:
        if_stack = 0
        markers: List[Tuple[str, int]] = []

        for line_number, line in enumerate(self._lines[self._current_line:], start=self._current_line):
            beginning = line[0]
            assert beginning.token_type is TokenType.DIRECTIVE
            directive = beginning.match.group(1).upper()

            if directive in {"IF", "IFDEF", "IFNDEF"}:
                if_stack += 1
                markers.append((if_stack, directive, line_number))
            elif directive in {"ELSE", "ELIF"}:
                markers.append((if_stack, directive, line_number))
            elif beginning.match.group(1).upper() == "ENDIF":
                markers.append((if_stack, directive, line_number))
                if_stack -= 1

                if if_stack == 0:
                    return markers

        raise PreprocessorSyntaxError(line_number, 0, "Expected #endif")

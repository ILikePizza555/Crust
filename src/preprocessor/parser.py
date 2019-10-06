from typing import List, Set, Optional, Union, Callable, Tuple
from .tokenizer import Token, TokenType, VALUE_TOKENS, RTL_OPS, OPERATOR_TOKENS


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

    __PRECIDENCE_MAP = (
        ({TokenType.DEFINED, TokenType.NOT}, 100),
        ({TokenType.GREATER_THAN_OR_EQUAL, TokenType.LESS_THAN_OR_EQUAL,
            TokenType.LESS_THAN, TokenType.GREATER_THAN}, 90),
        ({TokenType.EQUAL, TokenType.NOT_EQUAL}, 80),
        ({TokenType.AND, }, 50),
        ({TokenType.OR, }, 40)
    )

    @staticmethod
    def __get_operator_precidence(op: TokenType) -> int:
        for comp_set, value in Expression.__PRECIDENCE_MAP:
            if op in comp_set:
                return value
        return 0

    @staticmethod
    def _compare_operators(op1: TokenType, op2: TokenType):
        """
        Returns 1 if op1 has a higher precidence than op2,
                0 if op1 and op2 have the sace precidence,
                -1 if op1 has a lower precidence than op2
        """
        v = Expression.__get_operator_precidence(op1) - Expression.__get_operator_precidence(op2)

        if v > 0:
            return 1
        elif v < 0:
            return -1
        else:
            return 0

    @staticmethod
    def _push_operator(op_tok: Token, operator_stack: List[Token], output_stack: List[Token]):
        while operator_stack:
            op_peek = operator_stack[-1]
            op_comp = Expression._compare_operators(op_peek.token_type, op_tok.token_type)

            if op_peek.token_type is not TokenType.LPARAN and (
               op_peek.token_type in RTL_OPS or op_comp == 1):
                output_stack.append(operator_stack.pop())
            else:
                break

        operator_stack.append(op_tok)

    @staticmethod
    def _push_parenthesis(paran_tok: Token, operator_stack: List[Token], output_stack: List[Token]):
        if paran_tok.token_type is TokenType.LPARAN:
            operator_stack.append(paran_tok)
        elif paran_tok.token_type is TokenType.RPARAN:
            try:
                while operator_stack[-1].token_type is not TokenType.LPARAN:
                    output_stack.append(operator_stack.pop())

                # Discard the extra LPARAN
                operator_stack.pop()
            except IndexError:
                # Stack ran out without finding an LPARAN, we have mismatched parenthesis
                raise PreprocessorSyntaxError(paran_tok.line, paran_tok.col, "Unexpected ')'.")

    @staticmethod
    def _push_operator_stack(operator_stack: List[Token], output_stack: List[Token]):
        for operator in reversed(operator_stack):
            if operator.token_type in {TokenType.LPARAN, TokenType.RPARAN}:
                raise PreprocessorSyntaxError(operator.line, operator.col, "Unexpected paranthesis")
            output_stack.append(operator)

    @classmethod
    def from_tokens(cls, tokens: List[Token]):
        """
        Reads a conditional expression from tokens into an RPN stack.
        `tokens` should be a be a list of that tokens that only make up the conditional expression
        """
        output_stack: List[Token] = []
        operator_stack: List[Token] = []

        while tokens:
            tok = tokens.pop(0)

            if tok.token_type in VALUE_TOKENS:
                output_stack.append(tok)

            # Push right-to-left associative operators to the operator stack
            # TODO: Add support for function here
            elif tok.token_type in RTL_OPS:
                operator_stack.append(tok)
            elif tok.token_type in (OPERATOR_TOKENS - RTL_OPS):
                cls._push_operator(tok, operator_stack, output_stack)
            elif tok.token_type in {TokenType.LPARAN, TokenType.RPARAN}:
                cls._push_parenthesis(tok, operator_stack, output_stack)

        # Push all remaining operators on output stack. Note that list.extends is not used to check for mismatched parenthesis
        cls._push_operator_stack(operator_stack, output_stack)

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

        return cls(parameter_tok)

    def __init__(self, parameter: Token):
        self.expanded_include = (parameter.token_type is TokenType.STRING)
        self.include_path = parameter.match.group(1)


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

    def _peak_current_line(self) -> List[Token]:
        return self._lines[self._current_line]

    def _get_current_line_number(self) -> int:
        return self._peak_current_line()[0].line

    def _read_current_line(self, n: int = 1):
        self._current_line = min(self._current_line + n, len(self._lines))
        return self._lines[self._current_line - n:self._current_line]

    def _peek_directive(self) -> str:
        peek_directive_tok = self._peak_current_line()[0]
        assert peek_directive_tok.token_type is TokenType.DIRECTIVE
        return peek_directive_tok.match.group(1)

    @property
    def done(self):
        return self._current_line >= len(self._lines)

    def parse_next(self) -> Optional[ASTObject]:
        try:
            if not self.done:
                return self.parse_methods[self._peek_directive()]()
        except KeyError:
            raise UnknownPreprocessorDirectiveError(self._get_current_line_number(), self._peek_directive())

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
            "ifndef": self.parse_if_block
        })

    def parse_include_line(self) -> Union[EvaluatedInclude, DeferedInclude]:
        current_line = self._read_current_line()
        _expect_directive(current_line, "include")

        param = _expect_token(current_line, {TokenType.IDENTIFIER, TokenType.STRING, TokenType.FILENAME})

        try:
            return EvaluatedInclude(param)
        except PreprocessorSyntaxError:
            return DeferedInclude(param)

    def parse_define_line(self) -> Union[FunctionMacro, ObjectMacro]:
        current_line = self._read_current_line()
        _expect_directive(current_line, "define")

        # TODO: Better syntax error handling
        try:
            return FunctionMacro.from_tokens(current_line)
        except UnexpectedTokenError:
            return ObjectMacro.from_tokens(current_line)

    def parse_conditional_line(self) -> Tuple[str, Union[Expression, Token, None]]:
        current_line = self._read_current_line()
        directive = _expect_token(current_line, set(TokenType.DIRECTIVE))
        directive_str = directive.match.group(1).upper()

        if directive_str in {"IF", "ELIF"}:
            return (directive_str, Expression.from_tokens(current_line))
        elif directive_str in {"IFDEF", "IFNDEF"}:
            return (directive_str, current_line.pop(0))
        else:
            return (directive_str, None)

    def parse_if_block(self) -> List[ConditionalBranch]:
        block_markers = ((x[1], x[2]) for x in self._read_conditional_block() if x[0] == 1)
        block_ranges = ((a[1], b[1]) for a, b in zip(block_markers, block_markers[1:]))
        branches: List[ConditionalBranch] = []

        for begin, end in block_ranges:
            line_type, value = self.parse_conditional_line()
            children: List[ASTObject] = []

            while self._current_line < end:
                children.append(self.parse_next())

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

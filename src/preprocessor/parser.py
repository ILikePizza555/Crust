from typing import List, Callable, Dict, Optional, Tuple, Union
from .ast import ASTObject, Expression, ObjectMacro, FunctionMacro, EvaluatedInclude, DeferedInclude, ConditionalBranch, _expect_directive, _expect_token
from .tokenizer import Token, TokenType
from .exceptions import UnknownPreprocessorDirectiveError, UnexpectedTokenError, PreprocessorSyntaxError


class ParserBase():
    def __init__(self, token_lines: List[List[Token]]):
        self._lines = token_lines
        self._current_line = 0
        self.parse_methods: Dict[str, Callable[None, ASTObject]] = dict()

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

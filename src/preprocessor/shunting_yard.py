from typing import Set, Dict, Iterable
from .exceptions import PreprocessorSyntaxError
from .tokenizer import TokenType, Token

DEFAULT_PRECIDENCE_MAP = {
    TokenType.OP_DEFINED: 100,
    TokenType.OP_NOT: 100,
    TokenType.OP_GTE: 90,
    TokenType.OP_LTE: 90,
    TokenType.OP_LT: 90,
    TokenType.OP_GT: 90,
    TokenType.OP_EQ: 80,
    TokenType.OP_NEQ: 80,
    TokenType.AND: 50,
    TokenType.OR: 40
}


DEFAULT_RTL_SET = {TokenType.OP_NOT, TokenType.OP_DEFINED}


VALUE_TOKENS = {TokenType.NUM_LITERAL, TokenType.STRING_LITERAL, TokenType.IDENTIFIER}


OPERATOR_TOKENS = {
    TokenType.OP_LT, TokenType.OP_GT, TokenType.OP_EQ, TokenType.OP_NEQ, TokenType.OP_LTE, TokenType.OP_GTE,
    TokenType.OP_NOT, TokenType.OP_AND, TokenType.OP_OR, TokenType.OP_DEFINED, TokenType.OP_JOIN,
    TokenType.OP_CONCAT
}


class ShuntingYard():
    def __init__(self, precidence_map: Dict[TokenType, int] = DEFAULT_PRECIDENCE_MAP,
                 rtl_set: Set[Token] = DEFAULT_RTL_SET, value_token_set: Set[Token] = VALUE_TOKENS,
                 operator_token_set: Set[Token] = OPERATOR_TOKENS):
        self.precidence = precidence_map
        self.rtl_set = rtl_set
        self.value_tokens = value_token_set
        self.op_tokens = operator_token_set

        self.operator_stack = []
        self.output_stack = []

    def _compare_operators(self, op1: TokenType, op2: TokenType):
        """
        Returns 1 if op1 has a higher precidence than op2,
                0 if op1 and op2 have the sace precidence,
                -1 if op1 has a lower precidence than op2
        """
        v = self.precidence.get(op1, 0) - self.precidence.get(op2, 0)

        if v > 0:
            return 1
        elif v < 0:
            return -1
        else:
            return 0

    def _push_operator(self, op_tok: Token):
        """
        Pushes an operator onto the operator stack. If there exists operators on the operator stack,
        this function will attempt to move them to the output before pushing.
        """
        while self.operator_stack:
            op_peek = self.operator_stack[-1]
            op_comp = self._compare_operators(op_peek.token_type, op_tok.token_type)

            if op_peek.token_type is not TokenType.LPARAN and (
               op_peek.token_type in self.rtl_set or op_comp == 1):
                self.output_stack.append(self.operator_stack.pop())
            else:
                break

        self.operator_stack.append(op_tok)

    def _push_parenthesis(self, paran_tok: Token):
        if paran_tok.token_type is TokenType.LPAREN:
            self.operator_stack.append(paran_tok)
        elif paran_tok.token_type is TokenType.RPAREN:
            try:
                while self.operator_stack[-1].token_type is not TokenType.LPAREN:
                    self.output_stack.append(self.operator_stack.pop())

                # Discard the extra LPARAN
                self.operator_stack.pop()
            except IndexError:
                # Stack ran out without finding an LPARAN, we have mismatched parenthesis
                raise PreprocessorSyntaxError(paran_tok.line, paran_tok.col, "Unexpected ')'.")

    def _push_operator_stack(self):
        """
        Pushes the remainder of the operator stack onto the output stack
        """
        for operator in reversed(self.operator_stack):
            if operator.token_type in {TokenType.LPAREN, TokenType.RPAREN}:
                raise PreprocessorSyntaxError(operator.line, operator.col, "Unexpected paranthesis")
            self.output_stack.append(operator)

    def feed(self, tokens: Iterable[Token]):
        """
        Reads an expression from tokens into an RPN stack.
        `tokens` should be a be a list of that tokens that only make up the conditional expression
        """

        while tokens:
            tok = tokens.pop(0)

            if tok.token_type in self.value_tokens:
                self.output_stack.append(tok)

            # Push right-to-left associative operators to the operator stack
            # TODO: Add support for function here
            elif tok.token_type in self.rtl_set:
                self.operator_stack.append(tok)
            elif tok.token_type in (self.op_tokens - self.rtl_set):
                self._push_operator(tok)
            elif tok.token_type in {TokenType.LPAREN, TokenType.RPAREN}:
                self._push_parenthesis(tok)

        # Push all remaining operators on output stack. Note that list.extends is not used to check for mismatched parenthesis
        self._push_operator_stack()

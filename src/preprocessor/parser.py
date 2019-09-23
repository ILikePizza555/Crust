from typing import List, Set
from .tokenizer import Token, TokenType, VALUE_TOKENS, RTL_OPS, OPERATOR_TOKENS


class PreprocessorSyntaxError(Exception):
    def __init__(self, line_number, column_number, message):
        self.line_number = line_number
        self.column_number = column_number
        self.message = message

    def __str__(self):
        return f"Syntax error on line {self.line_number}, {self.column_number}: {self.message}"


def _expect_token(tokens: List[Token], expected_types: Set[TokenType], pos: int = 0) -> Token:
    """
    Asserts that the `pos` token in the list is one of `expected_types`.
    If it is, it is removed from the list and returned
    """
    peek = tokens[pos]

    if peek.token_type not in expected_types:
        raise PreprocessorSyntaxError(peek.line, peek.col, f"Expected one of {expected_types}")

    return tokens.pop(pos)


def __get_precidence(op: TokenType) -> int:
    PRECIDENCE_MAP = (
        ({TokenType.DEFINED, TokenType.NOT}, 100),
        ({TokenType.GREATER_THAN_OR_EQUAL, TokenType.LESS_THAN_OR_EQUAL,
            TokenType.LESS_THAN, TokenType.GREATER_THAN}, 90),
        ({TokenType.EQUAL, TokenType.NOT_EQUAL}, 80),
        (set(TokenType.AND), 50),
        (set(TokenType.OR), 40)
    )

    for comp_set, value in PRECIDENCE_MAP:
        if op in comp_set:
            return value
    return 0


def _compare_operators(op1: TokenType, op2: TokenType):
    """
    Returns 1 if op1 has a higher precidence than op2,
            0 if op1 and op2 have the sace precidence,
            -1 if op1 has a lower precidence than op2
    """
    v = __get_precidence(op1) - __get_precidence(op2)

    if v > 0:
        return 1
    elif v < 0:
        return -1
    else:
        return 0


def _read_conditional_expression(tokens: List[Token]):
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
            continue

        # Push right-to-left associative operators to the operator stack
        # TODO: Add support for function here
        if tok.token_type in RTL_OPS:
            operator_stack.append(tok)
            continue

        if tok.token_type in (OPERATOR_TOKENS - RTL_OPS):
            while operator_stack:
                op_peek = operator_stack[-1]
                op_comp = _compare_operators(op_peek.token_type, tok.token_type)

                if op_peek.token_type is not TokenType.LPARAN and (op_peek.token_type in RTL_OPS or op_comp == 1):
                    output_stack.append(operator_stack.pop())
                else:
                    break

            operator_stack.append(tok)

        if tok.token_type is TokenType.LPARAN:
            operator_stack.append(tok)

        if tok.token_type is TokenType.RPARAN:
            try:
                while operator_stack[-1].token_type is not TokenType.LPARAN:
                    output_stack.append(operator_stack.pop())

                # Discard the extra LPARAN
                operator_stack.pop()
            except IndexError:
                # Stack ran out without finding an LPARAN, we have mismatched parenthesis
                raise PreprocessorSyntaxError(tok.line, tok.col, "Unexpected ')'.")
    
    # Push all remaining operators on output stack. Note that list.extends is not used to check for mismatched parenthesis
    for operator in reversed(operator_stack):
        if operator.token_type is in {TokenType.LPARAN, TokenType.RPARAN}:
            raise PreprocessorSyntaxError(operator.line, operator.col, "Unexpected paranthesis")
        output_stack.append(operator)
    
    return output_stack
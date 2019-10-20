from typing import List, Set
from .exceptions import PreprocessorSyntaxError
from .tokenizer import TokenType, Token, RTL_OPS, VALUE_TOKENS, OPERATOR_TOKENS

DEFAULT_PRECIDENCE_MAP = (
    ({TokenType.DEFINED, TokenType.NOT}, 100),
    ({TokenType.GREATER_THAN_OR_EQUAL, TokenType.LESS_THAN_OR_EQUAL,
        TokenType.LESS_THAN, TokenType.GREATER_THAN}, 90),
    ({TokenType.EQUAL, TokenType.NOT_EQUAL}, 80),
    ({TokenType.AND, }, 50),
    ({TokenType.OR, }, 40)
)


def __get_operator_precidence(op: TokenType, precidence) -> int:
    for comp_set, value in precidence:
        if op in comp_set:
            return value
    return 0


def _compare_operators(op1: TokenType, op2: TokenType, precidence):
    """
    Returns 1 if op1 has a higher precidence than op2,
            0 if op1 and op2 have the sace precidence,
            -1 if op1 has a lower precidence than op2
    """
    v = __get_operator_precidence(op1, precidence) - __get_operator_precidence(op2, precidence)

    if v > 0:
        return 1
    elif v < 0:
        return -1
    else:
        return 0


def _push_operator(op_tok: Token, operator_stack: List[Token],
                   output_stack: List[Token], precidence, rtl_set: Set[Token]):
    """
    Pushes an operator onto the operator stack.
    """
    while operator_stack:
        op_peek = operator_stack[-1]
        op_comp = _compare_operators(op_peek.token_type, op_tok.token_type, precidence)

        if op_peek.token_type is not TokenType.LPARAN and (
           op_peek.token_type in rtl_set or op_comp == 1):
            output_stack.append(operator_stack.pop())
        else:
            break

    operator_stack.append(op_tok)


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


def _push_operator_stack(operator_stack: List[Token], output_stack: List[Token]):
    """
    Pushes the remainder of the operator stack onto the output stack
    """
    for operator in reversed(operator_stack):
        if operator.token_type in {TokenType.LPARAN, TokenType.RPARAN}:
            raise PreprocessorSyntaxError(operator.line, operator.col, "Unexpected paranthesis")
        output_stack.append(operator)


def shunting_yard_algorithmn(tokens: List[Token],
                             precidence_map=DEFAULT_PRECIDENCE_MAP, rtl_set=RTL_OPS,
                             value_tokens=VALUE_TOKENS, operator_tokens=OPERATOR_TOKENS):
    """
    Reads an expression from tokens into an RPN stack.
    `tokens` should be a be a list of that tokens that only make up the conditional expression
    """
    output_stack: List[Token] = []
    operator_stack: List[Token] = []

    while tokens:
        tok = tokens.pop(0)

        if tok.token_type in value_tokens:
            output_stack.append(tok)

        # Push right-to-left associative operators to the operator stack
        # TODO: Add support for function here
        elif tok.token_type in rtl_set:
            operator_stack.append(tok)
        elif tok.token_type in (operator_tokens - rtl_set):
            _push_operator(tok, operator_stack, output_stack, precidence_map, rtl_set)
        elif tok.token_type in {TokenType.LPARAN, TokenType.RPARAN}:
            _push_parenthesis(tok, operator_stack, output_stack)

    # Push all remaining operators on output stack. Note that list.extends is not used to check for mismatched parenthesis
    _push_operator_stack(operator_stack, output_stack)
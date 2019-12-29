from typing import Union, Iterable, Dict, List, Optional
from .tokenizer import TokenType, Token
from .shunting_yard import ShuntingYard


Literal = Union[str, int, float]
DefineMap = Dict[str, Primitive]


COMPARISON_OPERATOR_TOKENS = {
    TokenType.OP_GT, TokenType.OP_LT, TokenType.OP_EQ,
    TokenType.OP_NEQ, TokenType.OP_GTE, TokenType.OP_LTE
}
BOOLEAN_OPERATORS = {TokenType.OP_AND, TokenType.OP_OR}
SINGLE_BOOLEAN_OPERATOR = {TokenType.OP_NOT, TokenType.OP_DEFINED}
TOKEN_OPERATOR = {TokenType.OP_JOIN, TokenType.OP_CONCAT}

OPERATOR = COMPARISON_OPERATOR_TOKENS | BOOLEAN_OPERATORS | SINGLE_BOOLEAN_OPERATOR | TOKEN_OPERATOR

def parse_literal(literal_token: Token) -> Literal:
    """Parses a token of type  num into a python object"""
    if literal_token.type is TokenType.STRING_LITERAL:
        return literal_token.match.group(0)
    elif literal_token.type is TokenType.NUM_LITERAL:
        try:
            return int(literal_token.match.group(0))
        except ValueError:
            return float(literal_token.match.group(0))
    else:
        raise ValueError("primitive_token.type not set to a literal")


class ComparisonOperator():
    def __init__(self, token: Token):
        if token.type not in COMPARISON_OPERATOR_TOKENS:
            raise ValueError(f"token must be in set {COMPARISON_OPERATOR_TOKENS}")
        self.operator_type = token.type

    def evaluate(self, operand_1, operand_2):
        if self.operator_type is TokenType.OP_GT:
            return operand_1 > operand_2
        elif self.operator_type is TokenType.OP_LT:
            return operand_1 < operand_2
        elif self.operator_type is TokenType.OP_EQ:
            return operand_1 == operand_2
        elif self.operator_type is TokenType.OP_NEQ:
            return operand_1 != operand_2
        elif self.operator_type is TokenType.OP_GTE:
            return operand_1 >= operand_2
        elif self.operator_type is TokenType.OP_LTE:
            return operand_1 <= operand_2


class BooleanOperator():
    def __init__(self, token: Token):
        if token.type not in BOOLEAN_OPERATORS:
            raise ValueError(f"token must be in set {BOOLEAN_OPERATORS}")
        self.operator_type = token.type

    def evaluate(self, operand_1, operand_2):
        if self.operator_type is TokenType.OP_AND:
            return operand_1 and operand_2
        elif self.operator_type is TokenType.OP_OR:
            return operand_1 or operand_2


class NotOperator():
    def evaluate(self, operand):
        return not operand


class DefinedOperator():
    def evaluate(self, operand: str, define_map: DefineMap):
        return operand in define_map


def parse_operator(token: Token) -> Union[ComparisonOperator, BooleanOperator, NotOperator, DefinedOperator]:
    if token.type in COMPARISON_OPERATOR_TOKENS:
        return ComparisonOperator(token)
    elif token.type in BooleanOperator:
        return BooleanOperator(token)
    elif token.type is TokenType.NotOperator:
        return NotOperator()
    elif token.type is TokenType.DefinedOperator:
        return DefinedOperator()
    
    raise ValueError("token is not a valid operator")


class Expression():
    @classmethod
    def parse_tokens(cls, tokens: Iterable[Token], shunting_yard: Optional[ShuntingYard] = None) -> "Expression":
        if not shunting_yard:
            shunting_yard = ShuntingYard()
        shunting_yard.feed(tokens)

        expression_stack = map(lambda x: , shunting_yard.output_stack)
        return cls(list(expression_stack))

    def __init__(self, expression_stack: list):
        self.expression_stack = expression_stack

    def evaluate(self, define_map: DefineMap) -> bool:
        s = []

        for token in expression_stack:
            pass

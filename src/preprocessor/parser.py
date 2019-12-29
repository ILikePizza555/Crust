from typing import Union, Iterable, Dict, List, Optional, Set
from .tokenizer import TokenType, Token, COMPARISON_OPERATOR_TYPES, BOOLEAN_OPERATOR_TYPES, COMPARISON_OPERATOR_TYPES, OPERATOR_TYPES, LITERAL_TYPES
from .shunting_yard import ShuntingYard


Literal = Union[str, int, float]
DefineMap = Dict[str, Literal]


def parse_literal(literal_token: Token) -> Literal:
    """Parses a token of type num into a python object"""
    if literal_token.type is TokenType.STRING_LITERAL:
        return literal_token.match.group(0)
    elif literal_token.type is TokenType.NUM_LITERAL:
        try:
            return int(literal_token.match.group(0))
        except ValueError:
            return float(literal_token.match.group(0))
    else:
        raise ValueError("primitive_token.type not set to a literal")
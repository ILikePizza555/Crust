from typing import Union
from tokenizer import TokenType, Token


Primitive = Union[str, int, float]


def parse_literal(literal_token: Token) -> Primitive:
    """Parses a token of type string or num into a python object"""
    if literal_token.type is TokenType.STRING_LITERAL:
        return literal_token.match.group(0)
    elif literal_token.type is TokenType.NUM_LITERAL:
        try:
            return int(literal_token.match.group(0))
        except ValueError:
            return float(literal_token.match.group(0))
    else:
        raise ValueError("primitive_token.type not set to a literal")



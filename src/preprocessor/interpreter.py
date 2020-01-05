from typing import List, Dict, Set, Union
from .tokenizer import TokenType, VALUE_TYPES, OPERATOR_TYPES, Token
from .parser import ASTObject, IncludeDirective, DifferedIncludeDirective, ObjectMacro, FunctionMacro
from .shunting_yard import ShuntingYard


MacroTable = Dict[str, Union[ObjectMacro, FunctionMacro]]


def resolve_include(d: DifferedIncludeDirective, macro_table: MacroTable) -> IncludeDirective:
    identifier_value = macro_table[d.identifier]

    if isinstance(identifier_value, FunctionMacro):
        raise NotImplementedError("Evaluating of function macros in includes is not currently supported.")

    return IncludeDirective.from_tokens(identifier_value.tokens)


def resolve_value(token: Token):
    """Resolves a value token to a python object"""
    if token.type == TokenType.NUM_LITERAL:
        try:
            return int(token.value.group())
        except ValueError:
            return float(token.value.group())
    elif token.type == TokenType.STRING_LITERAL:
        return token.value.group(1)
    raise ValueError(f"Expected a token of type NUM_LITERAL or STRING_LITERAL, got {token.type} instead")


def evaluate_expression(expression_tokens: List[Token]):
    sy = ShuntingYard()
    sy.feed(expression_tokens)

    eval_stack = []
    for o in sy.output_stack:
        if o.type in VALUE_TYPES:
            eval_stack.append(resolve_value(o))
            continue

        if o.type not in OPERATOR_TYPES:
            raise ValueError(f"{o.line}, {o.col}: Expected an operator.")

        # Unary operators

        if o.type is TokenType.OP_NOT:
            eval_stack.append(not eval_stack.pop())

        # TODO: Defined implementation

        # Normal operators

        op_a = eval_stack.pop()
        op_b = eval_stack.pop()

        if o.type is TokenType.OP_AND:
            eval_stack.append(op_a and op_b)
        elif o.type is TokenType.OP_OR:
            eval_stack.append(op_a or op_b)
        elif o.type is TokenType.OP_EQ:
            eval_stack.append(op_a == op_b)
        elif o.type is TokenType.OP_GT:
            eval_stack.append(op_a > op_b)
        elif o.type is TokenType.OP_GTE:
            eval_stack.append(op_a >= op_b)
        elif o.type is TokenType.OP_LT:
            eval_stack.append(op_a < op_b)
        elif o.type is TokenType.OP_LTE:
            eval_stack.append(op_a <= op_b)
        elif o.type is TokenType.OP_NEQ:
            eval_stack.append(op_a != op_b)

    return eval_stack[0]


def evaluate_ast(ast_objects: List[ASTObject]):
    dependencies: Set[IncludeDirective] = set()
    macro_table: MacroTable = dict()

    i = 0
    while i < len(ast_objects):
        o = ast_objects[i]

        if isinstance(o, IncludeDirective):
            dependencies.add(IncludeDirective)
        elif isinstance(o, DifferedIncludeDirective):
            dependencies.add(resolve_include(o, macro_table))
        elif isinstance(o, ObjectMacro):
            macro_table[o.identifier] = o
        elif isinstance(o, FunctionMacro):
            macro_table[o.identifier] = o

        i += 1

    return dependencies
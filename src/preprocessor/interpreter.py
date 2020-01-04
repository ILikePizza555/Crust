from typing import List, Dict, Set, Union
from .parser import ASTObject, IncludeDirective, DifferedIncludeDirective, ObjectMacro, FunctionMacro


MacroTable = Dict[str, Union[ObjectMacro, FunctionMacro]]


def resolve_include(d: DifferedIncludeDirective, macro_table: MacroTable) -> IncludeDirective:
    identifier_value = macro_table[d.identifier]

    if isinstance(identifier_value, FunctionMacro):
        raise NotImplementedError("Evaluating of function macros in includes is not currently supported.")

    return IncludeDirective.from_tokens(identifier_value.tokens)


def evaluate_ast(ast_objects: List[ASTObject]):
    dependencies: Set[IncludeDirective] = set()
    macro_table: MacroTable = dict()

    for o in ast_objects:
        if isinstance(o, IncludeDirective):
            dependencies.add(IncludeDirective)
        elif isinstance(o, DifferedIncludeDirective):
            dependencies.add(resolve_include(o, macro_table))
        elif isinstance(o, ObjectMacro):
            macro_table[o.identifier] = o
        elif isinstance(o, FunctionMacro):
            macro_table[o.identifier] = o
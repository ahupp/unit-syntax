import ast
from .parser import parse_string, UnitsExpr
import pint


class UnitExprTransformer(ast.NodeTransformer):
    """
    AST transformer to turn python-with-units into standard python
    """

    ureg: pint.UnitRegistry

    def __init__(self, ureg: pint.UnitRegistry):
        self.ureg = ureg

    def generic_visit(self, node):
        if isinstance(node, UnitsExpr):
            # Check units are valid
            try:
                self.ureg.parse_units(node.units.value)
            except pint.UndefinedUnitError as e:
                raise SyntaxError(e)

            value = self.generic_visit(node.value)
            return ast.Call(
                ast.Name(id="_unit_syntax_q", ctx=ast.Load()),
                args=[value, node.units],
                keywords=[],
            )
        else:
            return super().generic_visit(node)


def transform_to_ast(code: str) -> ast.AST:
    "Transform a string of python-with-units into a standard python ast.AST"
    tree = parse_string(code, mode="file")
    ureg = pint._DEFAULT_REGISTRY
    tree_std = UnitExprTransformer(ureg).visit(tree)
    return ast.fix_missing_locations(tree_std)


def transform_to_str(code: str) -> str:
    "Transform a string of python-with-units into a standard python string"
    tree_std = transform_to_ast(code)
    return ast.unparse(tree_std)

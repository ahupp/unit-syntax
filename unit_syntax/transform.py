import ast
import pint
from .parser import parse_string, UnitsExpr
from import_transforms import SourceTransform


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


class UnitSourceTransform(SourceTransform):
    ureg: pint.UnitRegistry

    def __init__(self, ureg: pint.UnitRegistry | None):
        if ureg is None:
            ureg = pint._DEFAULT_REGISTRY
        self.ureg = ureg

    def injected_globals(self) -> dict[str, any]:
        return {"_unit_syntax_q": self.ureg.Quantity}

    def transform(self, source: str) -> ast.AST:
        tree = parse_string(source, mode="file")
        tree_std = UnitExprTransformer(self.ureg).visit(tree)
        return ast.fix_missing_locations(tree_std)

    def transform_to_str(self, source: str) -> str:
        "Transform a string of python-with-units into a standard python string"
        tree_std = self.transform(source)
        return ast.unparse(tree_std)

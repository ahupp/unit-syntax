import ast
import pint
from typing import Any
from .parser import parse_string, UnitsExpr


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
            return ast.copy_location(
                ast.Call(
                    ast.Name(id="_unit_syntax_q", ctx=ast.Load()),
                    args=[value, node.units],
                    keywords=[],
                ),
                node,
            )
        else:
            return super().generic_visit(node)


class UnitSourceTransform:
    def __init__(self, ureg: pint.UnitRegistry | None):
        self._ureg = ureg

    @property
    def ureg(self):
        return self._ureg if self._ureg is not None else pint.get_application_registry()

    def _quantity(self, value, units):
        # Resolve the application registry at call time, including in notebooks
        # whose injected globals outlive an application-registry replacement.
        return self.ureg.Quantity(value, units)

    def injected_globals(self) -> dict[str, Any]:
        return {"_unit_syntax_q": self._quantity}

    def transform(self, source: str) -> ast.Module:
        tree = parse_string(source, mode="exec")
        tree_std = UnitExprTransformer(self.ureg).visit(tree)
        return ast.fix_missing_locations(tree_std)

    def transform_to_str(self, source: str) -> str:
        "Transform a string of python-with-units into a standard python string"
        tree_std = self.transform(source)
        return ast.unparse(tree_std)

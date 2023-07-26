import ast
from io import StringIO
from typing import Iterator, Optional, Generator
from .parser import parse_string, UnitsExpr
import pint
from pprint import pprint


class UnitExprTransformer(ast.NodeTransformer):
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
                func=ast.Attribute(
                    ast.Name(id="unit_syntax", ctx=ast.Load()),
                    "Quantity",
                    ctx=ast.Load(),
                ),
                args=[value, node.units],
                keywords=[],
            )
        else:
            return super().generic_visit(node)


def transform(code: str) -> str:
    """Transform a string of python-with-units into a standard python string"""

    tree = parse_string(code, mode="file")
    ureg = pint.UnitRegistry()
    tree_std = UnitExprTransformer(ureg).visit(tree)
    tree_std = ast.fix_missing_locations(tree_std)
    return ast.unparse(tree_std)


def transform_lines(lines: list[str]) -> list[str]:
    """IPython transforms provide a list of strings in the current cell, but to parse correctly we
    need to parse them as a single string"""
    return transform("".join(lines)).splitlines(keepends=True)

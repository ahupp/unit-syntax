"""Typed public interface to the parser generated from python_units.gram."""

import ast
from collections.abc import Callable, Iterator
from tokenize import TokenInfo
from typing import Literal, overload

class UnitsExpr(ast.expr):
    value: ast.expr
    units: ast.Constant
    def __init__(
        self, value: ast.expr, units: ast.Constant, **locations: int
    ) -> None: ...

def parse_file(
    path: str,
    py_version: tuple[int, ...] | None = None,
    token_stream_factory: (
        Callable[[Callable[[], str]], Iterator[TokenInfo]] | None
    ) = None,
    verbose: bool = False,
) -> ast.Module: ...
@overload
def parse_string(
    source: str,
    mode: Literal["exec"],
    py_version: tuple[int, ...] | None = None,
    token_stream_factory: (
        Callable[[Callable[[], str]], Iterator[TokenInfo]] | None
    ) = None,
    verbose: bool = False,
) -> ast.Module: ...
@overload
def parse_string(
    source: str,
    mode: Literal["eval"],
    py_version: tuple[int, ...] | None = None,
    token_stream_factory: (
        Callable[[Callable[[], str]], Iterator[TokenInfo]] | None
    ) = None,
    verbose: bool = False,
) -> ast.Expression: ...

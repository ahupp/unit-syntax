import ast
import sys

import pytest

from unit_syntax.parser import UnitsExpr, parse_string
from unit_syntax.transform import UnitSourceTransform


def structure(value, locations=False):
    if isinstance(value, ast.AST):
        fields = list(value._fields) + (list(value._attributes) if locations else [])
        return type(value).__name__, [
            (name, structure(getattr(value, name, None), locations)) for name in fields
        ]
    if isinstance(value, list):
        return [structure(item, locations) for item in value]
    return value


@pytest.mark.parametrize(
    "source",
    [
        "é = 3; value = é + 1\n",
        "match x:\n case {'x': value, **rest}: pass\n",
        "try:\n pass\nexcept* ValueError as e:\n pass\n",
        "def f[T](value: T) -> T:\n return value\n",
        "type Pair[T] = tuple[T, T]\n",
        "type Pair[T = int] = tuple[T, T]\n",
        "def f[*Ts = *tuple[int, str], **P = [int]](): pass\n",
        "x = f'{{é}}\\n{1 + 2 = :03d}'\n",
        "x = f'{f\"{1 + 2}\"}'\n",
        'x = f"{\n 1 + 2 # comment\n}"\n',
        'x = t"before { 1 + 2 = !r:03} after"\n',
        'x = t"a" t"{1}"\n',
        "try:\n pass\nexcept ValueError, TypeError:\n pass\n",
        "lazy import math\nlazy from math import sqrt\n",
        "x = [*row for row in [[1], [2]]]\n",
        "x = {**row for row in [{'a': 1}]}\n",
    ],
)
def test_matches_native_python_grammar(source):
    try:
        expected = ast.parse(source)
    except SyntaxError:
        pytest.skip("Syntax is newer than the test interpreter")
    actual = parse_string(source, mode="exec")
    assert structure(actual) == structure(expected)
    compile(actual, "grammar_test.py", "exec")


@pytest.mark.parametrize(
    "source",
    [
        "é = 3; model = 5 mm\n",
        "é = f'{1+2}'\n",
        'x = t"{ 1 + 2 }"\n',
    ],
)
def test_utf8_source_locations(source):
    if " mm" in source:
        tree = parse_string(source, mode="exec")
        unit = next(node for node in ast.walk(tree) if isinstance(node, UnitsExpr))
        assert ast.get_source_segment(source, unit) == "5 mm"
        assert ast.get_source_segment(source, unit.value) == "5"
        assert ast.get_source_segment(source, unit.units) == "mm"
    else:
        try:
            expected = ast.parse(source)
        except SyntaxError:
            pytest.skip("Syntax is newer than the test interpreter")
        assert structure(parse_string(source, mode="exec"), True) == structure(
            expected, True
        )


@pytest.mark.parametrize(
    "source",
    [
        "type Q[T = int] = list[T]\nresult = 5 mm\n",
        "class C[T]:\n size = 5 mm\nresult = C.size\n",
        "lazy import math\nresult = 5 mm\n",
        'result = f"{ 3 mm = }"\n',
        'result = t"{ 3 mm }"\n',
        'result = t"{3 mm=}"\n',
    ],
)
def test_new_syntax_composes_with_units(source):
    if sys.version_info < (3, 15):
        pytest.skip("Python 3.15 execution coverage")
    transform = UnitSourceTransform(None)
    namespace = transform.injected_globals()
    exec(compile(transform.transform(source), "unit_grammar.py", "exec"), namespace)
    result = namespace["result"]
    if source.startswith("result = t"):
        assert result.interpolations[0].value.magnitude == 3
        assert result.interpolations[0].expression.strip() == "3 mm"
    elif source.startswith("result = f"):
        assert result.startswith(" 3 mm = ")
    else:
        assert result.to("mm").magnitude == 5


@pytest.mark.parametrize(
    "source", ["1 + 3 mm", "3 mm + 1", "t'hello' 'world'", "f'hello' t'world'"]
)
def test_invalid_operator_and_string_mixing(source):
    with pytest.raises(SyntaxError):
        parse_string(source, mode="eval")

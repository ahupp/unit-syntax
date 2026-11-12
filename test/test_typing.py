import ast
from pathlib import Path
import subprocess
import sys

import pint
import pytest

from unit_syntax.check import checking_source, check_paths


def check(tmp_path, source):
    path = tmp_path / "model.py"
    path.write_text(source)
    return path, check_paths([path])


def test_valid_dimensions_and_numeric_coercion(tmp_path):
    _, (code, output) = check(
        tmp_path,
        """
from math import sqrt
from typing import SupportsFloat
from unit_syntax.typing import Quantity, Length, Area, Velocity, Force
x = 18 mm
y = 27 mm
ratio = x / y
scalar: SupportsFloat = ratio
result = x * sqrt(1 - ratio * ratio)
percent = sqrt(50 percent)
area: Quantity[Area] = x * y
volume = area * x
back: Quantity[Length] = volume / area
speed: Quantity[Velocity] = x / (2 seconds)
force: Quantity[Force] = (2 kg) * (3 m/s**2)
converted = (1 m) mm
custom = (1 m**7) / (2 mm**7)
sqrt(custom)
def double(length: Quantity[Length]) -> Quantity[Length]:
    return length * 2
double(x)
""",
    )
    assert code == 0, output


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("x + (2 seconds)", "Operator `+`"),
        ("sqrt(x)", "function `sqrt`"),
        ("sqrt(30 deg)", "Quantity[Angle]"),
        ("float(x)", "float.__new__"),
        ("(2 seconds) mm", "Quantity.__init__"),
        ("x ** 2 + (2 mm)", "Operator `+`"),
        ("x + 2", "Operator `+`"),
        ("sqrt((1 m**7) * (2 m**7))", "function `sqrt`"),
    ],
)
def test_invalid_operations_report_original_locations(tmp_path, expression, expected):
    path, (code, output) = check(
        tmp_path, f"from math import sqrt\nx = 18 mm\nresult = {expression}\n"
    )
    assert code == 1, output
    assert f"{path}:3:" in output
    assert expected in output
    assert "_unit_syntax_types" not in output
    assert "unit-syntax-check-" not in output


def test_function_annotations_reject_wrong_dimensions(tmp_path):
    _, (code, output) = check(
        tmp_path,
        """
from unit_syntax.typing import Quantity, Length
def model(radius: Quantity[Length]) -> Quantity[Length]:
    return radius
model(2 seconds)
""",
    )
    assert code == 1
    assert "Quantity[Time]" in output


def test_checking_does_not_execute_source(tmp_path):
    sentinel = tmp_path / "executed"
    _, (code, output) = check(
        tmp_path, f"open({str(sentinel)!r}, 'w').write('bad')\nx=1 mm\n"
    )
    assert code == 0, output
    assert not sentinel.exists()


def test_project_imports_are_checked_without_execution(tmp_path):
    sentinel = tmp_path / "import-executed"
    (tmp_path / "dimensions.py").write_text(
        f"open({str(sentinel)!r}, 'w').write('bad')\nsize = 1 mm\n"
    )
    _, (code, output) = check(
        tmp_path, "from math import sqrt\nfrom dimensions import size\nsqrt(size)\n"
    )
    assert code == 1, output
    assert "Quantity[Length]" in output
    assert not sentinel.exists()


def test_unselected_invalid_module_does_not_block_check(tmp_path):
    (tmp_path / "unrelated.py").write_text("x = 1 not_a_unit\n")
    _, (code, output) = check(tmp_path, "x = 1 mm\n")
    assert code == 0, output


def test_unicode_columns_and_future_imports(tmp_path):
    source = '"doc"\nfrom __future__ import annotations\nfrom math import sqrt\né = 18 mm; result = sqrt(é)\n'
    view = checking_source(source)
    ast.parse(view.source)
    assert view.source.startswith('"doc"\nfrom __future__ import annotations\n')
    path, (code, output) = check(tmp_path, source)
    assert code == 1, output
    assert f"{path}:4:26:" in output


def test_runtime_stays_pint_and_normalizes_scaled_ratios():
    from unit_syntax.typing import Quantity
    from unit_syntax.transform import UnitSourceTransform

    transform = UnitSourceTransform()
    namespace = transform.injected_globals()
    exec(
        compile(transform.transform("value=(1 m)/(1 mm)\n"), "units.py", "exec"),
        namespace,
    )
    assert Quantity is pint.Quantity
    assert isinstance(namespace["value"], pint.Quantity)
    assert float(namespace["value"]) == 1000


def test_cli(tmp_path):
    path = tmp_path / "model.py"
    path.write_text("from math import sqrt\nx = sqrt(5 mm)\n")
    result = subprocess.run(
        [sys.executable, "-m", "unit_syntax", "--check", str(path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert f"{path}:2:" in result.stdout


@pytest.mark.skipif(sys.version_info < (3, 15), reason="Python 3.15 grammar")
@pytest.mark.parametrize("source", [
    "lazy import math\nx = math.sqrt(5 mm)\n",
    "from math import sqrt\ndef identity[T](value: T) -> T: return value\nx = sqrt(identity(5 mm))\n",
    'from math import sqrt\nx = t"{sqrt(5 mm)}"\n',
])
def test_type_checks_new_grammar_forms(tmp_path, source):
    path, (code, output) = check(tmp_path, source)
    assert code == 1, output
    assert "Quantity[Length]" in output
    assert str(path) in output


def test_reserved_alias_collision_is_avoided(tmp_path):
    _, (code, output) = check(tmp_path, "_unit_syntax_types = 1\nx = 1 mm\n")
    assert code == 0, output


def test_unknown_unit_has_source_diagnostic(tmp_path):
    path, (code, output) = check(tmp_path, "x = 1 not_a_unit\n")
    assert code == 1
    assert f"{path}:1:7:" in output
    assert "not_a_unit" in output


def test_unicode_string_separator_keeps_checker_source_lines(tmp_path):
    path, (code, output) = check(tmp_path, 'label="a\u2028b"\nvalue: int = 5 mm\n')
    assert code == 1, output
    assert f"{path}:2:" in output
    assert "invalid-assignment" in output

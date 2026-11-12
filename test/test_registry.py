"""Registry selection stays consistent across transforms and import entry points."""

import ast
import subprocess
import sys

import pint
import pytest

from unit_syntax.check import check_paths
from unit_syntax.transform import UnitSourceTransform


@pytest.fixture(autouse=True)
def restore_application_registry():
    original = pint.get_application_registry().get()
    try:
        yield
    finally:
        pint.set_application_registry(original)


def custom_registry(scale):
    registry = pint.UnitRegistry()
    registry.define(f"custom_span_xyz = {scale} * meter")
    return registry


@pytest.mark.parametrize("replace_after_transform", [False, True])
def test_default_constructor_follows_application_registry(replace_after_transform):
    transform = UnitSourceTransform()
    namespace = transform.injected_globals()
    registry = custom_registry(2)
    if not replace_after_transform:
        pint.set_application_registry(registry)
    tree = transform.transform("value = 1 meter\n")
    if replace_after_transform:
        pint.set_application_registry(registry)
    exec(compile(tree, "model.py", "exec"), namespace)
    assert namespace["value"]._REGISTRY is registry


def test_checker_and_execution_share_custom_application_registry(tmp_path):
    registry = custom_registry(2)
    pint.set_application_registry(registry)
    transform = UnitSourceTransform()
    namespace = transform.injected_globals()
    exec(
        compile(transform.transform("value = 1 custom_span_xyz\n"), "model.py", "exec"),
        namespace,
    )
    assert namespace["value"].to("meter").magnitude == 2
    path = tmp_path / "model.py"
    path.write_text("from math import sqrt\nvalue = sqrt(1 custom_span_xyz)\n")
    code, output = check_paths([path])
    assert code == 1, output
    assert "Quantity[Length]" in output
    assert f"{path}:2:" in output


def test_notebook_constructor_follows_registry_after_extension_initialization():
    from unit_syntax.ipython import _UNIT_TRANSFORM, transform_lines

    namespace = _UNIT_TRANSFORM.injected_globals()
    registry = custom_registry(2)
    pint.set_application_registry(registry)
    source = "".join(transform_lines(["value = 1 custom_span_xyz\n"]))
    exec(compile(ast.parse(source), "notebook.py", "exec"), namespace)
    assert namespace["value"]._REGISTRY is registry
    assert namespace["value"].to("meter").magnitude == 2


def test_imports_share_application_registry_across_global_and_package_hooks(tmp_path):
    package = tmp_path / "registry_package_xyz"
    nested = package / "nested"
    nested.mkdir(parents=True)
    initializer = (
        "from unit_syntax import enable_units_for_package\n"
        "enable_units_for_package(__name__)\n"
    )
    (package / "__init__.py").write_text(initializer)
    (nested / "__init__.py").write_text(initializer)
    (package / "model.py").write_text("value = 1 custom_span_xyz\n")
    (nested / "model.py").write_text("value = 1 custom_span_xyz\n")
    (nested / "later.py").write_text("value = 1 custom_span_xyz\n")
    script = tmp_path / "model.py"
    script.write_text(
        "import pint\n"
        "registry = pint.UnitRegistry()\n"
        "registry.define('custom_span_xyz = 2 * meter')\n"
        "pint.set_application_registry(registry)\n"
        "import registry_package_xyz.model as parent\n"
        "import registry_package_xyz.nested.model as child\n"
        "assert parent.value._REGISTRY is registry\n"
        "assert child.value._REGISTRY is registry\n"
        "assert parent.value.to('meter').magnitude == 2\n"
        "assert child.value.to('meter').magnitude == 2\n"
        "replacement = pint.UnitRegistry()\n"
        "replacement.define('custom_span_xyz = 3 * meter')\n"
        "pint.set_application_registry(replacement)\n"
        "import registry_package_xyz.nested.later as later\n"
        "assert later.value._REGISTRY is replacement\n"
        "assert later.value.to('meter').magnitude == 3\n"
        "print('shared application registry')\n"
    )
    result = subprocess.run(
        [sys.executable, "-m", "unit_syntax", str(script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "shared application registry\n"

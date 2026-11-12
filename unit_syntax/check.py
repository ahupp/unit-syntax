"""Check unit-enabled Python with ty without importing or executing that source."""

from __future__ import annotations

import ast
from bisect import bisect_right
from dataclasses import dataclass
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tokenize

import pint

from .parser import UnitsExpr, parse_string
from .typing import DIMENSIONS, dimension_key

_DIMENSION_NAMES = {dimension_key(value): name for name, value in DIMENSIONS.items()}
_IGNORED = {
    ".git",
    ".jj",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def _line_offsets(source):
    return [0] + [match.end() for match in re.finditer("\n", source)]


@dataclass
class CheckingSource:
    source: str
    original: str
    origins: list[int]

    def original_position(self, line, column):
        lines = _line_offsets(self.source)
        index = lines[min(line - 1, len(lines) - 1)] + column - 1
        origin = self.origins[min(index, len(self.origins) - 1)] if self.origins else 0
        original_lines = _line_offsets(self.original)
        row = bisect_right(original_lines, origin) - 1
        return row + 1, origin - original_lines[row] + 1


def _unit_dimension(ureg, unit):
    quantity = ureg.Quantity(1, unit).to_base_units()
    dimensions = dict(quantity.dimensionality)
    # Pint intentionally treats angles as dimensionless. Keep their semantic
    # distinction for numeric coercion and arithmetic in the checking view.
    angle = quantity.units._units.get("radian", 0)
    if angle:
        dimensions["[angle]"] = angle
    return dimension_key(dimensions)


def checking_source(source: str, *, ureg=None, filename="<unknown>") -> CheckingSource:
    """Lower suffixes to typed constructors, with a map to original characters."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        tree = parse_string(source, mode="exec")
    units = [node for node in ast.walk(tree) if isinstance(node, UnitsExpr)]
    if not units:
        return CheckingSource(source, source, list(range(len(source))))
    if ureg is None:
        ureg = pint.get_application_registry()
    lines = source.split("\n")
    offsets = _line_offsets(source)

    def position(line, byte_column):
        return offsets[line - 1] + len(
            lines[line - 1].encode("utf-8")[:byte_column].decode("utf-8")
        )

    def start(node):
        return position(node.lineno, node.col_offset)

    def end(node):
        return position(node.end_lineno, node.end_col_offset)

    occupied = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    occupied.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    occupied.update(
        node.asname or node.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.alias)
    )
    alias = "_unit_syntax_types"
    while alias in occupied:
        alias += "_"
    units.sort(key=lambda node: (start(node), -end(node)))

    def generated(text, origin):
        return text, [origin] * len(text)

    def render(a, b, excluded=None):
        text, mapping, cursor = [], [], a
        for node in units:
            left, right = start(node), end(node)
            if node is excluded or left < cursor or right > b:
                continue
            text.append(source[cursor:left])
            mapping.extend(range(cursor, left))
            unit_start = start(node.units)
            try:
                key = _unit_dimension(ureg, node.units.value)
            except (pint.PintError, ValueError) as exc:
                raise SyntaxError(
                    str(exc),
                    (
                        filename,
                        node.units.lineno,
                        node.units.col_offset + 1,
                        lines[node.units.lineno - 1],
                    ),
                ) from exc
            name = _DIMENSION_NAMES.get(key)
            dimension = (
                f"{alias}.{name}"
                if name
                else f"{alias}.Dimension[{alias}.Literal[{key!r}]]"
            )
            prefix, prefix_map = generated(f"{alias}.Quantity[{dimension}](", left)
            value, value_map = render(left, unit_start, node)
            suffix, suffix_map = generated(f", {node.units.value!r})", unit_start)
            text.extend([prefix, value, suffix])
            mapping.extend(prefix_map + value_map + suffix_map)
            cursor = right
        text.append(source[cursor:b])
        mapping.extend(range(cursor, b))
        return "".join(text), mapping

    lowered, origins = render(0, len(source))
    # Preserve the module docstring and Python's future-import placement rule.
    insertion = 0
    for index, statement in enumerate(tree.body):
        docstring = (
            index == 0
            and isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
        future = (
            isinstance(statement, ast.ImportFrom) and statement.module == "__future__"
        )
        if not (docstring or future):
            break
        end_line = statement.end_lineno
        assert end_line is not None  # Parsed statements always carry source locations.
        insertion = offsets[end_line] if end_line < len(offsets) else len(source)
    # Every original character survives outside replacements. Locate the
    # insertion in the generated view by its mapped original position.
    generated_insertion = next(
        (i for i, origin in enumerate(origins) if origin >= insertion), len(lowered)
    )
    prelude = f"from unit_syntax import typing as {alias}\n"
    if generated_insertion and lowered[generated_insertion - 1] != "\n":
        prelude = "\n" + prelude
    lowered = lowered[:generated_insertion] + prelude + lowered[generated_insertion:]
    origins[generated_insertion:generated_insertion] = [insertion] * len(prelude)
    return CheckingSource(lowered, source, origins)


def _project_root(paths):
    roots = []
    for path in paths:
        root = path if path.is_dir() else path.parent
        for parent in [root, *root.parents]:
            if (parent / "pyproject.toml").exists():
                root = parent
                break
        else:
            while (root / "__init__.py").exists():
                root = root.parent
        roots.append(root)
    return Path(os.path.commonpath(roots))


def check_paths(paths, *, project=None):
    """Return (exit code, diagnostics), keeping all checked source read-only."""
    paths = [Path(path).resolve() for path in paths]
    for path in paths:
        if not path.exists():
            return 2, f"File or directory does not exist: {path}\n"
    if importlib.util.find_spec("ty") is None:
        return 2, 'Install the checker with: pip install "unit-syntax[check]"\n'
    root = Path(project).resolve() if project else _project_root(paths)
    if any(not path.is_relative_to(root) for path in paths):
        return 2, "All checked paths must be inside the project root.\n"
    with tempfile.TemporaryDirectory(prefix="unit-syntax-check-") as temporary:
        mirror = Path(temporary)
        mappings = {}
        for directory, subdirs, files in os.walk(root):
            subdirs[:] = [
                name
                for name in subdirs
                if name not in _IGNORED and not name.startswith(".")
            ]
            for name in files:
                if not name.endswith((".py", ".pyi")):
                    continue
                original = Path(directory) / name
                relative = original.relative_to(root)
                with tokenize.open(original) as stream:
                    source = stream.read()
                try:
                    view = (
                        checking_source(source, filename=str(original))
                        if name.endswith(".py")
                        else CheckingSource(source, source, list(range(len(source))))
                    )
                except SyntaxError as exc:
                    if any(
                        original == target
                        or target.is_dir()
                        and original.is_relative_to(target)
                        for target in paths
                    ):
                        return (
                            1,
                            f"{original}:{exc.lineno or 1}:{exc.offset or 1}: error[invalid-syntax] {exc.msg}\n",
                        )
                    view = CheckingSource(source, source, list(range(len(source))))
                destination = mirror / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(view.source, encoding="utf-8")
                mappings[relative] = view
        targets = [str(path.relative_to(root)) for path in paths]
        command = [
            sys.executable,
            "-m",
            "ty",
            "check",
            *targets,
            "--project",
            str(mirror),
            "--python",
            sys.executable,
            "--extra-search-path",
            str(Path(__file__).resolve().parent.parent),
            "--output-format",
            "concise",
            "--color",
            "never",
        ]
        result = subprocess.run(command, cwd=mirror, text=True, capture_output=True)
        output = []
        for line in (result.stdout + result.stderr).splitlines():
            match = re.match(r"^(.*?):(\d+):(\d+): (.*)$", line)
            if match:
                path, row, column, message = match.groups()
                path = Path(path)
                if path.is_absolute() and path.is_relative_to(mirror):
                    path = path.relative_to(mirror)
                if path in mappings:
                    row, column = mappings[path].original_position(
                        int(row), int(column)
                    )
                    line = f"{root / path}:{row}:{column}: {message}"
            for key, name in _DIMENSION_NAMES.items():
                for quote in ['"', "'"]:
                    line = line.replace(
                        f"Dimension[Literal[{quote}{key}{quote}]]]", f"{name}]"
                    )
            if "SupportsFloat" in line and "Quantity[" in line:
                line += " Only dimensionless quantities support numeric conversion."
            output.append(line.replace(str(mirror), str(root)))
        return result.returncode, "\n".join(output) + "\n"

# Python 3.15 and dimensional typing validation

Base repository revision: `684955f5` (v0.3.1).

Local validation on 2026-10-29:

- Python 3.15.2: **53 tests passed**, including original execution/import tests,
  CPython grammar comparisons, source locations, and positive/negative ty tests.
- Python 3.11.14: **32 passed, 21 skipped**. Skips cover syntax unavailable in
  that interpreter; ordinary Python and dimension checking passed.
- ty 0.0.95 accepted the generated stubs. Tests prove dimensionless numeric
  coercion, dimensional function annotations, incompatible addition, invalid
  conversions, generic declarations, lazy imports, and template-string checks.
- Pint 0.26.2 on Python 3.15.2; Pint 0.25.3 on Python 3.11.14. Runtime values
  remain Pint quantities. A scaled dimensionless ratio converts to `1000`.
- pegen 0.3.0 generated identical parser source under Python 3.11 and 3.15.
  Regenerating both the parser and typing stubs produced identical checked-in
  contents.
- Parsed and compiled Python 3.15.2's `contextlib`, `functools`, `dataclasses`,
  `enum`, and `importlib._bootstrap_external` through the unit-enabled parser.
- Source and wheel distributions built successfully. The wheel contains
  `typing.pyi`, `py.typed`, the checker, and parser support module.

Checking source does not execute it or imported project modules. Diagnostics
retain original filenames and line/column positions, including Unicode and
future imports. The checked-in example exercises the same typed source path.

Common dimensional algebra is normalized by generated overloads. Other
products retain symbolic dimensions and can yield conservative rejections;
this is not a complete symbolic algebra engine. Magnitude/array-shape checks,
dynamic units, and Pint contexts remain runtime responsibilities.

The CI matrix covers Python 3.11, 3.14, and 3.15. Remote CI has not been run;
Python 3.14 was not independently tested in this local run. Nothing has been
published to PyPI or pushed to GitHub.


## uv management and registry fixes (2026-11-12)

The project now uses PEP 621 metadata, a default development dependency group,
`uv.lock`, and the uv build backend. Poetry configuration and its lockfile were
removed. Both GitHub Actions workflows use uv and run the library type check.
The test matrix does not cancel other versions after one version fails.

Local validation used uv 0.9.24 and locked ty 0.0.95:

| Python | Tests | Library type check |
| --- | --- | --- |
| 3.10 | 51 passed, 22 skipped | Pass |
| 3.11 | 52 passed, 21 skipped | Pass |
| 3.14 | 61 passed, 12 skipped | Pass |
| 3.15 | 73 passed | Pass |

Skips cover language syntax unavailable in the corresponding interpreter.
The two original Python 3.11 Unicode/f-string source-location failures were
reproduced before the fix; the same assertions now pass with additional Unicode
cases. No failing test was removed or weakened.

Registry regressions cover replacing the application registry before and after
transformation, notebook constructors initialized before replacement, explicit
registries, matching runtime/checker dimensions, and nested package-specific
registries taking precedence over a standalone runner's global import hook.

Parser and dimensional-stub regeneration produce identical checked-in contents
on all four interpreters. `uv lock --check` passes. `uv build` produces a wheel
and a source archive; the wheel includes the CLI entry point, parser and quantity
stubs, and `py.typed`. The source archive also includes the lockfile, changelog,
grammar, generators, examples, and tests.

`uv run ty check unit_syntax` checks handwritten library files and public stubs.
The pegen-generated parser implementation is excluded from ty; its typed public
interface, grammar comparisons, compilation, and regeneration remain checked.
These are local results; GitHub Actions records remote execution separately.

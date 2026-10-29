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

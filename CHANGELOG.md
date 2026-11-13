# Changelog

## 0.4.1

### Changed

- Documented `uvx --with unit-syntax ipython` startup, gave unit registries
  their own README section, and removed the standalone-script import-hook note.
- Migrated project metadata, dependency locking, development commands, and
  test/release workflows from Poetry to uv. Run tests with `uv run pytest`.
- GitHub Actions checks the handwritten library and public stubs with ty,
  tests Python 3.10, 3.11, 3.14, and 3.15, and keeps other matrix jobs running
  when one version fails.
- Transforms, injected constructors, package imports, notebooks, and static
  checking always use Pint's current application registry. Removed registry
  override arguments from the transform, package-hook, and checking APIs.
- The `unit-syntax` command now runs standalone scripts directly, enabling
  `uvx unit-syntax script.py` and passing subsequent arguments to the script.
- Replaced the `check` subcommand with `--check` for static dimensional checking.
  The console command and `python -m unit_syntax` use the same CLI.
- Updated standalone-script and checker examples in the README and removed
  the Python grammar version paragraph.

### Fixed

- Initialize Pint's lazy application registry before concurrent first use,
  so checks and execution cannot observe partially loaded unit definitions.

- Avoided applying UTF-8 column conversion twice to native string ASTs on
  Python 3.10 and 3.11, preserving Unicode and f-string source locations.

## 0.4.0

### Added

- Optional static dimensional checking with `unit-syntax check` and
  `python -m unit_syntax check`. Install it with `unit-syntax[check]`.
  The checker uses ty, checks project imports without executing user code,
  and reports diagnostics at original filenames, lines, and columns.
- Dimension-aware `Quantity[D]` annotations and named physical dimensions in
  `unit_syntax.typing`, generated arithmetic overloads, and a `py.typed` marker.
  Common dimensional products and quotients are normalized; other combinations
  retain symbolic dimensions and may be conservatively rejected.
- Static checks for incompatible arithmetic and unit conversions, dimensional
  function arguments, and numeric conversion of physical quantities. Only
  dimensionless quantities support implicit numeric conversion in the typing
  contract; angles and solid angles remain distinct dimensions. Runtime values
  remain ordinary Pint quantities.
- Grammar and dimensional-checking regression tests, a typed-units example,
  grammar provenance and regeneration instructions, and validation notes.
- CI coverage for Python 3.11, 3.14, and 3.15, including parser and typing-stub
  regeneration checks and distribution builds.

### Changed

- Updated the parser to target Python 3.15 syntax, including generic declarations,
  type parameter defaults, modern f-strings, template strings, unparenthesized
  exception lists, lazy imports, and unpacking comprehensions. Executing newer
  syntax requires an interpreter that supports it.
- Replaced `import-transforms` with a loader using Python's public `importlib`
  interfaces. Imported modules and standalone scripts compile the transformed
  AST directly, with unit-construction globals supplied by unit-syntax.
- Raised the minimum Python version from 3.8 to 3.10 and updated Pint, IPython,
  and pegen requirements, development dependencies, and the dependency lockfile.
- Updated release tooling to build and test with the optional checker enabled.

### Fixed

- Preserved CPython UTF-8 byte-column locations and the separate source spans
  of unit values, suffixes, and complete applications, including parentheses
  in nested conversions such as `(1 inch) mm`.
- Preserved original source locations when lowering unit expressions to calls.
- Prevented Unicode separators inside strings from introducing false source
  lines in parser locations or dimensional-checking diagnostics.
- Preserved template interpolation expression text across Python 3.14 and 3.15
  differences in trailing whitespace handling.

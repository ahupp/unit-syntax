# Grammar provenance and maintenance

`python_units.gram` targets Python 3.15. The ordinary Python grammar is based on
the Python-action grammar maintained by pegen, with CPython's 3.15 grammar as
the language reference:

- [pegen grammar at 813cf0879bc5e2dac8f7eca158c96aec3e481d59](https://github.com/we-like-parsers/pegen/blob/813cf0879bc5e2dac8f7eca158c96aec3e481d59/data/python.gram)
- [CPython 3.15 grammar at cdba68e56344377c33da8c7eddf1bf57dd8c5d60](https://github.com/python/cpython/blob/cdba68e56344377c33da8c7eddf1bf57dd8c5d60/Grammar/python.gram)

The pegen source does not have all of CPython's newer Python-action rules. The
local grammar adds type parameter defaults and template-string rules, using
the native interpreter to build string contents and interpolation metadata.
The grammar retains pegen's newer lazy imports, exception lists, and unpacking
comprehensions. New syntax is executable only on a host interpreter supporting
the corresponding AST and compiler features.

Unit syntax adds `UnitsExpr(value, units)` on simple expressions, compound-unit
rules, and the requirement to parenthesize unit expressions when mixing them
with other operators. The value, unit suffix, and complete application retain
separate source ranges. AST columns use CPython's UTF-8 byte convention.

Generate the checked-in parser with pegen 0.3:

```sh
python -m pegen python_units.gram -o unit_syntax/parser.py
```

Do not edit `parser.py` directly. `test/test_grammar.py` compares newer language
forms against the running CPython parser, compiles their ASTs, and exercises
unit syntax inside those forms. Run this suite on Python 3.15 as well as older
supported interpreters. The Python 3.15.2 validation also parsed and compiled
the standard-library `contextlib`, `functools`, `dataclasses`, `enum`, and
`importlib._bootstrap_external` modules.

The dimension annotations in `unit_syntax/typing.pyi` are generated separately:

```sh
python scripts/generate_typing.py
```

Edit the dimensional aliases in `unit_syntax/typing.py` and the operator rules
in that generator, then run the positive and negative ty integration tests.

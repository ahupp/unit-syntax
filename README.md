`unit-syntax` adds support for physical units to the Python language:

```python
>>> speed = 5 meters/second
>>> (2 seconds) * speed
10 meter
```

Why? I like to use Python as a calculator for physical problems and wished it had the type safety of explicit units along with the readability of normal notation.

`unit-syntax` works in Jupyter notebooks, standalone Python scripts, and Python packages.

[How does it work?](https://github.com/ahupp/unit-syntax#how-does-it-work)

## Getting Started

Install the package:

```shell
$ pip install unit-syntax
```

### ... with Jupyter/IPython

To enable unit-syntax in a Jupyter/IPython session run:

```python
%load_ext unit_syntax
```

Tip: In Jupyter this must be run in its own cell before any units expressions are evaluated.

### ... with standalone scripts

To run a standalone script with units:

```
$ python -m unit_syntax <path_to_script.py>
```

Note that this installs a custom import hook that affects all imports performed by the script.

### ... with Python packages

To use/distribute a package with unit-syntax, add this in your `__init__.py`:

```python
from unit_syntax.import_hook import enable_units_for_package
enable_units_for_package(__name__)
```

This applies the transform only to sub-modules of your package.

## Usage

[An interactive notebook to play around with units](https://colab.research.google.com/drive/1PInyLGZHnUzEuUVgMsLrUUNdCurXK7v1#scrollTo=JszzXmATY0TV)

Units can be applied to any "simple" expression:

- number: `1 meter`
- variables: `x parsec`, `y.z watts`, `area[id] meters**2`
- lists and tuples: `[1., 37.] newton meters`
- unary operators: `-x dBm`
- power: `x**2 meters`

In expressions mixing units and binary operators, parenthesize:

```python
one_lux = (1 lumen)/(1 meter**2)
```

Units can be used in any place where Python allows expressions, e.g:

- function arguments: `area_of_circle(radius=1 meter)`
- list comprehensions: `[x meters for x in range(10)]`

Quantities can be converted to another measurement system:

```python
>>> (88 miles / hour) furlongs / fortnight
236543.5269120001 furlong / fortnight
>>> (0 degC) degF
31.999999999999936 degree_Fahrenheit
```

Compound units (e.g. `newtons/meter**2`) are supported and follow the usual precedence rules.

Units _may not_ begin with parentheses (consider the possible
interpretations of `x (meters)`). Parentheses are allowed anywhere else:

```python
# parsed as a function call, will result in a runtime error
x (newton meters)/(second*kg)
# a-ok
x newton meters/(second*kg)
```

Using unknown units produces a syntax error at import time:

```python
>>> 1 smoot
...
SyntaxError: 'smoot' is not defined in the unit registry
```

## How does it work?

`unit-syntax` transforms python-with-units into standard python that calls the excellent [pint](https://pint.readthedocs.io/en/stable/) units handling library.

The parser is [pegen](https://we-like-parsers.github.io/pegen/), which is a standalone version of the same parser generator used by Python itself. The grammar is a [lightly modified](https://github.com/ahupp/unit-syntax/compare/base-grammar..main#diff-7405fdc26614e4d2e7f8f37c9b559ccb3a7f7c619d41e207dda28afdfae20f83) version the official Python grammar shipped with pegen.

Syntax transformation in IPython/Jupyter uses [IPython custom input transformers](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html).

Syntax transformation of arbitrary Python modules uses [importlib](https://docs.python.org/3/library/importlib.html)'s [MetaPathFinder](https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder), see [import-transforms](https://github.com/ahupp/import-transformss) and [unit_syntax.import_hook](https://github.com/ahupp/unit-syntax/blob/main/unit_syntax/import_hook.py) for details.

## Why only allow units on simple expressions?

Imagine units were instead parsed as operator with high precedence and you wrote this reasonable looking expression:

```python
ppi = 300 pixels/inch
y = x inches * ppi
```

`inches * ppi` would be parsed as the unit, leading to (at best) a runtime error sometime later and at worst an incorrect calculation. This could be avoided by parenthesizing the expression (e.g. `(x inches) * ppi`, but if that's optional it's easy to forget. So the intent of this restriction is to make these risky forms uncommon and thus more obvious. This is not a hypothetical concern, I hit this within 10 minutes of first using the initial syntax.

## Prior Art

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf) from Sun Microsystems. Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)

A [long discussion on the python-ideas mailing list](https://lwn.net/Articles/900739/) about literal units in Python.

## Development

To regenerate the parser:

`python -m pegen python_units.gram -o unit_syntax/parser.py`

Running tests:

```
$ poetry install --with dev
$ poetry run pytest
```

## Future work and open questions

- Test against various ipython and python versions
- Ensure bytecode caching still works
- Test with wider range of source files with the wildcard loader
- Unit type hints, maybe checked with [@runtime_checkable](https://docs.python.org/3/library/typing.html#typing.runtime_checkable). More Pint typechecking [discussion](https://github.com/hgrecco/pint/issues/1166)
- Typography of output
- pre-parse units
- talk to pint about interop between UnitRegistries

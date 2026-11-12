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

With [uv](https://docs.astral.sh/uv/), run a standalone script with units
without installing unit-syntax first:

```sh
$ uvx unit-syntax path_to_script.py
```

Arguments after the script filename are passed to the script.

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

Syntax transformation of arbitrary Python modules uses Python's public
`importlib` finder and loader interfaces; see `unit_syntax.import_hook`.

## Static dimension checking

Install the optional checker, then check a script or package before executing it:

```sh
pip install 'unit-syntax[check]'
unit-syntax --check model.py
unit-syntax --check my_package/
```

To fetch and run the optional checker with uv:

```sh
uvx --from 'unit-syntax[check]' unit-syntax --check model.py
```

The checker uses **ty**. It creates a temporary Python view of the source, gives
every unit literal its physical dimension, checks project imports, and maps
diagnostics back to the original filenames and positions. It never executes the
checked code or writes transformed code into the project. Running `ty check`
directly on a file containing unit suffixes will still produce syntax errors;
use `unit-syntax --check`. `--project PATH` explicitly selects the
root for imports. Syntax-only errors in unrelated, unselected files do not
prevent checking the selected files.

```python
from math import sqrt

width = 18 mm
height = 27 mm
ratio = width / height
ear = width * sqrt(1 - ratio * ratio)  # accepted: ratio is dimensionless

sqrt(width)                  # error: Quantity[Length] is not dimensionless
width + (2 seconds)          # error: Length and Time are incompatible
converted = (2 seconds) mm   # error: conversion requires compatible dimensions
```

Function annotations can express the same contract:

```python
from unit_syntax.typing import Quantity, Length, Area

def surface_area(radius: Quantity[Length]) -> Quantity[Area]:
    return radius * radius

surface_area(5 mm)       # accepted
surface_area(5 seconds)  # rejected by the checker
```

In `unit_syntax.typing`, `Quantity[D]` carries a **dimension**. This differs
from Pint's `pint.Quantity[T]`, whose type parameter describes the **magnitude**
(such as `float` or an array), not whether the value is a length or time. Pint's
existing annotations do not perform this dimensional checking. At runtime
`unit_syntax.typing.Quantity` is an alias for Pint's real `Quantity`; values,
registries, formatting, and arithmetic continue to use Pint.

Only `Quantity[Dimensionless]` supports `__float__` in the typing contract.
Pint already performs dimensionless numeric conversion at runtime, including
scale normalization: `float((1 m) / (1 mm))` is `1000`. Angles remain a distinct
static dimension, even though Pint treats radians as dimensionless. Convert an
angle to radians and explicitly extract its magnitude when calling Python's
plain numeric trigonometric functions.

The operator annotations normalize common dimensions, including area, volume,
velocity, acceleration, force, pressure, energy, power, and density. Matching
dimensions divide to a dimensionless quantity, including arbitrary compound
units written as literals. Other products and quotients retain symbolic
dimension types. Python typing cannot generally simplify arbitrary exponent
algebra, so an equivalent expression outside the normalized set can be
conservatively rejected. Physical powers currently require a supported literal
integer exponent (`-3` through `4`); dimensionless powers accept ordinary
numbers. Magnitude dtype and shape constraints, runtime-selected units,
arbitrary `.to()` strings, and Pint contexts remain runtime checks. Untyped
Python values retain the usual limits of gradual type checking.

The checker resolves literal unit names with its supplied registry (the Pint
application registry by default). Python API callers can pass their own registry
to `unit_syntax.check.checking_source`; checking does not execute package
initializers to discover custom registry definitions.

## Why only allow units on simple expressions?

Imagine units were instead parsed as operator with high precedence and you wrote this reasonable looking expression:

```python
ppi = 300 pixels/inch
y = x inches * ppi
```

`inches * ppi` would be parsed as the unit, leading to (at best) a runtime error sometime later and at worst an incorrect calculation. This could be avoided by parenthesizing the expression (e.g. `(x inches) * ppi`, but if that's optional it's easy to forget. So the intent of this restriction is to make these risky forms uncommon and thus more obvious. This is not a hypothetical concern, I hit this within 10 minutes of first using the initial syntax.

## Related Work

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf) from Sun Microsystems. Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)

A [long discussion on the python-ideas mailing list](https://lwn.net/Articles/900739/) about literal units in Python.

## Development

To regenerate the parser:

`python -m pegen python_units.gram -o unit_syntax/parser.py`

Running tests:

```
$ poetry install --with dev --extras check
$ poetry run pytest
$ poetry run python scripts/generate_typing.py
$ poetry run ty check unit_syntax/typing.pyi
```

## Future work and open questions

- Test against various ipython and python versions
- Ensure bytecode caching still works
- Test with wider range of source files with the wildcard loader
- Extend static normalization to more dimensional products and exponent expressions.
- Typography of output
- pre-parse units
- talk to pint about interop between UnitRegistries
- Fix reported location of SyntaxError when paren missing

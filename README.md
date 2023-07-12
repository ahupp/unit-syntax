`unit-syntax` extends the Python language in Jupyter/IPython to support expressions with physical units:

```python
>>> speed = 5 meters/second
>>> (2 seconds) * speed
10 meter
```

Behind the scenes this is translated into standard Python that uses the excellent [Pint](https://pint.readthedocs.io/) units library.

## Getting Started

Install the package:

```shell
$ pip install unit-syntax
```

To enable unit-syntax in a Jupyter/IPython session run:

```python
import unit_syntax
unit_syntax.enable_ipython()
```

Note: in Jupyter this must be run in its own cell before any units expressions are evaluated.

## Usage

[An interactive notebook to play around with units](https://colab.research.google.com/drive/1PInyLGZHnUzEuUVgMsLrUUNdCurXK7v1#scrollTo=JszzXmATY0TV)

Units apply to the immediately preceding value:

```python
1.21 gigawatts # literal number
(30 + 7) watts # parenthesized expression
[5, 7] meters # literal list
(9, 11) lumens # literal tuple
# variable reference
y becquerel
position.x attoparsec
velocity[player_id] meters/s
```

Units are parsed greedily and bind only to the immediately preceding value:

```python
x * 5 meters # x * (5 meters), not (x*5) meters
```

Quantities can be converted to another measurement system:

```python
>>> (88 miles / hour) furlongs / fortnight
236543.5269120001 furlong / fortnight
>>> (0 degC) degF
31.999999999999936 degree_Fahrenheit
```

It's _highly_ recommended to parenthesize any complex that include units. For example:

```python
1 meters * sin(degrees)
```

This is desugared to `Quantity(1, "meters * sin(degrees)")`, when you probably wanted `(1 meters) * sin(degrees)`.

Units _may not_ begin with parentheses (consider the possible
interpretations of `x (meters)`). Parentheses are allowed anywhere else:

```python
x (newton meters)/(second*kg) # parsed as a function call, will result in a runtime error
x newton meters/(second*kg) # ok
```

## Syntax Details

The full grammar for units is:

```
units:
    | units '/' units_group
    | units '*' units_group
    | units units_group
    | units '**' NUMBER
    | NAME

units_group:
    | '(' units ')'
    | units
```

Compound units allow the usual operators multiplication, division, and exponentiation with the usual precedence rules. Adjacent units without an operator are treated as multiplication.

## Help!

If you're getting an unexpected result, try using `unit_syntax.enable_ipython(debug_transform=True)`. This will log the transformed python code to the console.

## Why? How? Are you sure this a good idea?

I like using Python with [Jupyter Notebook](https://jupyter.org/) as a calculator for physical problems and often wish it had the clarity and type checking of explicit units. [Pint](https://pint.readthedocs.io/) is great, but its (necessary) verbosity makes it hard to see the underlying calculation that's going. Ultimately I want something that is as readable as what I'd write on paper using normal notation.

`unit-syntax` is an IPython [custom input transformer](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html) that rewrites expressions with units into calls to `pint.Quantity`. The parser is a lightly modified version of the Python grammar using the same parser generator ([pegen](https://github.com/we-like-parsers/pegen)) as Python itself.

Should you use this? There are tradeoffs. When using unit-syntax as an interactive calculator the clarity of explicit units improves both readability and correctness. However, the new syntax also introduces _new_ opportunities for error if an expression is parsed in an unexpected way. Usually this is obvious when used interactively, but it's something to be aware of.

`unit-syntax` cannot (currently) be used for standalone python scripts outside of IPython/Jupyter, but that's in principle possible through [meta_path import hooks](https://docs.python.org/3/reference/import.html#the-meta-path).

## Prior Art

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf) from Sun Microsystems. Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)

A [long discussion on the python-ideas mailing list](https://lwn.net/Articles/900739/) about literal units in Python.

## Development

To regenerate the parser:

`python -m pegen grammar.txt -o unit_syntax/parser.py`

Running tests:

```

$ poetry install --with dev
$ poetry run pytest

```

## Future work and open questions

- Test against various ipython and python versions
- Support standalone scripts through sys.meta_path
- Check units at parse time
- Unit type hints, maybe checked with [@runtime_checkable](https://docs.python.org/3/library/typing.html#typing.runtime_checkable). More Pint typechecking [discussion](https://github.com/hgrecco/pint/issues/1166)
- Expand the demo Colab notebook
- Typography of output
- Its too easy to get an unexpected parse if you forget parentheses.

```

```

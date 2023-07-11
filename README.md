`unit-syntax` extends the Python language in Jupyter/IPython to support expressions with physical units:

```python
>>> speed = 5 meters/second
>>> 2 seconds * speed
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

Units apply to the immediately preceding value (a literal, function call, variable reference, indexing, etc):

```python
1.21 gigawatts
[5., 7.] meters
position.x attoparsec
velocity[player_id] meters/s
```

Units have higher precedence than binary operators, and lower precedence than exponentiation and `await`:

```python
x = 5 meters/second
x * 7 seconds # x * (7 seconds) == 35 meters
2**4 meters # (2**4) meters == 16 meters
await foo() meters # (await foo()) meters
```

Units terms follow the usual mathmatical conventions:

```python
1 newton/meter**2 # pressure
1 newton meter # work
1 newton * meter # also work
```

Values can be converted to another measurement system:

```python
(88 miles / hour) furlongs / fortnight
(32 degF) degC
```

Pint transparently [supports Numpy](https://pint.readthedocs.io/en/stable/user/numpy.html) when available:

```python
velocity = [5, 7] meters/second
location = velocity * 2 seconds
distance_traveled = numpy.linalg.norm(location)
```

To fit with the existing python syntax, units _may not_ begin with
parentheses (consider the possible interpretations of `x (meters)`).
Parentheses are allowed anywhere else:

```python
x (newton meters)/second # invalid, parsed as a function call
x newton meters/(second) # valid
```

## Should I use this?

There are tradeoffs. When using unit-syntax as an interactive calculator the clarity of explicit units improves both readability and correctness. However, the new syntax also introduces _new_ opportunities for error

Take care when creating complex expressions with units. For example:

```python
1 meters * sin(degrees)
```

This is desugared to `Quantity(1, "meters * sin(degrees)")`, when you probably intended `(1 meters) * sin(degrees)`.

Be particularly careful when using identifiers with the same name as units. For example:

```python
meters = 5
# ... 100 lines
y = x + meters # oops, did you mean `x meters` instead?
```

Keep expressions simple, and use parentheses to make the order of operations explicit.

## Why? How?

I like using Python with [Jupyter Notebook](https://jupyter.org/) as a calculator for physical problems and often wish it had the clarity and type checking of explicit units. [Pint](https://pint.readthedocs.io/) is great, but its (necessary) verbosity makes it hard to see the underlying calculation that's going.

`unit-syntax` is an IPython [custom input transformer](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html) that rewrites expressions with units into calls to `pint.Quantity`. The parser is a lightly modified version of the Python grammar using the same parser generator ([pegen](https://github.com/we-like-parsers/pegen)) as Python itself.

`unit-syntax` cannot (currently) be used for standalone python scripts outside of IPython/Jupyter, but that's in principle possible through [meta_path import hooks](https://docs.python.org/3/reference/import.html#the-meta-path).

## Prior Art

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf) from Sun Microsystems. Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)

## Alternative syntax

- No spaces: harder to read, and will not work with formatters

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

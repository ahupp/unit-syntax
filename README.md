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

Units can be written directly after number, list, and tuple literals:

```python
1.21 gigawatts
[5., 7.] meters
(88, 0) miles / hour
```

For non-literals, the `as` keyword is repurposed to mean "with units":

```python
some_list[5] as meters
some_function() as meters / second
(5 meters) as feet
```

Units have higher precedence than any other operator and only apply to the immediately preceding value (specifically: a literal, function call or variable reference):

```python
x * 1.21 gigawatts
x * y as gigawatts
x
```

This is equivalent to `x * (1.21 gigawatts)`, and desugars to something like `x * Quantity(1.21, "gigawatts")`. The high precedence means units apply to the literal not the whole expression.

Values can be converted to another measurement system:

```python
(88 miles / hour) furlongs / fortnight
(68 degF) degC
```

Pint transparently [supports Numpy](https://pint.readthedocs.io/en/stable/user/numpy.html) when available:

```python
velocity = [5, 7] meters/second**2
location = velocity * 2 seconds
distance_traveled = numpy.linalg.norm(location)
```

## Why? How?

I like using Python+[Jupyter Notebook](https://jupyter.org/) as a calculator for physical problems and often wish it had the clarity and type checking of explicit units. [Pint](https://pint.readthedocs.io/) is great, but its (necessary) verbosity makes it hard to see the underlying calculation that's going.

`unit-syntax` is an IPython [custom input transformer](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html) that rewrites expressions with units into calls to `pint.Quantity`. The parser is a lightly modified version of the Python grammar using the same parser generator ([pegen](https://github.com/we-like-parsers/pegen)) as Python itself.

`unit-syntax` cannot (currently) be used for standalone python scripts outside of IPython/Jupyter, but that's in principle possible through [meta_path import hooks](https://docs.python.org/3/reference/import.html#the-meta-path).

## Prior Art

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf) from Sun Microsystems. Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)

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
-

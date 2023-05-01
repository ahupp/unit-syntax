`unit-syntax` extends the Python language in Jupyter/IPython to support expressions with physical units:

```python
>>> import unit_syntax.ipython
>>> speed = 5 meters/second
>>> 2 seconds * speed
10 meter
```

Behind the scenes this is translated into standard Python that uses the excellent [Pint](https://pint.readthedocs.io/) units library.

## Getting Started

Install the package with `pip install unit_syntax`.  Tip: In Google Colab, you can run this directly in a cell by prefixing the command with `!`.

To enable unit-syntax in a Jupyter/IPython session run:

```python
import unit_syntax.ipython
```

Note that in Jupyter this must be run in its own cell before any units expressions are evaluated.

## Syntax

Units apply to the preceding value (literal, variable, function call or indexing), and have higher precedence than other operators:

```python
x * 1.21 gigawatts
```

This is equivalent to `x * (1.21 gigawatts)`, and desugars to something like `x * Quantity(1.21, "gigawatts")`.  The high precedence means units apply to the literal not the whole expression.

Values can be converted to another measurement system:

```python
(88 miles / hour) furlongs / fortnight
```

Pint transparently supports numpy when available:

```python
velocity = [5, 7] meters/second**2
location = velocity * 2 seconds
distance_traveled = numpy.linalg.norm(location)
```

Units must start with an identifier

```python
10 cm * sin(45 degrees)
```

This is a syntax error because `sin` is parsed as part of the units; to resolve add parentheses: `(10 cm) * sin(45 degrees)`


The units term follows this grammar:

```
units:
    | '(' units ')'
    | NAME '/' units
    | NAME '*' units
    | NAME units
    | NAME '**' NUMBER
    | NAME
```

The syntax takes advantage of the fact that that in python its illegal for a NAME to follow a "primary" (literal, function call etc), so there's no ambiguity.  

## Why?  How?

I like using Python+[Jupyter Notebook](https://jupyter.org/) as a calculator for physical problems and often wish it had the clarity and type checking of explicit units. [Pint](https://pint.readthedocs.io/) is great, but (IMO) its necessary verbosity makes it hard to see the underlying calculation that's going.

`unit-syntax` is an IPython/Jupyter [custom input transformer](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html) that rewrites expressions with units into calls to `pint.Quantity`.

This is possible without ambiguity in the python grammar because it's otherwise invalid for a "primary" (literal, function call etc) to be immediately followed by 

`unit-syntax` cannot (currently) be used for standalone python scripts outside of IPython/Jupyter, but that's in principle possible through [meta_path import hooks](https://docs.python.org/3/reference/import.html#the-meta-path).

## Prior Art

The immediate inspriration of `unit-syntax` is a language called [Fortress](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf
) from Sun Microsystems.  Fortress was intended as a modern Fortran, and had first-class support for units in both the syntax and type system.

F# (an OCaml derivative from Microsoft) also [has first class support for units](https://en.wikibooks.org/wiki/F_Sharp_Programming/Units_of_Measure).

The Julia package [Unitful.jl](http://painterqubits.github.io/Unitful.jl/stable/)



## Development

To regenerate the parser:

`python -m pegen grammar.txt -o unit_literals/parser.py`

Running tests:

```
 $ poetry install --with dev
 $ poetry run pytest
```

## Open questions and future work

 * Fortress uses an `in` operator to apply units to a non-literal value, e.g `x in meters`.  This has the advantage of being unambiguous regardless of parenthesization, so you could write `x (meter seconds)/parsec` without conflicting with a function call grammar rules.

 * Test against various ipython and python versions
 * Support standalone scripts through sys.meta_path
 * Check units at parse time
 * Unit type hints, maybe checked with [@runtime_checkable](https://docs.python.org/3/library/typing.html#typing.runtime_checkable).  More Pint typechecking [discussion](https://github.com/hgrecco/pint/issues/1166)
   ```
   def speed(distance: Unit[meters], time: Unit[seconds]):
      ...
   ```
 * Pint does not do the right thing when applied to generator expressions, e.g `(a for a in range(0, 4)) meters`
 * `from unit_syntax import ipython`
 * Demo colab notebook: https://colab.research.google.com/drive/1PInyLGZHnUzEuUVgMsLrUUNdCurXK7v1#scrollTo=JszzXmATY0TV
 * Ensure it doesn't forcibly update ipython



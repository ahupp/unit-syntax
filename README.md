

`unit-syntax` extends the Python language in Jupyter/IPython to support expressions with physical units:

```
>>> speed = 5 meters/second
>>> 2 seconds * speed
10 meter
```

Units apply to the immediatly preceding "primary" term: a literal, variable, function call, or indexing operation.  Put another way, they have maximum precedence: `a * 5 meters` is evaluated to `a * (5 meters)`.  

The units term must start with an identifier and follows this grammar:

```
units:
    | '(' units ')'
    | NAME '/' units
    | NAME '*' units
    | NAME '**' NUMBER
    | NAME

```

Some examples to illustrate:


```
x * 5 meters
```

This is equivalent to `x * (5 meters)`, and desugars to `x * Quantity(5, "meters")`.  The high precedence means units apply to the literal not the whole expression.

`(88 miles / hours) furlongs / fortnight`

This creates a value of 88 miles per hour and then converts it to furlongs per fortnight (30064.3.., specifically).


```
velocity = [5, 7] meters/second**2
location = velocity * 2 seconds

from numpy.linalg import norm
distance = norm(location)
```

Pint transparently supports numpy, so a list of values becomes a `numpy.array`.

## Why?  How?

I like using Python+[Jupyter Notebook](https://jupyter.org/) as a calculator for physical problems and often wish it had the clarity and type checking of explicit units. [Pint](https://pint.readthedocs.io/) is nice library for manipulating physical quantifies, but (IMO) its necessarily verbosity makes it hard to see the underlying calculation that's going on.

`unit-syntax` is an IPython/Jupyter [custom input transformer](https://ipython.readthedocs.io/en/stable/config/inputtransforms.html) that rewrites expressions with units into calls to `pint.Quantity`.  All the logic for unit handling is handled by `pint`; this module is purely concerned with syntax.

`unit-syntax` cannot (currently) be used for standalone python scripts outside of IPython/Jupyter, but that's in principle possible through [meta_path import hooks](https://docs.python.org/3/reference/import.html#the-meta-path).

## Prior art

Julia: http://painterqubits.github.io/Unitful.jl/stable/
F#: https://docs.microsoft.com/en-us/archive/blogs/andrewkennedy/


Fortress: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf


## Development

To regenerate the parser:

`python -m pegen grammar.txt -o unit_literals/parser.py`

Running tests:

```
 $ poetry install --with dev
 $ poetry run pytest
```

## TODO

 * Test against various ipython and python versions
 * Support standalone scripts through sys.meta_path
 * Check units at parse time
 * Unit type hints, maybe checked with [@runtime_checkable](https://docs.python.org/3/library/typing.html#typing.runtime_checkable).  
   ```
   def speed(distance: Unit[meters], time: Unit[seconds]):
      ...
   ```

    

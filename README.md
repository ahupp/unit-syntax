

`unit-syntax` extends the Python language in Jupyter/IPython to support expressions with physical units:

  >>> speed = 5 m/s
  >>> distance = 20s * speed

## Why?

I often use python+jupyter as a calculator, and miss clarity and type checking of having

## Prior art

Julia: http://painterqubits.github.io/Unitful.jl/stable/
F#: https://docs.microsoft.com/en-us/archive/blogs/andrewkennedy/

https://github.com/trzemecki/Unum

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

# unit-literals

This package extends the python language to support literals with physical units:

  >>> speed = 5 m/s
  >>> distance = 20s * speed

## Wait, what?

This module is syntactic sugar to convert

This module works by adding an IPython input hook, tokenizing the input, and
transforming any numbers with units into a pint.Quantity.

## Prior art

Julia: http://painterqubits.github.io/Unitful.jl/stable/
F#: https://docs.microsoft.com/en-us/archive/blogs/andrewkennedy/

https://github.com/trzemecki/Unum

Fortress: https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.180.6323&rep=rep1&type=pdf

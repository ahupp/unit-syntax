# ipython-literals

Adds support for physical literals to an interactive IPython shell:

  >>> import ipyliterals
  >>> speed = 5 m/s
  >>> distance = 20s * speed

## Wait, what?

This module is syntactic sugar to convert

This module works by adding an IPython input hook, tokenizing the input, and
transforming any numbers with units into a pint.Quantity.
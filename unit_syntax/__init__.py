import pint


# Use the _DEFAULT_REGISTRY so we can interoperate with other pint-using libraries
ureg = pint._DEFAULT_REGISTRY


BOOTSTRAP = """
import unit_syntax
_unit_syntax_q = unit_syntax.ureg.Quantity
"""


from .ipython import load_ipython_extension, unload_ipython_extension

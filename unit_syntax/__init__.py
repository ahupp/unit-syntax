import pint


def _injected_q(ureg: pint.UnitRegistry | None):
    """Returns a dict that is injected into the module namespace, allowing the
    transformed units expressions to (indirectly) call into pint using the correct
    UnitRegistry"""
    if ureg is None:
        ureg = pint._DEFAULT_REGISTRY
    return {"_unit_syntax_q": ureg.Quantity}


from .ipython import load_ipython_extension, unload_ipython_extension
from .import_hook import enable_units_for_package

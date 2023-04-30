import pint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


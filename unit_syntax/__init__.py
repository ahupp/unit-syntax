import pint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


def enable_ipython():
    import IPython
    from .transform import transform_lines

    ip = IPython.get_ipython()
    if not hasattr(ip, "input_transformers_post"):
        raise ImportError("Unsupported IPython version, version >=7 is required")

    ip.input_transformers_post.append(transform_lines)
    
    # ensure the module is still visible if imported via 
    # `from unit_syntax import ipython` for some reason
    ip.run_cell("import unit_syntax")    

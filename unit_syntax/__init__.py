import pint

# Use the _DEFAULT_REGISTRY so we can interoperate with other pint-using libraries
ureg = pint._DEFAULT_REGISTRY

DEBUG = False


def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


def enable_ipython(debug=False):
    import IPython
    from .transform import transform_lines

    ip = IPython.get_ipython()
    if not hasattr(ip, "input_transformers_post"):
        raise ImportError("Unsupported IPython version, version >=7 is required")

    if debug:
        import logging

        logging.basicConfig(level=logging.DEBUG, force=True)

        def transform_lines_dbg(lines):
            ret = transform_lines(lines)
            logging.debug("unit_syntax: %s -> %s", lines, ret)
            return ret

        do_transform = transform_lines_dbg
    else:
        do_transform = transform_lines
    ip.input_transformers_post.append(do_transform)

    # ensure the module is still visible if imported via
    # `from unit_syntax import ipython` for some reason
    ip.run_cell("import unit_syntax")

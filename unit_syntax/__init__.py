import pint

# Use the _DEFAULT_REGISTRY so we can interoperate with other pint-using libraries
ureg = pint._DEFAULT_REGISTRY


def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


def _format_quantity_markdown(q):
    return q.to_reduced_units()._repr_markdown_()


def _format_quantity_html(q):
    return q.to_reduced_units()._repr_html_()


def _format_quantity_pretty(q, p, cycle):
    return q.to_reduced_units()._repr_pretty_(p, cycle)


def _format_quantity_latex(q):
    return q.to_reduced_units()._repr_latex_()


def enable_ipython(debug_transform=False):
    """
    debug_transform -- if True, log the input and output of each transform
    """
    import IPython
    from .transform import transform_lines

    ip = IPython.get_ipython()
    if not hasattr(ip, "input_transformers_post"):
        raise ImportError("Unsupported IPython version, version >=7 is required")

    if debug_transform:
        import logging

        logging.basicConfig(level=logging.DEBUG, force=True)

        def transform_lines_dbg(lines):
            ret = transform_lines(lines)
            logging.debug("unit_syntax: %s -> %s", "\n".join(lines), "\n".join(ret))
            return ret

        do_transform = transform_lines_dbg
    else:
        do_transform = transform_lines
    ip.input_transformers_post.append(do_transform)

    # Overide default formatters to use reduced units.  This lets us keep using the
    # default registry for interop with other pint-using libraries, but gives more
    # sensible output in the notebook.
    def add_formatter(mime, fn):
        formatter = ip.display_formatter.formatters[mime]
        formatter.for_type(pint.Quantity, fn)

    add_formatter("text/markdown", _format_quantity_markdown)
    add_formatter("text/html", _format_quantity_html)
    add_formatter("text/plain", _format_quantity_pretty)
    add_formatter("text/latex", _format_quantity_latex)

    # ensure the module is still visible if imported via
    # `from unit_syntax import ipython` for some reason
    ip.run_cell("import unit_syntax")

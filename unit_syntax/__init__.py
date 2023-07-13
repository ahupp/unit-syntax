import pint

# Use the _DEFAULT_REGISTRY so we can interoperate with other pint-using libraries
ureg = pint._DEFAULT_REGISTRY


def Quantity(value, units):
    if isinstance(value, ureg.Quantity):
        return value.to(units)
    else:
        return ureg.Quantity(value, units)


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
    def add_formatter(mime, display_fn_name):
        formatter = ip.display_formatter.formatters.get(mime)
        if formatter is None:
            return

        fn = getattr(pint.Quantity, display_fn_name, None)
        if fn is None:
            return

        def fmt_reduced(q, *args):
            return fn(q.to_reduced_units(), *args)

        formatter.for_type(pint.Quantity, fmt_reduced)

    add_formatter("text/markdown", "_repr_markdown_")
    add_formatter("text/html", "_repr_html_")
    add_formatter("text/plain", "_repr_pretty_")
    add_formatter("text/latex", "_repr_latex_")

    # ensure the module is still visible if imported via
    # `from unit_syntax import ipython` for some reason
    ip.run_cell("import unit_syntax")

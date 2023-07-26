from .transform import transform_lines
import pint


def _add_formatters(ipython):
    # Overide default formatters to use reduced units.  This lets us keep using the
    # default registry for interop with other pint-using libraries, but gives more
    # sensible output in the notebook.
    def add_formatter(mime, display_fn_name):
        fn = getattr(pint.Quantity, display_fn_name, None)
        if fn is None:
            return

        def fmt_reduced(q, *args):
            return fn(q.to_reduced_units(), *args)

        formatter = ipython.display_formatter.formatters[mime]
        formatter.for_type(pint.Quantity, fmt_reduced)

    add_formatter("text/markdown", "_repr_markdown_")
    add_formatter("text/html", "_repr_html_")
    add_formatter("text/plain", "_repr_pretty_")
    add_formatter("text/latex", "_repr_latex_")


_has_init_log = False
_debug = False


def ipython_transform(lines):
    ret = transform_lines(lines)

    if _debug:
        import logging

        if not _has_init_log:
            logging.basicConfig(level=logging.DEBUG, force=True)
        logging.debug("unit_syntax: %s -> %s", "\n".join(lines), "\n".join(ret))
    return ret


def load_ipython_extension(ipython):
    if not hasattr(ipython, "input_transformers_post"):
        raise ImportError("Unsupported IPython version, version >=7 is required")

    ipython.input_transformers_post.append(ipython_transform)

    _add_formatters(ipython)

    # ensure the module is still visible if imported via
    # `from unit_syntax import ipython` for some reason
    ipython.run_cell("import unit_syntax")

    try:
        import matplotlib

        pint.setup_matplotlib(True)
    except ImportError:
        pass


def unload_ipython_extension(ipython):
    ipython.input_transformers_post.remove(ipython_transform)

import pint
import logging
from .transform import UnitSourceTransform


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


def enable_debug():
    logging.basicConfig(level=logging.DEBUG, force=True)


_UNIT_TRANSFORM = UnitSourceTransform(None)


def transform_lines(lines: list[str]) -> list[str]:
    """IPython transforms provide a list of strings in the current cell, but to parse correctly we
    need to parse them as a single string"""
    ret = _UNIT_TRANSFORM.transform_to_str("".join(lines)).splitlines(keepends=True)
    logging.debug("unit_syntax: %s -> %s", lines, ret)
    return ret


def load_ipython_extension(ipython):
    logging.debug("unit_syntax: loading extension")

    if not hasattr(ipython, "input_transformers_post"):
        raise ImportError("Unsupported IPython version, version >=7 is required")

    ipython.input_transformers_post.append(transform_lines)

    _add_formatters(ipython)

    ipython.push(_UNIT_TRANSFORM.injected_globals())


def unload_ipython_extension(ipython):
    logging.debug("unit_syntax: unload extension")
    ipython.input_transformers_post.remove(transform_lines)

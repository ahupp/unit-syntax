from .transform import transform_lines

def _hook_ipython():
    import IPython

    ip = IPython.get_ipython()
    if not hasattr(ip, "input_transformers_post"):
        raise ImportError("Unsupported IPython version")

    ip.input_transformers_post.append(transform_lines)
    # ensure the module is still visible if imported via 
    # `from unit_syntax import ipython` for some reason
    ip.run_cell("import unit_syntax")    

_hook_ipython()

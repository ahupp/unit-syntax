from . import transform_lines


def hook_ipython():
    import IPython

    ip = IPython.get_ipython()
    if hasattr(ip, "input_transformers_post"):
        ip.input_transformers_post.append(transform_lines)
    else:
        raise ImportError("Unsupported IPython version")


hook_ipython()

import pint

from . import _injected_q


def _enable(module_glob: str, ureg: pint.UnitRegistry | None, check_loaded: bool):
    from import_transforms import register_module_source_transform
    from .transform import transform_to_ast

    register_module_source_transform(
        module_glob,
        transform_to_ast,
        injected=_injected_q(ureg),
        check_loaded=check_loaded,
    )


def enable_units_for_package(package_name: str, ureg: pint.UnitRegistry | None = None):
    _enable(f"{package_name}.*", ureg, True)


def enable_units_everywhere():
    _enable("*", None, False)

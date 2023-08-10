import pint


def enable_units_for_package(package_name: str, ureg: pint.UnitRegistry | None = None):
    from import_transforms import register_package_source_transform
    from .transform import transform_to_ast

    if ureg is None:
        _q = pint._DEFAULT_REGISTRY.Quantity
    else:
        _q = ureg.Quantity

    register_package_source_transform(
        package_name, transform_to_ast, injected={"_unit_syntax_q": _q}
    )

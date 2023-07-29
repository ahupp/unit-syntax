def enable_units_for_package(package_name: str):
    from import_transforms import set_module_source_transform, SourceTransformLoader
    from .transform import transform_to_ast
    from . import BOOTSTRAP
    import ast

    def f(source: str) -> ast.AST:
        return transform_to_ast(BOOTSTRAP + source)

    set_module_source_transform(f"{package_name}.*", f)

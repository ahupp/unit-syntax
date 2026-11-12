"""Import unit-enabled source through Python's public loader protocol."""

import fnmatch
import importlib.abc
import sys

from .transform import UnitSourceTransform


class _UnitLoader(importlib.abc.Loader):
    def __init__(self, original, transform):
        self.original = original
        self.transform = transform

    def create_module(self, spec):
        return self.original.create_module(spec)

    def exec_module(self, module):
        source = self.original.get_source(module.__name__)
        filename = self.original.get_filename(module.__name__)
        code = compile(self.transform.transform(source), filename, "exec")
        module.__dict__.update(self.transform.injected_globals())
        exec(code, module.__dict__)

    def __getattr__(self, name):
        return getattr(self.original, name)


class _UnitFinder(importlib.abc.MetaPathFinder):
    def __init__(self):
        self.patterns = []
        self.transform = UnitSourceTransform()

    def find_spec(self, fullname, path=None, target=None):
        if not any(fnmatch.fnmatchcase(fullname, pattern) for pattern in self.patterns):
            return None
        for finder in sys.meta_path:
            if finder is self:
                continue
            spec = finder.find_spec(fullname, path, target)
            if spec is not None:
                if isinstance(spec.loader, importlib.abc.SourceLoader):
                    spec.loader = _UnitLoader(spec.loader, self.transform)
                return spec
        return None


_finder = _UnitFinder()


def _enable(module_glob, check_loaded):
    if check_loaded:
        loaded = [
            name for name in sys.modules if fnmatch.fnmatchcase(name, module_glob)
        ]
        if loaded:
            raise RuntimeError(
                f"Already loaded modules matching {module_glob}: {', '.join(loaded)}"
            )
    _finder.patterns.append(module_glob)
    if _finder not in sys.meta_path:
        sys.meta_path.insert(0, _finder)


def enable_units_for_package(package_name: str):
    _enable(f"{package_name}.*", True)


def enable_units_everywhere():
    _enable("*", False)

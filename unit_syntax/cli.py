"""Run or statically check unit-enabled Python from either command entry point."""

import argparse
from pathlib import Path
import sys

from .import_hook import enable_units_everywhere
from .transform import UnitSourceTransform


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="unit-syntax", description="Run a Python script with physical unit syntax."
    )
    parser.add_argument(
        "--check", action="store_true", help="Check dimensions without executing code"
    )
    parser.add_argument(
        "--project", type=Path, help="Project root for imports when using --check"
    )
    parser.add_argument("path", help="Script to run, or a file or directory to check")
    parser.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        help="Script arguments, or additional paths and options for --check",
    )
    args = parser.parse_args(argv)
    if args.check:
        from .check import check_paths

        checker = argparse.ArgumentParser(prog="unit-syntax --check")
        checker.add_argument("--project", type=Path, default=args.project)
        checker.add_argument("paths", nargs="+", type=Path)
        checked = checker.parse_intermixed_args([args.path, *args.arguments])
        code, output = check_paths(checked.paths, project=checked.project)
        print(output, end="")
        return code
    if args.project is not None:
        parser.error("--project requires --check")

    filename = args.path
    sys.argv = [filename, *args.arguments]
    sys.path.insert(0, str(Path(filename).resolve().parent))
    transform = UnitSourceTransform(None)
    enable_units_everywhere()
    namespace = {
        "__name__": "__main__",
        "__file__": filename,
        "__package__": None,
        **transform.injected_globals(),
    }
    source = Path(filename).read_text(encoding="utf-8")
    exec(compile(transform.transform(source), filename, "exec"), namespace)
    return 0

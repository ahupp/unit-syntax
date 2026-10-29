import sys
from .transform import UnitSourceTransform

if len(sys.argv) < 2:
    sys.exit("usage: python -m unit_syntax <script.py>")

if sys.argv[1] == "check":
    from .check import main

    sys.exit(main(sys.argv[1:]))

from pathlib import Path
from .import_hook import enable_units_everywhere

filename = sys.argv[1]
sys.argv = sys.argv[1:]
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

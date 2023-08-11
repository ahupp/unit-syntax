from .import_hook import enable_units_everywhere
from .transform import transform_to_ast
from . import _injected_q
import sys
import types

enable_units_everywhere()

if len(sys.argv) < 2:
    sys.exit("usage: python -m unit_syntax <script.py>")

filename = sys.argv[1]
# Make the passed-in script argv[0]
del sys.argv[1]

ast = transform_to_ast(open(filename).read())
code = compile(ast, filename, mode="exec")

mod = types.ModuleType("__main__")
d = mod.__dict__
d.update(_injected_q(None))
d["__file__"] = filename
exec(code, mod.__dict__, None)

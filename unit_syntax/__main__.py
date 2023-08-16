import sys
import import_transforms
from .transform import UnitSourceTransform

if len(sys.argv) < 2:
    sys.exit("usage: python -m unit_syntax <script.py>")

transform = UnitSourceTransform(None)
import_transforms.run_script(sys.argv[1], transform)

import unittest
from IPython.testing.globalipapp import get_ipython

class Test(unittest.TestCase):
    def test_transforms(self):
        ip = get_ipython()
        ip.run_cell("import unit_literals.autohook")
        res = ip.run_cell("""
d = 1 lightyear
t = 1 fortnight
speed = d / t

how_far = speed * 1 millisecond

print(how_far.to_compact())
print(how_far.to_base_units())
print(how_far.ito_base_units())
how_far
""")
        print(res)
unittest.main()

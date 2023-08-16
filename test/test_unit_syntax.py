import os.path
import sys
from io import StringIO
from unit_syntax.transform import UnitSourceTransform
import pytest
import numpy
import pint
import tokenize

TEST_DIR = os.path.dirname(__file__)

## For testing various kinds of operations


class AttrTest:
    def __init__(self):
        self.second = 7


test_attr = AttrTest()
test_dict = {"value": 37}
second = 1024


def do_mult(left, right):
    return left * right


def id(v):
    return v


class UnitSourceTransformTester:
    def __init__(self, ust: UnitSourceTransform):
        self.ust = ust

    def transform_eval(self, code):
        code_assign = "result = " + code
        return self.transform_exec(code_assign)

    def transform_exec(self, code):
        glo = dict(globals())
        glo.update(self.ust.injected_globals())
        exec(self.ust.transform_to_str(code), glo)
        return glo["result"]

    def dbg_transform(self, code: str):
        from pprint import pprint

        tokens = list(tokenize.generate_tokens(StringIO(code).readline))
        pprint(tokens)
        # pprint(transform.parse(iter(tokens)))
        pprint(self.ust.transform_to_str(code))

    def assert_quantity_exec(self, code, value, units):
        try:
            result = self.transform_exec(code)
            assert_quantity_eq(result, value, units)
        except Exception as e:
            self.dbg_transform(code)
            raise e

    def assert_quantity(self, code, value, units):
        try:
            result = self.transform_eval(code)
            assert_quantity_eq(result, value, units)
        except Exception as e:
            self.dbg_transform(code)
            raise e

    def assert_syntax_error(self, code):
        with pytest.raises(SyntaxError):
            self.transform_exec(code)


def assert_quantity_eq(result, value, units):
    # Use the same registry as `result`, in case its different
    # from the default
    u = result._REGISTRY.Quantity(value, units)
    result = result.to(u.units)

    if type(result.magnitude) == numpy.ndarray:
        assert numpy.all(result.magnitude == value)
    else:
        assert result.magnitude == pytest.approx(value)
    assert result.units == u.units


def test_all():
    tst = UnitSourceTransformTester(UnitSourceTransform(None))

    tst.assert_quantity_exec(
        """
from math import *
def surface_area(radius):
    return 2*pi*(radius meters)**2

def total_surface_force(radius):
    return (101 kilopascal)*surface_area(radius)
result = total_surface_force(1.0)
""",
        634601.716025,
        "N",
    )

    tst.assert_quantity_exec(
        """
# this is a comment
result = 1 meters
""",
        1.0,
        "meters",
    )

    tst.assert_quantity("12 meter", 12, "meter")
    tst.assert_quantity("27.1 meter/s**2", 27.1, "meter/s**2")
    tst.assert_quantity("3 meter second/kg", 3, "(meter second)/kg")

    tst.assert_quantity("(2048 meter)/second * (2 second)", 4, "meter*second")
    tst.assert_quantity("do_mult(3 kg, 5 s)", 15, "kg*s")

    tst.assert_quantity("[2, 5] T", [2, 5], "T")
    tst.assert_quantity("(1., 3., 5.) attoparsec", (1.0, 3.0, 5.0), "attoparsec")

    tst.assert_quantity("(3 kg) pounds", 6.61386786, "pounds")

    tst.assert_quantity("test_attr.second degF", 7, "degF")
    tst.assert_quantity("test_dict['value'] ns", 37, "ns")

    tst.assert_quantity("(2**4) meters", 16, "meters")

    tst.assert_quantity("(2 meters) ** 2", 4, "meters**2")
    tst.assert_quantity("second * (1 meters)", 1024, "meters")
    tst.assert_quantity("-1 meters", -1, "meters")

    tst.assert_quantity("6.67 N m**2/kg**2", 6.67, "N*m**2/kg**2")

    list_comp = tst.transform_eval("[x meters for x in range(4)]")
    assert list_comp == [pint.Quantity(x, "meters") for x in range(4)]

    # Check valid units at parse time
    tst.assert_syntax_error("3 smoots")

    # Check mixing operators and units without parens is disallowed
    tst.assert_syntax_error("1 + 3 meters")


def test_loader():
    import test_pkg_standard_btu.mod_with_units

    assert_quantity_eq(
        test_pkg_standard_btu.mod_with_units.speed(), 1, "attoparsec/fortnight"
    )
    assert_quantity_eq(test_pkg_standard_btu.mod_with_units.btu(), 1055.056, "joule")

    # Check that a custom UnitRegistry is being used
    import test_pkg_intl_btu.mod_with_units

    assert_quantity_eq(test_pkg_intl_btu.mod_with_units.btu(), 1, "Btu_it")


def test_standalone_scripts():
    import subprocess

    filename = os.path.join(TEST_DIR, "./standalone_script.py")

    out = subprocess.check_output([sys.executable, "-m", "unit_syntax", filename])
    assert out == b"15 meter\n"

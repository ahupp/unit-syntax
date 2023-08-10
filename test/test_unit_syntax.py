from os import path
from io import StringIO
from unit_syntax import transform
import sys
import unit_syntax
import unit_syntax.ipython
import pytest
import numpy
import pint
import tokenize


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


##


def dbg_transform(code: str):
    from pprint import pprint

    tokens = list(tokenize.generate_tokens(StringIO(code).readline))
    pprint(tokens)
    # pprint(transform.parse(iter(tokens)))
    pprint(transform.transform_to_str(code))


def transform_exec(code):
    glo = dict(globals())
    glo["_unit_syntax_q"] = unit_syntax.ipython.Quantity
    exec(transform.transform_to_str(code), glo)
    return glo["result"]


def transform_eval(code):
    code_assign = "result = " + code
    return transform_exec(code_assign)


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


def assert_quantity_exec(code, value, units):
    try:
        result = transform_exec(code)
        assert_quantity_eq(result, value, units)
    except Exception as e:
        dbg_transform(code)
        raise e


def assert_quantity(code, value, units):
    try:
        result = transform_eval(code)
        assert_quantity_eq(result, value, units)
    except Exception as e:
        dbg_transform(code)
        raise e


def assert_syntax_error(code):
    with pytest.raises(SyntaxError):
        exec(transform.transform_to_str(code))


def test_all():
    assert_quantity_exec(
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

    assert_quantity_exec(
        """
# this is a comment
result = 1 meters
""",
        1.0,
        "meters",
    )

    assert_quantity("12 meter", 12, "meter")
    assert_quantity("27.1 meter/s**2", 27.1, "meter/s**2")
    assert_quantity("3 meter second/kg", 3, "(meter second)/kg")

    assert_quantity("(2048 meter)/second * (2 second)", 4, "meter*second")
    assert_quantity("do_mult(3 kg, 5 s)", 15, "kg*s")

    assert_quantity("[2, 5] T", [2, 5], "T")
    assert_quantity("(1., 3., 5.) attoparsec", (1.0, 3.0, 5.0), "attoparsec")

    assert_quantity("(3 kg) pounds", 6.61386786, "pounds")

    assert_quantity("test_attr.second degF", 7, "degF")
    assert_quantity("test_dict['value'] ns", 37, "ns")

    assert_quantity("(2**4) meters", 16, "meters")

    assert_quantity("(2 meters) ** 2", 4, "meters**2")
    assert_quantity("second * (1 meters)", 1024, "meters")
    assert_quantity("-1 meters", -1, "meters")

    assert_quantity("6.67 N m**2/kg**2", 6.67, "N*m**2/kg**2")

    list_comp = transform_eval("[x meters for x in range(4)]")
    assert list_comp == [pint.Quantity(x, "meters") for x in range(4)]

    # Check valid units at parse time
    assert_syntax_error("3 smoots")

    # Check mixing operators and units without parens is disallowed
    assert_syntax_error("1 + 3 meters")


def test_loader():
    sys.path.append(path.join(path.dirname(__file__), "test_pkg"))

    import test_pkg_standard_btu.mod_with_units

    assert_quantity_eq(
        test_pkg_standard_btu.mod_with_units.speed(), 1, "attoparsec/fortnight"
    )
    assert_quantity_eq(test_pkg_standard_btu.mod_with_units.btu(), 1055.056, "joule")

    # Check that a custom UnitRegistry is being used
    import test_pkg_intl_btu.mod_with_units

    assert_quantity_eq(test_pkg_intl_btu.mod_with_units.btu(), 1, "Btu_it")

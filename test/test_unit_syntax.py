from unit_syntax import transform
import unit_syntax
import pytest
import numpy
import pint


class AttrTest:
    def __init__(self):
        self.second = 7


test_attr = AttrTest()
test_dict = {"value": 37}
second = 1024
seven_furlong = unit_syntax.ureg.Quantity(7.0, "furlong")


def dbg_transform(code):
    from pprint import pprint

    tokens = list(transform.generate_tokens(code))
    pprint(tokens)
    pprint(transform.parse(iter(tokens)))
    pprint(transform.transform(code))


def do_mult(left, right):
    return left * right


def id(v):
    return v


def assert_quantity_exec(code, value, units):
    try:
        glo = dict(globals())
        exec(transform.transform(code), glo)
        result = glo["result"]

        u = unit_syntax.ureg.Quantity(value, units)
        result = result.to(u.units)

        if type(value) == float and type(result.magnitude) == float:
            assert result.magnitude == pytest.approx(value)
        elif type(result.magnitude) == numpy.ndarray:
            assert numpy.all(result.magnitude == value)
        else:
            assert result.magnitude == value
        assert result.units == u.units
    except Exception as e:
        dbg_transform(code)
        raise e


def assert_quantity(code, value, units):
    code_assign = "result = " + code
    assert_quantity_exec(code_assign, value, units)


def assert_syntax_error(code):
    with pytest.raises(SyntaxError):
        exec(transform.transform(code))


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

    assert_quantity("(2048 meter/second) * 2 second", 4096, "meters")
    assert_quantity("(2048 meter)/second * (2 second)", 4, "meter*second")
    assert_quantity("do_mult(3 kg, 5 s)", 15, "kg*s")

    assert_quantity("[2, 5] T", [2, 5], "T")
    assert_quantity("(1., 3., 5.) attoparsec", (1.0, 3.0, 5.0), "attoparsec")

    assert_quantity("(3 kg) pounds", 6.61386786, "pounds")

    assert_quantity("test_attr.second degF", 7, "degF")
    assert_quantity("test_dict['value'] ns", 37, "ns")

    assert_quantity("(2**4) meters", 16, "meters")
    with pytest.raises(pint.DimensionalityError):
        assert_quantity("2**4 meters", 16, "meters")

    assert_quantity("(2 meters) ** 2", 4, "meters**2")
    assert_quantity("second * 1 meters", 1024, "meters")
    assert_quantity("-1 meters", -1, "meters")

    assert_quantity("6.67 N m**2/kg**2", 6.67, "N*m**2/kg**2")
    assert_quantity("6.67 N m^2/kg^2", 6.67, "N*m**2/kg**2")


# TODO
# with pytest.raises(SyntaxError):
#     assert_quantity("3 smoots", 3, "smoots")

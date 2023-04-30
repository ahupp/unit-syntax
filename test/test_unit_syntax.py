from unit_syntax import transform
import unit_syntax
import pytest
import numpy
import pint


class AttrTest:
    def __init__(self):
        self.second = 7


attr_test = AttrTest()

dict_test = {"value": 37}

second = 1024


def dbg_transform(code):
    from pprint import pprint

    tokens = list(transform.generate_tokens(code))
    pprint(tokens)
    pprint(transform.parse(iter(tokens)))
    pprint(transform.transform(code))


def do_mult(left, right):
    return left * right


def assert_quantity(code, value, units):
    result = eval(transform.transform(code), globals())

    if type(value) == float and type(result.magnitude) == float:
        assert result.magnitude == pytest.approx(value)
    elif type(result.magnitude) == numpy.ndarray:
        assert numpy.all(result.magnitude == value)
    else:
        assert result.magnitude == value
    assert result.units == unit_syntax.ureg.Unit(units)


def test_all():

    assert_quantity("12 meter", 12, "meter")
    assert_quantity("13 meter/s**2", 13, "meter/s**2")
    assert_quantity("2048 meter/second * 2 second", 4096, "meters")
    assert_quantity("(2048 meter)/second * 2 second", 4, "meter*second")
    assert_quantity("do_mult(3 kg, 5 s)", 15, "kg*s")
    assert_quantity("(3 kg) pounds", 6.61386786, "pounds")
    assert_quantity("[2, 5] T", [2, 5], "T")
    assert_quantity("attr_test.second degF", 7, "degF")
    assert_quantity("dict_test['value'] ns", 37, "ns")
    with pytest.raises(pint.errors.DimensionalityError):
        assert_quantity("2**4 meters", 16, "meters")
    assert_quantity("second * 1 meters", 1024, "meters")

    # TODO
    # with pytest.raises(SyntaxError):
    #     assert_quantity("3 smoots", 3, "smoots")

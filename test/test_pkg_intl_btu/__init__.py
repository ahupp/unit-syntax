from unit_syntax import enable_units_for_package
import pint

ureg = pint.UnitRegistry()
ureg.load_definitions(
    """
BTU = Btu_it
""".splitlines()
)

enable_units_for_package(__name__, ureg=ureg)

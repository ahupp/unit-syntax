"""Dimension names for annotations; runtime quantities remain ordinary Pint values.

The companion stub provides dimensional operator signatures for static tools.
Pint's own Quantity[T] parameter describes magnitude, not physical dimension.
"""

from collections.abc import Mapping
from typing import Generic, Literal, TypeVar

import pint

K = TypeVar("K")
D = TypeVar("D")
E = TypeVar("E")


class Dimension(Generic[K]):
    """A canonical physical dimension, independent of its display units."""


class Product(Generic[D, E]):
    """An unreduced dimension product retained by the static type system."""


class Quotient(Generic[D, E]):
    """An unreduced dimension quotient retained by the static type system."""


class PowerOf(Generic[D, E]):
    """A dimension raised to a statically known integer power."""


DIMENSIONS = {
    "Dimensionless": {},
    "Length": {"[length]": 1},
    "Area": {"[length]": 2},
    "Volume": {"[length]": 3},
    "Time": {"[time]": 1},
    "Frequency": {"[time]": -1},
    "Mass": {"[mass]": 1},
    "Temperature": {"[temperature]": 1},
    "Current": {"[current]": 1},
    "Substance": {"[substance]": 1},
    "Luminosity": {"[luminosity]": 1},
    "Angle": {"[angle]": 1},
    "SolidAngle": {"[angle]": 2},
    "Velocity": {"[length]": 1, "[time]": -1},
    "Acceleration": {"[length]": 1, "[time]": -2},
    "Force": {"[length]": 1, "[mass]": 1, "[time]": -2},
    "Pressure": {"[length]": -1, "[mass]": 1, "[time]": -2},
    "Energy": {"[length]": 2, "[mass]": 1, "[time]": -2},
    "Power": {"[length]": 2, "[mass]": 1, "[time]": -3},
    "Density": {"[length]": -3, "[mass]": 1},
}


def dimension_key(dimensions: Mapping[str, float]) -> str:
    return (
        "|".join(
            f"{name}^{power:g}" for name, power in sorted(dimensions.items()) if power
        )
        or "1"
    )


for _name, _dimensions in DIMENSIONS.items():
    # The generated companion stub gives these dynamically created aliases
    # their statically known dimension keys.
    globals()[_name] = Dimension[
        Literal[dimension_key(_dimensions)]  # ty: ignore[invalid-type-form]
    ]

# This is deliberately an alias: unit-syntax does not introduce another
# quantity implementation or replace the user's Pint registry.
Quantity = pint.Quantity

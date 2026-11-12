"""Run with unit-syntax, or check with `unit-syntax --check` without execution."""
from math import sqrt
from unit_syntax.typing import Area, Length, Quantity


def surface_area(radius: Quantity[Length]) -> Quantity[Area]:
    return radius * radius


width = 18 mm
height = 27 mm
ratio = width / height
ear_radius = width * sqrt(1 - ratio * ratio)
area = surface_area(width)

# These are rejected before execution if uncommented:
# sqrt(width)
# width + (2 seconds)
# surface_area(2 seconds)
# (2 seconds) mm

print(ear_radius, area)

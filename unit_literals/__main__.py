from . import transform, parse
from pprint import pprint

if __name__ == "__main__":
  tests = [
    # "1",
    "1 meter",
    "1 meter/s**2",
    "1 meter",
    "1 meter/s^2",
    "1 meter/s * 1 second",
    "2**4 meters",
      """
if foo > 1:
  bar = 5 meters / s
     """,
      "x = (5 kg) pounds",
    # TODO
    "x meters",
  ]
  for i in tests:
    print(i)
    pprint(parse(i))
    pprint(transform(i))
    print()


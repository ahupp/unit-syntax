from .transform import transform_to_str
import sys

if len(sys.argv) < 2:
    input = sys.stdin
else:
    input = open(sys.argv[1], "r")

print(transform_to_str(input.read()))

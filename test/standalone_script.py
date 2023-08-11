import sys
import os.path
sys.path.append(os.path.dirname(__file__))

# Verify modules imported from this one do the transform
import standalone_script_mod


if __name__ == "__main__":
    dist = (3 seconds) * standalone_script_mod.speed()
    print(dist)
    result = dist


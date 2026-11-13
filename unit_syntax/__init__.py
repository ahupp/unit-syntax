import pint

# Initialize Pint's lazy default while package imports are serialized. Concurrent
# first use must not observe a registry whose definitions are still loading.
pint.get_application_registry().parse_units("")

from .ipython import load_ipython_extension, unload_ipython_extension
from .import_hook import enable_units_for_package

"""
PlanarDiagram is data Python package for knot theory.
See ... for complete documentation.
"""

__version__ = "0.0"

from knotpy import utils
from knotpy.utils import *

from knotpy import notation
from knotpy.notation import *

from knotpy import classes
from knotpy.classes import *

from knotpy import tables
from knotpy.tables import *

from knotpy import algorithms
from knotpy.algorithms import *

from knotpy import invariants
from knotpy.invariants import *

from knotpy import drawing
from knotpy.drawing import *

#from .algorithms import sanity
from knotpy.algorithms.sanity import *

from knotpy import reidemeister
from .reidemeister import *

from ._settings import settings


from knotpy.algorithms.sanity import sanity_check

from knotpy._settings import settings

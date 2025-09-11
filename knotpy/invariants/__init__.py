"""
List of possible invairants to implement:

Alexander Polynomial
Conway Polynomial
Jones Polynomial
HOMFLY-PT Polynomial
Kauffman 2-variable Polynomial (F polynomial)
Writhe
Linking Number
Seifert Genus (Upper Bound)
Turaev Genus (more advanced but diagrammatic)
Tricolorability
n-Colorability (mod n coloring)

"""


from .bracket import *
from .conway import *
from .jones import *
from .unplugging import*
from .affine_index import *
from .arrow import *
from .mock_alexander import *
from .yamada import *
from .homflypt import *
from .writhe import *
from .kauffman import *
from .alexander import *
from .classifier import *
from .fundamental_group import *
from .tutte import *
from ._symbols import SYMBOL_LOCALS

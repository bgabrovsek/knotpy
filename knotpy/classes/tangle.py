from functools import cached_property

from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.knotoid import Knotoid
from knotpy.classes.node import Crossing, Terminal # BivalentVertex,
from knotpy.classes.views import FilteredNodeView

__all__ = ['Knotoid']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class Tangle(Knotoid):

    def __init__(self, n=None, **attr):
        self._nodes = dict()
        super().__init__(**attr)


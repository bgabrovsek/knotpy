from functools import cached_property

import knotpy as kp
from knotpy.classes.knot import Knot
from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.node import Crossing, Bond #, BivalentVertex
from knotpy.classes.views import FilteredNodeView

__all__ = ['BondedKnot', "OrientedBondedKnot"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class BondedKnot(Knot):

    # init the descriptor instance, parameter keys are node types, values are cached propery names
    _nodes: dict = _NodeCachedPropertyResetter(Crossing="crossings",
                                               Bonds="bonds")

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    @staticmethod
    def is_oriented():
        return False


class OrientedBondedKnot(BondedKnot):

    # init the descriptor instance, parameter keys are node types, values are cached propery names
    _nodes: dict = _NodeCachedPropertyResetter(Crossing="crossings",
                                               Bonds="bonds")

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    @staticmethod
    def is_oriented():
        return True



if __name__ == "__main__":

    b = BondedKnot()
    print(b)
    pass
    #_tests()
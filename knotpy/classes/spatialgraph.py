from functools import cached_property

from knotpy.classes.planardiagram import _NodeCachedPropertyResetter
from knotpy.classes.planargraph import PlanarGraph
from knotpy.classes.knot import Knot

__all__ = ['SpatialGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


#class SpatialGraph(PlanarGraph, Knot):

class SpatialGraph(PlanarGraph, Knot):

    # init the descriptor instance, parameter keys are node types, values are cached property names
    _nodes: dict = _NodeCachedPropertyResetter(Vertex="vertices",
                                               Crossings="crossings",
                                               BivalentVertex="bivalent_vertices")

    # TODO: spatial graph should not have bivalent vertices, since these all normal vertices.

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)



if __name__ == "__main__":
    pass
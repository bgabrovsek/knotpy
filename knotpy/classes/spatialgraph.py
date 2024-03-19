from functools import cached_property

from knotpy.classes.planardiagram import _NodeCachedPropertyResetter
from knotpy.classes.planargraph import PlanarGraph, OrientedPlanarGraph
from knotpy.classes.knot import Knot, OrientedKnot
from knotpy.classes.node import Crossing, Vertex #BivalentVertex,
from knotpy.classes.views import FilteredNodeView

__all__ = ['SpatialGraph', "OrientedSpatialGraph"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class SpatialGraph(PlanarGraph, Knot):

    # init the descriptor instance, parameter keys are node types, values are cached property names
    _nodes: dict = _NodeCachedPropertyResetter(Vertex="vertices",
                                               Crossings="crossings",
                                               BivalentVertex="bivalent_vertices")

    @cached_property
    def vertices(self):
        """Node object holding the adjacencies of each node."""
        return FilteredNodeView(self._nodes, node_type=Vertex)

    # TODO: spatial graph should not have bivalent vertices, since these all normal vertices.

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    def is_oriented(self):
        return False

    @staticmethod
    def to_unoriented_class():
        return SpatialGraph

    @staticmethod
    def to_oriented_class():
        return OrientedSpatialGraph




class OrientedSpatialGraph(SpatialGraph):

    def is_oriented(self):
        return True


if __name__ == "__main__":
    pass
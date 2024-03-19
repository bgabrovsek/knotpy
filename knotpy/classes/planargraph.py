from functools import cached_property
from itertools import repeat

import knotpy as kp
from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.node import Vertex
from knotpy.classes.views import NodeView


__all__ = ['PlanarGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class PlanarGraph(PlanarDiagram):

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    # init the descriptor instance, parameter keys are node types, values are cached property names
    _nodes: dict = _NodeCachedPropertyResetter(Vertex="vertices")

    @cached_property
    def vertices(self):
        """Node object holding the adjacencies of each node."""
        return NodeView(self._nodes)

    def add_vertex(self, vertex_for_adding, degree=None, **attr):
        """Add or update a vertex. A vertex can be any hashable object."""
        self.add_node(node_for_adding=vertex_for_adding, create_using=Vertex, degree=degree, **attr)

    def add_vertices_from(self, vertices_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        self.add_nodes_from(nodes_for_adding=vertices_for_adding, create_using=Vertex, **attr)

    def is_oriented(self):
        return False

    @staticmethod
    def to_unoriented_class():
        return PlanarGraph

    @staticmethod
    def to_oriented_class():
        return OrientedPlanarGraph

    @property
    def number_of_vertices(self):
        return len(self._nodes)


class OrientedPlanarGraph(PlanarDiagram):

    @staticmethod
    def is_oriented():
        return True

    @staticmethod
    def to_unoriented_class():
        return PlanarGraph

    @staticmethod
    def to_oriented_class():
        raise OrientedPlanarGraph


if __name__ == "__main__":
    pass
    #_tests()
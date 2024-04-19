from functools import cached_property

import knotpy as kp
from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.node import Crossing
from knotpy.classes.views import FilteredNodeView
#from knotpy.algorithms.components import link_components_endpoints
#from knotpy.classes.orientedknot import OrientedKnot


__all__ = ['Knot', "OrientedKnot"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class Knot(PlanarDiagram):

    # init the descriptor instance, parameter keys are node types, values are cached property names
    _nodes: dict = _NodeCachedPropertyResetter(Crossing="crossings")

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    @cached_property
    def crossings(self):
        """Node object holding the adjacencies of each node."""
        return FilteredNodeView(self._nodes, node_type=Crossing)

    # @cached_property
    # def bivalent_vertices(self):
    #     """Node object holding the adjacencies of each node."""
    #     return FilteredNodeView(self._nodes, node_type=BivalentVertex)

    def add_crossing(self, crossing_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=crossing_for_adding, create_using=Crossing, degree=4, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        self.add_nodes_from(nodes_for_adding=crossings_for_adding, create_using=Crossing, **attr)

    # def add_bivalent_vertex(self, bivalent_vertex_for_adding, **attr):
    #     """Add or update a bivalent node  and update the node attributes. A node can be any hashable object."""
    #
    #     node = bivalent_vertex_for_adding
    #     if node is None:
    #         raise ValueError("None cannot be a bivalent node")
    #     if node not in self._nodes:  # TODO: check if bivalent node is a crossing
    #         self._nodes[node] = BivalentVertex()
    #     self._nodes[node].attr.update(attr)

    # def add_bivalent_vertices(self, bivalent_nodes_for_adding, **attr):
    #     """Add or update a bunch (iterable) of bivalent nodes and update the node attributes. Nodes can be any
    #     hashable objects."""
    #     for node in bivalent_nodes_for_adding:
    #         self.add_bivalent_vertex(node, **attr)



    @staticmethod
    def is_oriented():
        return False

    @staticmethod
    def to_unoriented_class():
        return Knot

    @staticmethod
    def to_oriented_class():
        return OrientedKnot

    @property
    def number_of_crossings(self):
        return len(self._nodes)


class OrientedKnot(Knot):
    @staticmethod
    def is_oriented():
        return True

def _tests():

    from knotpy.algorithms.faces import faces

    # construct a knot for testing
    k = Knot(name="My knot", color="blue")
    k.add_crossings_from("abc")
    k.set_arcs_from([(("a", 0), ("b", 1)), (("a", 1), ("b", 0)), (("a", 2), ("c", 1)),
                     (("a", 3), ("c", 0)), (("b", 2), ("c", 3)), (("b", 3), ("c", 2))])
    print(k)
    print(set(k.endpoints))
    print(set(k.arcs))
    print(list(faces(k)))

if __name__ == "__main__":
    pass
    #_tests()
from functools import cached_property

from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.node import Crossing, BivalentVertex
from knotpy.classes.views import FilteredNodeView
from knotpy.classes.endpoint import Endpoint

__all__ = ['Knot']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class Knot(PlanarDiagram):

    # init the descriptor instance, parameter keys are node types, values are cached propery names
    _nodes: dict = _NodeCachedPropertyResetter(Crossing="crossings", BivalentVertex="bivalent_vertices")

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    @cached_property
    def crossings(self):
        """Node object holding the adjacencies of each node."""
        return FilteredNodeView(self._nodes, node_type=Crossing)

    @cached_property
    def bivalent_vertices(self):
        """Node object holding the adjacencies of each node."""
        return FilteredNodeView(self._nodes, node_type=BivalentVertex)

    def add_crossing(self, crossing_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A Crossing can be any hashable objects."""
        crossing = crossing_for_adding

        if crossing is None:
            raise ValueError("None cannot be a crossing.")

        if crossing not in self._nodes:
            self._nodes[crossing] = Crossing()
        self._nodes[crossing_for_adding].attr.update(attr)

    def add_crossings(self, crossings_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        for crossing in crossings_for_adding:
            self.add_crossing(crossing, **attr)

    def is_oriented(self):
        return False

    def is_knotted(self):
        return True

    @property
    def number_of_crossings(self):
        return len(self._nodes)

def _tests():

    from knotpy.algorithms.region_algorithms import regions

    # construct a knot for testing
    k = Knot(name="My knot", color="blue")
    k.add_crossings("abc")
    k.set_arcs_from([(("a", 0), ("b", 1)), (("a", 1), ("b", 0)), (("a", 2), ("c", 1)),
                     (("a", 3), ("c", 0)), (("b", 2), ("c", 3)), (("b", 3), ("c", 2))])
    print(k)
    print(set(k.endpoints))
    print(set(k.arcs))
    print(list(regions(k)))

if __name__ == "__main__":
    pass
    #_tests()
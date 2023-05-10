
from functools import cached_property

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.old.views import FilteredAttributeView

__all__ = ['Knot']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _KnotCachedPropertyNodeAndCrossingAttributeResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node_attr"] = value
        if "nodes" in od: del od["nodes"]
        if "crossings" in od: del od["crossings"]


class Knot(PlanarDiagram):

    _node_attr = _KnotCachedPropertyNodeAndCrossingAttributeResetter()

    def __init__(self, incoming_knot_data=None, **attr):
        super().__init__(incoming_knot_data=None, **attr)

        if incoming_knot_data is not None:
            raise NotImplementedError()

    def add_crossing(self, crossing_for_adding, **attr):
        super()._add_node(node_for_adding=crossing_for_adding, degree=4, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        super()._add_nodes_from(self, nodes_for_adding=crossings_for_adding, **attr)

    def is_oriented(self):
        """Returns True if knot is directed, False otherwise."""
        return False

    def _canonically_rotate_node(self, node):
        """For a knot there are two choices for rotating a node/crossing (0 and 180 degrees rotation)."""

        if self._adj[node][2:] + self._adj[node][:2] < self._adj[node]:
            self._permute_node_positions(node, ccw_shift=2)

    @property
    def number_of_crossings(self):
        return len(self.crossings)

    @property
    def number_of_trivial_components(self):
        # TODO: this works only for knots
        return len(self.nodes) - len(self.crossings)

    @cached_property
    def crossings(self):
        """Knot crossing  object holding the attributes of each crossing."""
        return FilteredAttributeView(self._node_attr)


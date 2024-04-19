"""Base Node class for a node and its child classes (Crossing, Vertex, Terminal,...).
Node types:
Node: abstract node class
Vertex: contains a list of n incident endpoints
Crossing: contains a list of 4 incident endpoints, 0-th and 2-nd endpoints are arcs, 1-st and 3-rd are over arcs
Bivalent vertex: contains a list of 2 incident endpoints
Terminal: contains a list of 1 incident endpoint
Bond: contains a list of 4 incident endpoints, endpoints 0 and 1 (resp. 2 and 3) are on the same strand, the two strands
are connected through a tiny bond
"""


from abc import ABC, abstractmethod

from knotpy.utils.dict_utils import compare_dicts
from knotpy.utils.decorators import total_ordering_py3

"""
define what a node is and what data it consists of
"""

__all__ = ['Node']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'

@total_ordering_py3
class Node(ABC):
    """Abstract node class. Holds a list of incident endpoints and node attributes.
    Nodes can be crossings, vertices, etc."""

    attr: dict  # node's attributes (color, weight, ...)
    _inc: list  # list of adjacent endpoints

    def __init__(self, incoming_node_data=None, degree=None, **attr):
        incoming_node_data = incoming_node_data or []
        degree = degree or 0

        if len(incoming_node_data) > degree:
            raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")

        if len(incoming_node_data) < degree:
            incoming_node_data += [None] * (degree - len(incoming_node_data))

        self.attr = dict()
        self.attr.update(attr)
        self._inc = list(incoming_node_data)
        super().__init__()

    # "list" methods

    def __iter__(self):
        return self._inc.__iter__()

    def __getitem__(self, position):
        return self._inc[position]

    def __setitem__(self, position, endpoint):
        self._inc[position] = endpoint
        return self

    def __delitem__(self, position):
        del self._inc[position]

    def append(self, item):
        self._inc.append(item)

    def __len__(self):
        return len(self._inc)

    def py3_cmp(self, other, compare_attr=False):
        """Compare node. Replaces obsolete __cmp__ method.
        :param other: Node to compare with
        :param compare_attr: do we compare also the node attributes (name, color, ...)
        :return: 1 if self > other, -1 if self < other,0 otherwise.
        """

        def _compare(_x, _y):
            return 1 if (_x > _y) else (-1 if (_x < _y) else 0)

        if type(self).__name__ != type(other).__name__:
            return _compare(type(self).__name__, type(other).__name__)

        if len(self) != len(other):
            return ((len(self) < len(other)) << 1) - 1

        for a, b in zip(self, other):
            if a != b:
                return ((a < b) << 1) - 1

        if compare_attr:
            return compare_dicts(self.attr, other.attr)
        return 0

    def degree(self):
        return len(self)


    @abstractmethod
    def mirror(self):
        pass

    def __str__(self):
        """Used mostly for debugging. Actual node is usually printed via NodeView."""
        return "({})".format(
            " ".join(str(ep) if ep is not None else "?" for ep in self._inc)
        )






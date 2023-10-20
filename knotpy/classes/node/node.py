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

from knotpy.utils.decorators import total_order_py3
from knotpy.utils.combinatorics import cmp_dict

"""
define what a node is and what data it consists of
"""

__all__ = ['Node']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


@total_order_py3
class Node(ABC): #Node(ABC, list):
    """Abstract node class. Nodes can be crossings, vertices,..."""

    attr: dict
    _inc: list

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

    def append(self, item):
        self._inc.append(item)

    # def __iadd__(self, other):
    #     #print("iadd", self,"+",other)
    #     return self #._adj.__iadd__(other)

    def __len__(self):
        return len(self._inc)


    # def __eq__(self, other):
    #     return self.py3_cmp(other) == 0
    #
    # def __ne__(self, other):
    #     return self.py3_cmp(other) != 0
    #
    # def __lt__(self, other):
    #     return self.py3_cmp(other) < 0
    #
    # def __le__(self, other):
    #     return self.py3_cmp(other) <= 0
    #
    # def __gt__(self, other):
    #     return self.py3_cmp(other) > 0
    #
    # def __ge__(self, other):
    #     return self.py3_cmp(other) >= 0

    def py3_cmp(self, other, compare_attr=False):
        """Compare node. Replaces obsolete __cmp__ method.
        :param other: Node to compare with
        :param compare_attr: do we compare also the node attributes (name, color, ...)
        :return: 1 if self > other, -1 if self < other, and 0 otherwise.
        """

        if type(self).__name__ != type(other).__name__:
            return ((type(self).__name__ > type(other).__name__) << 1) - 1

        if len(self) != len(other):
            return ((len(self) < len(other)) << 1) - 1

        for a, b in zip(self, other):
            if a != b:
                return ((a < b) << 1) - 1

        if compare_attr:
            return cmp_dict(self.attr, other.attr)
        return 0

    def degree(self):
        return len(self)

    # def naive_permute(self, p):
    #     """Permute the endpoints of the node. For example, if p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,3,1]),
    #     endpoints 1, 2, 3 will be placed at positions 2, 3, 1, respectively. I.e. adjacent vert
    #     Warning: the permutation does not fix adjacent endpoints. For a clean permute, call permute_node from
    #     node_algorithms.
    #     :param p: dict, list or tuple.
    #     :return: None
    #     TODO: are there problems regarding endpoint attributes?
    #     """
    #     if isinstance(p, list) or isinstance(p, tuple):
    #         p = dict(enumerate(p))
    #
    #     inv_p = inverse_dict(p)
    #
    #     self._inc = [self._inc[p[i]] for i in p]


    # def flip(self, steps):
    #     """Flips the node from CW to CCW. Use with caution: the code can break the realizability of the knot."""
    #
    #     self.reverse()


    @abstractmethod
    def mirror(self):
        pass

    @staticmethod
    @abstractmethod
    def is_crossing(self):
        pass

    @staticmethod
    @abstractmethod
    def is_bivalent(self):
        pass

    def __str__(self):
        """Used mostly for debugging. Actual node is usually printed via NodeView."""
        return "({})".format(
            " ".join((str(e.node) + str(e.position)) if e is not None else "?" for e in self._inc)
        )








#
#
# class OrientedCrossing(Node):
#
#     def __init__(self, incoming_node_data=None, degree=None):
#         if len(incoming_node_data) > degree:
#             raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")
#         super().__init__(incoming_node_data)
#
#     def mirror(self):
#         return True
#
#     @staticmethod
#     def is_crossing(self):
#         return True
#
#     @staticmethod
#     def is_bivalent_vertex(self):
#         return False
#
#
#     def __str__(self):
#         return "O" + super().__str__()  # TODO: incorporate plus/minus
#
#

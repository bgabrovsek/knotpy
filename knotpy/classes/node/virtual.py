from knotpy.classes.node.node import Node

__all__ = ['VirtualCrossing']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class VirtualCrossing(Node):
    """A crossing is degree 4 node from knot theory that also holds information about over- and under-arcs. Arcs at
    positions 0 and 2 are connected over-arcs, arcs at positions 1 and 3 are connected under-arcs."""

    def __init__(self, incoming_node_data=None, degree=4, **attr):
        """
        :param incoming_node_data:
        :param degree:
        :param attr:
        """
        degree = degree or 4
        if degree != 4:
            raise ValueError("Cannot create a crossing with degree not equal to four.")
        super().__init__(incoming_node_data, degree=degree, **attr)

    def mirror(self):
        raise NotImplementedError()
        pass

    def __str__(self):
        return "V" + super().__str__()

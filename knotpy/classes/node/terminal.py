#from knotpy.classes.node.node import Node
from knotpy.classes.node.vertex import Vertex

_s_all__ = ['Terminal']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class Terminal(Vertex):
    """A terminal is a special degree 1 vertex of a knotoid endpoint."""

    def __init__(self, incoming_terminal_data=None, degree=1, **attr):
        degree = degree or 1
        if degree != 1:
            raise ValueError("Degree of a terminal must be 1")
        super().__init__(incoming_terminal_data, degree, **attr)

    def mirror(self):
        pass

    # @staticmethod
    # def is_crossing(self):
    #     return False

    # @staticmethod
    # def is_bivalent(self):
    #     return False

    def __str__(self):
        return "T" + super().__str__()
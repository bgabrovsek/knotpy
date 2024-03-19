from knotpy.classes.node import Node

__all__ = ['Vertex']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class Vertex(Node):
    """A graph 0-dimensional vertex is a point with arcs emitting from it.
    """

    def mirror(self):
        pass

    # @staticmethod
    # def is_crossing(self):
    #     return False

    # @staticmethod
    # def is_bivalent(self):
    #     return False

    def __str__(self):
        return "V" + super().__str__()

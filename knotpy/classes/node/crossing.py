from knotpy.classes.node.node import Node

__all__ = ['Crossing']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class Crossing(Node):
    def __init__(self, incoming_node_data=None, degree=4, **attr):
        degree = degree or 4
        if degree != 4:
            raise ValueError("Cannot create a crossing with degree not equal to four.")
        super().__init__(incoming_node_data, degree=degree, **attr)


    def mirror(self):
        pass

    @staticmethod
    def is_crossing(self):
        return True

    @staticmethod
    def is_bivalent(self):
        return False

    def __str__(self):
        return "X" + super().__str__()
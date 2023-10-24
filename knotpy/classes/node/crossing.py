from knotpy.classes.node.node import Node

__all__ = ['Crossing']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class Crossing(Node):
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
        pass

    @staticmethod
    def is_crossing(self):
        return True

    @staticmethod
    def is_bivalent(self):
        return False

    def jump_over(self, position):
        """Return the adjacent endpoint of (node, position) that is connected (is on the same strand or component) of
        the endpoint at the input position. For the position i, the jump is at position (i + 2) mod 4.
        :param position:
        :return: for a crossing-type node return adjacent position
        """
        return (position + 2) % 4

    def __str__(self):
        return "X" + super().__str__()

#
#
# class OrientedCrossing(Crossing):
#     def __init__(self, incoming_node_data=None, degree=4, sign=1, **attr):
#         """
#         :param incoming_node_data:
#         :param degree:
#         :param sign:
#         :param attr:
#         """
#         degree = degree or 4
#         if degree != 4:
#             raise ValueError("Cannot create a crossing with degree not equal to four.")
#         super().__init__(incoming_node_data, degree=degree, **attr)
#         self.sign = sign
#
#     def mirror(self):
#         raise NotImplementedError()
#
#
#
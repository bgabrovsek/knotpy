from knotpy.classes.knot import Knot

__all__ = ['OrientedKnot']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class OrientedKnot(Knot):

    def __init__(self, incoming_knot_data=None, **attr):
        super().__init__(incoming_knot_data=None, **attr)

    def _canonically_rotate_node(self, node):
        """For an oriented knot, there are no choices for rotating a node/crossing."""
        pass

    def is_oriented(self):
        return True

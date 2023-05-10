from knotpy.classes.old.xOldknot import Knot

class OrientedKnot(Knot):

    def __init__(self, incoming_knot_data=None, **attr):
        super().__init__(incoming_knot_data=None, **attr)

    def _canonically_rotate_node(self, node):
        """For an oriented knot, there are no choices for rotating a node/crossing."""
        pass

    def is_oriented(self):
        return True
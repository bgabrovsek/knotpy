from knotpy.classes.node.node import Node

__all__ = ['BivalentVertex']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'


class BivalentVertex(Node):
    def __init__(self, incoming_node_data=None, **attr):
        super().__init__(incoming_node_data, degree=2, **attr)

    def mirror(self):
        pass

    @staticmethod
    def is_crossing():
        return False

    @staticmethod
    def is_bivalent_vertex():
        return True

    def __str__(self):
        return (""
                "B") + super().__str__()

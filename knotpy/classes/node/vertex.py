from knotpy.classes.node import Node

__all__ = ['Vertex']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@gmail.si>'



class Vertex(Node):

    # def __init__(self, incoming_node_data=None, degree=None, **attr):
    #     degree = degree or 0
    #     #print("xx",incoming_node_data)
    #     if incoming_node_data is not None:
    #         raise NotImplementedError
    #     if degree is not None:
    #         raise NotImplementedError
    #     #if len(incoming_node_data) > degree:
    #     #    raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")
    #     super().__init__(incoming_node_data)

    def mirror(self):
        pass

    @staticmethod
    def is_crossing(self):
        return False

    @staticmethod
    def is_bivalent(self):
        return False

    def __str__(self):
        return "V" + super().__str__()

from abc import ABC, abstractmethod

__all__ = ['Node', 'Crossing', "BivalentVertex", 'node_dispatcher']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'



class Node(ABC, list):

    attr: dict

    def __init__(self, incoming_node_data=None, degree=None, **attr):
        incoming_node_data = incoming_node_data or []
        if len(incoming_node_data) > degree:
            raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")
        if len(incoming_node_data) < degree:
            incoming_node_data += [None] * (degree - len(incoming_node_data))
        self.attr = dict()
        self.attr.update(attr)
        super().__init__(incoming_node_data)

    @abstractmethod
    def mirror(self):
        pass

    def __str__(self):
        return "(" + " ".join(str(e.node) if e is not None else "?" for e in self) + ")"


class Vertex(ABC, list):

    def __init__(self, incoming_node_data=None, degree=None):
        if len(incoming_node_data) > degree:
            raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")
        super().__init__(incoming_node_data)

    def mirror(self):
        pass



class Crossing(Node):
    def __init__(self, incoming_node_data=None, **attr):
        super().__init__(incoming_node_data, degree=4, **attr)


    def mirror(self):
        pass


class BivalentVertex(Node):
    def __init__(self, incoming_node_data=None, **attr):
        super().__init__(incoming_node_data, degree=2, **attr)


    def mirror(self):
        pass


class OrientedCrossing(ABC, list):

    def __init__(self, incoming_node_data=None, degree=None):
        if len(incoming_node_data) > degree:
            raise ValueError(f"Cannot create node {incoming_node_data} that is larger than its degree ({degree})")
        super().__init__(incoming_node_data)


node_dispatcher = {"V": Vertex, "X": Crossing}

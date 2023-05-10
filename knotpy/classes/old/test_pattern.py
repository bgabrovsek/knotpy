from abc import ABC, abstractmethod


# decorator
def knotted_structure(*node_types):
    def wrapper(cls):
        setattr(cls, "_allowed_node_types", {node_type: node_type._class_holder_name() for node_type in node_types})
        setattr(cls, "_nodes", _NodeSync(getattr(cls, "_allowed_node_types")))
        def inner_wrapper(*args, **kwargs):
            result = cls(*args, **kwargs)
            return result
        return cls
    return wrapper

# nodes


class Node(ABC, list):

    def __init__(self, incoming_node_data):
        super().__init__(incoming_node_data)

    @staticmethod
    @abstractmethod
    def _class_holder_name():
        pass

    @staticmethod
    @abstractmethod
    def _class_viewer_name():
        pass


class Crossing(Node):
    @staticmethod
    def _class_holder_name():
        return "_crossings"

    @staticmethod
    def _class_viewer_name():
        return "crossings"

# Classes


class _NodeSync:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""
    def __set_name__(self, owner, name):
        print("setname", owner, name)

    def __init__(self, allowed_node_types):
        self._allowed_node_types = allowed_node_types

    def __set__(self, obj, value):
        #print("NODE", obj, value)
        od = obj.__dict__
        #print("_nodes" in od)
        #if isinstance(value, tuple):
        #    od["_nodes"][value[0]] = value[1]
        #else:
        od["_nodes"] = value
        if "nodes" in od: del od["nodes"]


    def update(self, arg):
        print("updating", arg, "...", self.__dict__)



class _CrossingSync:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""

    def __init__(self, node_type, _nodes):
        self._node_type = node_type
        self._class_holder_name = node_type._class_holder_name()
        self._class_viewer_name = node_type._class_viewer_name()
        self._nodes = _nodes

    def __set__(self, obj, value):
        od = obj.__dict__
        od[self._class_holder_name] = value
        if self._class_viewer_name in od: del od[self._class_viewer_name]
        #print("crossing set", obj, value)
        #obj._nodes[self._node_type] = value




@knotted_structure()
class PlanarBase(ABC):

    _allowed_node_types = dict()
    _nodes = _NodeSync(_allowed_node_types)

    def __init__(self):
        self._nodes = {node_type: dict() for node_type in self._allowed_node_types}


@knotted_structure(Crossing)
class Knot(PlanarBase):

    _crossings = _CrossingSync(Crossing, "_nodes")

    def __init__(self, **attr):
        super().__init__()
        self._crossings = dict()

    def add_crossing(self, crossing_for_adding, data):
        self._crossings[crossing_for_adding] = data

k = Knot()

print("Crossings:", k._nodes, "     Nodes:", k._crossings)

k.add_crossing("a", [1,2])

print("Crossings:", k._nodes, "     Nodes:", k._crossings)

k._crossings = {"b":[6]}

print("Crossings:", k._nodes, "     Nodes:", k._crossings)

k._nodes[Crossing] = {"c": [8]}

print("Crossings:", k._nodes, "     Nodes:", k._crossings)

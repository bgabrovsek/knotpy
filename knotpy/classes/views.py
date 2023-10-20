"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""
from collections.abc import Mapping, Set
from itertools import chain
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Node, Crossing

__all__ = [
    "NodeView", "EndpointView", "FilteredNodeView"
]


class NodeView(Mapping, Set):
    __slots__ = ("_nodes",)

    def __getstate__(self):
        return {"_nodes": self._nodes}

    def __setstate__(self, state):
        self._nodes = state["_nodes"]

    def __init__(self, nodes):
        self._nodes = nodes

    def arcs(self, node):
        # iterate over the arcs emanating from the node
        # TODO: can I return the iterator?
        return [(self._nodes[ep.node][ep.position], ep) for ep in self._nodes[node]]

    # Mapping methods
    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def __getitem__(self, key):

        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint):
            return self[key.node][key.position]

        return self._nodes[key]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint):
            self._nodes[key.node][key.position] = value  # should we check endpoint type? no this should be done by node

        else:
            self._nodes[key] = value


    # Set methods
    def __contains__(self, key):
        return key in self._nodes

    # Call methods
    def __call__(self, degree):
        """ Can  call k.nodes(degree=3) and it will return a list of nodes of degree degree.
        TODO: return a view or iterator"""
        return [node for node in self._nodes if len(self._nodes[node]) == degree]

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):

        return ", ".join(
            [
                u"{} \u2192 {}".format(v, str(u))
                for v, u in sorted(self._nodes.items())
            ]
        )


class FilteredNodeView(NodeView):
    __slots__ = ("_nodes", "_filter")

    def __init__(self, nodes, node_type):
        super().__init__(nodes)
        self._filter = lambda _: isinstance(self._nodes[_], node_type)

    # Mapping methods
    def __len__(self):
        return len([filter(self._filter, self._nodes)])  # slow

    def __iter__(self):
        return iter(filter(self._filter, self._nodes))

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint):
            return self[key.node][key.position]

        if key in self:
            return self._nodes[key]
        else:
            raise KeyError(f"{key}")

    def __bool__(self):
        # returns True if the filter contains at least one object, False otherwise
        return any(True for _ in self)

    # Set methods
    def __contains__(self, key):
        return key in self._nodes and self._filter(key)

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                u"{} \u2192 {}".format(node, self._nodes[node])
                for node in sorted(self)
            ]
        )


class EndpointView(NodeView):

    # Mapping methods
    def __len__(self):
        return sum(len(node) for node in self._nodes)

    def __iter__(self):
        return chain(*self._nodes.values())

    def __getitem__(self, key):
        """Return the endpoints that belong to the node key. Example: if key is 'a', the method returns
         [('a',0),('a',1),...] """
        if key in self._nodes:
            return [self._nodes[ep.node][ep.position] for ep in self._nodes[key]._inc]


        raise NotImplemented
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")
        return self._nodes[key]

    # Set methods
    def __contains__(self, key):
        raise NotImplemented
        return key in self._nodes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{v}" +
                u" \u2192 ({0})".format(" ".join([str(e[0] if e is not None else "?") for e in u]))
                for v, u in sorted(self._nodes.items())
            ]
        )


class ArcView(NodeView):

    # Mapping methods
    def __len__(self):
        return sum(len(node) for node in self._nodes) // 2

    def __iter__(self):
        # return map(lambda ep: (self._nodes[ep.node][ep.position], ep), chain(*self._nodes.values()))
        self._iter_endpoints = iter(chain(*self._nodes.values()))
        #print("ARC", list(iter(chain(*self._nodes.values()))))
        self._visited_endpoints = set()
        return self

    def __next__(self):
        while True:
            endpoint = next(self._iter_endpoints)  # can raise StopIteration
            adjacent_endpoint = self._nodes[endpoint.node][endpoint.position]
            self._visited_endpoints.add(adjacent_endpoint)
            if endpoint not in self._visited_endpoints:
                return adjacent_endpoint, endpoint

    def __getitem__(self, key):
        """
        If key is an Endpoints, it returns the arc that the endpoints belong to.
        If key is a node, if returns the list of arcs that emanate from the node.
        :param key: Endpoint instance or node
        :return: arc
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint):
            return self._nodes[key.node][key.position], key

        if isinstance(key, Node):
            raise NotImplementedError()



        if key in self._nodes:
            return [
                (self._nodes[ep.node][ep.position], ep)
                for ep in self._nodes[key]
                if ep.node != self._nodes[ep.node][ep.position].node
                   or ep.position > self._nodes[ep.node][ep.position].position
            ]
        raise ValueError(f"{key} is not a valid arc key.")

    # Set methods
    def __contains__(self, key):
        raise NotImplemented
        return key in self._nodes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{v}" +
                u" \u2192 ({0})".format(" ".join([str(e.node if e is not None else "?") for e in u]))
                for v, u in sorted(self._nodes.items())
            ]
        )

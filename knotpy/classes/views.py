"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""
from collections.abc import Mapping, Set
from itertools import chain
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node import Node, Crossing

__all__ = [
    "NodeView", "EndpointView", "FilteredNodeView", "FaceView", "ArcView"
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
        # TODO: convert to generator, not iterator
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


    def __call__(self, *attr_keys, **attr):
        return [node for node in self
                if all(k in self._nodes[node].attr for k in attr_keys)
                and all(k in self._nodes[node].attr and self._nodes[node].attr[k] == v for k, v in attr.items())]



    # Set methods
    def __contains__(self, key):
        return key in self._nodes

    # Call methods
    # def __call__(self, degree):
    #     """ Can  call k.nodes(degree=3) and it will return a list of nodes of degree degree.
    #     TODO: return a view or iterator"""
    #     return [node for node in self._nodes if len(self._nodes[node]) == degree]

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
        #print("init node view", node_type)
        super().__init__(nodes)
        self._filter = lambda _: isinstance(self._nodes[_], node_type)
        #print("filter", self._filter)

    # Mapping methods
    def __len__(self):
        return len(list(filter(self._filter, self._nodes)))  # slow

    def __iter__(self):
        # TODO: convert to generator, not iterator
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
        return sum(len(node_inst._inc) for node_inst in self._nodes.values())

    def __iter__(self):
        # TODO: convert to generator, not iterator
        return chain(*self._nodes.values())

    def __getitem__(self, key):
        """Return the endpoints that belong to the node key.
         Example: if key is 'a', the method returns.
        Guarantees that endpoints are given in ccw order
         [('a',0),('a',1),...]
        if node is endpoint, returns the endpoint (is the same as .get_endpoint_from_pair()
        :param key:
        :return:
        """
        if key in self._nodes:
            return [self._nodes[ep.node][ep.position] for ep in self._nodes[key]._inc]

        if isinstance(key, tuple):
            node, position = key
            twin = self._nodes[node][position]
            return self._nodes[twin.node][twin.position]  # return twin of twin


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
    """ Provides a view for arcs of a planar graph.

    The `ArcView` class is designed to provide an interface for accessing and manipulating arcs in a graph.
    It implements methods to traverse and inspect arcs, ensuring proper handling of graph structures.
    """

    # Mapping methods
    def __len__(self):
        """
        Return the number of arcs in the graph.

        Returns:
            int: The total number of edges present in the graph.
        """
        return sum(len(self._nodes[node]) for node in self._nodes) // 2

    def __iter__(self):
        """
        Returns an iterator object for iterating over arcs stored in the node structure.

        Each call to __iter__ will return a fresh iterator independent of others.
        """
        visited_endpoints = set()
        iter_endpoints = iter(chain(*self._nodes.values()))

        for endpoint in iter_endpoints:
            if endpoint not in visited_endpoints:
                adjacent_endpoint = self._nodes[endpoint.node][endpoint.position]
                visited_endpoints.add(adjacent_endpoint)
                yield frozenset((adjacent_endpoint, endpoint))

    # def __next__(self):
    #     """
    #     Returns the next unique arc (endpoint pair) encapsulated as a frozenset.
    #
    #     Raises:
    #         StopIteration: If the underlying iterator runs out of endpoints.
    #
    #     Returns:
    #         frozenset: A frozen set containing the arc (unique pair of endpoints),
    #         including the given endpoint and its adjacent endpoint.
    #     """
    #     while True:
    #         endpoint = next(self._iter_endpoints)  # Can raise StopIteration
    #         if endpoint not in self._visited_endpoints:
    #             adjacent_endpoint = self._nodes[endpoint.node][endpoint.position]
    #             self._visited_endpoints.add(adjacent_endpoint)  # We do not need to add endpoint, since it is already transversed
    #             #if endpoint not in self._visited_endpoints:
    #             return frozenset((adjacent_endpoint, endpoint))  # Reverse, since the iterator starts with adjacent endpoints

    def __getitem__(self, key):
        """If key is an Endpoints, it returns the arc that the endpoints belong to.
        If key is a node, if returns the list of arcs that emanate from the node. Guarantees that arcs are given in ccw
        order.
        :param key: Endpoint instance or node
        :return: arc
        """

        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint) or isinstance(key, tuple) and key and len(key) == 2 and key[0] in self._nodes:
            if isinstance(key, Endpoint):
                return frozenset((self._nodes[key.node][key.position], key))
            else:
                twin = self._nodes[key[0]][key[1]]
                twin_twin = self._nodes[twin.node][twin.position]
                return frozenset((twin, twin_twin))

        if isinstance(key, Node):
            # return arcs connected to node
            raise NotImplementedError()


        if key in self._nodes:
            return [
                frozenset((self._nodes[ep.node][ep.position], ep))
                for ep in self._nodes[key]
                if ep.node != self._nodes[ep.node][ep.position].node
                   or ep.position > self._nodes[ep.node][ep.position].position
            ]
        raise ValueError(f"{key} is not a valid arc key.")

    # Set methods
    def __contains__(self, arc):
        ep1, ep2 = arc
        adj1 = self._nodes[ep1.node][ep1.position]
        adj2 = self._nodes[ep2.node][ep2.position]
        return adj2 == ep1 and adj1 == ep2

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return ", ".join(
            [
                f"{v}" +
                u" \u2194 ({0})".format(" ".join([str(e.node if e is not None else "?") for e in u]))  # \u2192
                for v, u in sorted(self._nodes.items())
            ]
        )


class FaceView(NodeView):
    """
    Represents a view of the faces of a planar graph.

    A face (region, are) is a sequence of endpoints. Given a face on the plane, a face is given by the target (second)
    endpoint when travelling around the face in a CCW faction.

    Provides methods for iterating over, accessing, and representing the
    faces of the graph calculated based on the sphere's Euler characteristic.
    A `NodeView` serves as the underlying structure from which this class
    derives its functionality.

    """

    # Mapping methods
    def __len__(self):
        """Get the number of faces by the Euler characteristic of the sphere, V-E+F=2."""
        number_of_nodes = len(self._nodes)
        number_of_arcs = sum(len(self._nodes[node]) for node in self._nodes) // 2
        return 2 - number_of_nodes + number_of_arcs

    def __iter__(self):
        # TODO: convert to generator, not iterator
        # return map(lambda ep: (self._nodes[ep.node][ep.position], ep), chain(*self._nodes.values()))
        endpoints = set(chain(*self._nodes.values()))
        self._unused_endpoints = set(endpoints)
        #self._iter_endpoints = iter(chain(*self._nodes.values()))
        #print("ARC", list(iter(chain(*self._nodes.values()))))
        #self._visited_endpoints = set()
        return self

    def __next__(self):
        if self._unused_endpoints:
            ep = self._unused_endpoints.pop()
            region = list()
            while True:
                region.append(ep)
                ep = self._nodes[ep.node][(ep.position - 1) % len(self._nodes[ep.node])]
                if ep in self._unused_endpoints:
                    self._unused_endpoints.remove(ep)
                else:
                    return tuple(region)
        raise StopIteration

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
            raise NotImplementedError()

        if isinstance(key, Node):
            raise NotImplementedError()

        raise NotImplementedError()

    # Set methods
    def __contains__(self, key):
        raise NotImplementedError()

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

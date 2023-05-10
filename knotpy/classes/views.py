"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""
from collections.abc import Mapping, Set
from itertools import chain

__all__ = [
    "NodeView",
    "EndpointView"
]


class NodeView(Mapping, Set):

    __slots__ = ("_nodes",)

    def __getstate__(self):
        return {"_nodes": self._nodes}

    def __setstate__(self, state):
        self._nodes = state["_nodes"]

    def __init__(self, nodes):
        self._nodes = nodes

    # Mapping methods
    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return iter(self._nodes)

    def __getitem__(self, key):
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")
        return self._nodes[key]

    # Set methods
    def __contains__(self, key):
        return key in self._nodes

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

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
        if key in self:
            return self._nodes[key]
        else:
            raise KeyError(f"{key}")

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
        return map(lambda ep: (self._nodes[ep.node][ep.position], ep), chain(*self._nodes.values()))

    def __getitem__(self, key):
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

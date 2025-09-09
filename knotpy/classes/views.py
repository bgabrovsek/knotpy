from __future__ import annotations

"""Read-only views over a planar diagram.

These views are iterable containers backed by the diagram’s internal state.
As with dicts, the diagram should not be structurally modified while iterating.
"""

from collections.abc import Iterable, Iterator, Mapping, Set
from itertools import chain
from typing import Any, FrozenSet, Hashable

from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node import Node, Crossing

__all__ = ["NodeView", "EndpointView", "FilteredNodeView", "FaceView", "ArcView"]


class NodeView(Mapping, Set):
    """Mapping/set-like view over the diagram’s nodes.

    Keys are node identifiers (hashable), values are :class:`Node` instances.

    Note:
        This is a *view*: it reflects the underlying diagram. Avoid mutating
        the diagram while iterating this view.

    Attributes:
        _nodes (dict[Hashable, Node]): Backing node mapping.
    """

    __slots__ = ("_nodes",)

    # Pickle support
    def __getstate__(self) -> dict[str, Any]:
        """Return state for pickling.

        Returns:
            dict: Serializable state.
        """
        return {"_nodes": self._nodes}

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore state from pickling.

        Args:
            state: Serializable state created by :meth:`__getstate__`.
        """
        self._nodes = state["_nodes"]

    def __init__(self, nodes: dict[Hashable, Node]) -> None:
        """Create a view over the given node mapping.

        Args:
            nodes: Mapping from node id → :class:`Node` instance.
        """
        self._nodes = nodes

    def arcs(self, node: Hashable) -> list[tuple[Endpoint, Endpoint]]:
        """Return the arcs emanating from a node.

        Each arc is returned as a pair ``(adjacent_endpoint, endpoint)``.

        Args:
            node: Node identifier.

        Returns:
            list[tuple[Endpoint, Endpoint]]: List of arcs from the node.
        """
        # TODO: consider returning a generator for large diagrams.
        return [(self._nodes[ep.node][ep.position], ep) for ep in self._nodes[node]]

    # Mapping methods

    def __len__(self) -> int:
        """Return the number of nodes.

        Returns:
            int: Node count.
        """
        return len(self._nodes)

    def __iter__(self) -> Iterator[Hashable]:
        """Iterate over node identifiers.

        Returns:
            iterator: Iterator of node ids.
        """
        # TODO: consider returning a generator directly from self._nodes.
        return iter(self._nodes)

    def __getitem__(self, key: Any) -> Any:
        """Get a node, endpoint, or nth node depending on the key.

        Args:
            key: Node id, :class:`Endpoint`, or small integer index.

        Returns:
            Node | Endpoint | Hashable: Node instance for id; endpoint for Endpoint key;
            or the nth node id for an int key.

        Raises:
            ValueError: If slicing is attempted.
            KeyError: If a node id is not present.
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        # Node instance by id
        if key in self._nodes:
            return self._nodes[key]

        # Endpoint dereference
        if isinstance(key, Endpoint):
            return self._nodes[key.node][key.position]

        # nth node by iteration order
        if isinstance(key, int):
            return list(self._nodes.keys())[key]

        raise KeyError(f"{key}")

    def __setitem__(self, key: Any, value: Any) -> None:
        """Assign a node entry or endpoint slot.

        Args:
            key: Node id or :class:`Endpoint`.
            value: Node/Endpoint instance appropriate for the key.
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint):
            # Endpoint slot assignment (type validation is handled by node implementation)
            self._nodes[key.node][key.position] = value
        else:
            self._nodes[key] = value

    # Set methods

    def __contains__(self, key: object) -> bool:
        """Return whether a node id is present.

        Args:
            key: Potential node id.

        Returns:
            bool: ``True`` if present, else ``False``.
        """
        return key in self._nodes

    @classmethod
    def _from_iterable(cls, it: Iterable[Any]) -> set[Any]:
        """Construct a set from an iterable (for Set mixin compatibility).

        Args:
            it: Iterable of items.

        Returns:
            set: Materialized set.
        """
        return set(it)

    def __str__(self) -> str:
        """Return the string representation (delegates to :meth:`__repr__`)."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a readable mapping summary.

        Returns:
            str: Representation mapping node id → node.
        """
        return ", ".join([f"{v} \u2192 {u}" for v, u in sorted(self._nodes.items())])
        #return str([str(v) for v in sorted(self)])


class FilteredNodeView(NodeView):
    """Node view filtered by node type."""

    # TODO: __getitem__ on this view currently returns a node by id; if you expect
    #       crossing-specific behavior, consider overriding accordingly.

    __slots__ = ("_nodes", "_filter")

    def __init__(self, nodes: dict[Hashable, Node], node_type: type[Node]) -> None:
        """Create a filtered node view.

        Args:
            nodes: Node mapping to filter.
            node_type: Concrete node class to include (e.g., :class:`Crossing`).
        """
        super().__init__(nodes)
        self._filter = lambda _: isinstance(self._nodes[_], node_type)

    # Mapping methods

    def __len__(self) -> int:
        """Return the number of nodes matching the filter.

        Returns:
            int: Count of filtered nodes.
        """
        # Note: O(n) each time; acceptable for small n. Consider caching if needed.
        return len(list(filter(self._filter, self._nodes)))

    def __iter__(self) -> Iterator[Hashable]:
        """Iterate over filtered node identifiers.

        Returns:
            iterator: Iterator of matching node ids.
        """
        # TODO: return a generator rather than a materialized iterator if needed.
        return iter(filter(self._filter, self._nodes))

    def __bool__(self) -> bool:
        """Return whether there is at least one matching node.

        Returns:
            bool: ``True`` if any node passes the filter.
        """
        return any(True for _ in self)

    # Set methods

    def __contains__(self, key: object) -> bool:
        """Return whether a node id is present *and* passes the filter.

        Args:
            key: Potential node id.

        Returns:
            bool: ``True`` only if the node id exists and matches the filter.
        """
        return key in self._nodes and self._filter(key)  # type: ignore[arg-type]

    @classmethod
    def _from_iterable(cls, it: Iterable[Any]) -> set[Any]:
        """Construct a set from an iterable (for Set mixin compatibility).

        Args:
            it: Iterable of items.

        Returns:
            set: Materialized set.
        """
        return set(it)

    def __str__(self) -> str:
        """Return the string representation (delegates to :meth:`__repr__`)."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a readable mapping summary for filtered nodes.

        Returns:
            str: Representation mapping node id → node (for filtered subset).
        """
        return ", ".join([f"{node} \u2192 {self._nodes[node]}" for node in sorted(self)])


class EndpointView(NodeView):
    """View over all endpoints of the diagram."""

    # Mapping methods

    def __len__(self) -> int:
        """Return the number of endpoints.

        Returns:
            int: Endpoint count across all nodes.
        """
        return sum(len(node_inst._inc) for node_inst in self._nodes.values())

    def __iter__(self) -> Iterator[Endpoint]:
        """Iterate over all endpoints in CCW order within each node.

        Returns:
            iterator: Iterator of endpoints.
        """
        # TODO: return a generator if performance matters; fine for now.
        return chain(*self._nodes.values())

    def __getitem__(self, key: Any) -> Any:
        """Return endpoints for a node or resolve by pair.

        If ``key`` is a node id, returns that node’s endpoints in CCW order.
        If ``key`` is a pair ``(node, position)``, returns the *twin of the twin*
        (i.e., the canonical endpoint instance at that position).

        Args:
            key: Node id or pair ``(node, position)``.

        Returns:
            list[Endpoint] | Endpoint: Endpoints for a node, or the resolved endpoint.

        Raises:
            ValueError: If slicing is attempted.
            KeyError: If the node does not exist.
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if key in self._nodes:
            return [self._nodes[ep.node][ep.position] for ep in self._nodes[key]._inc]

        if isinstance(key, tuple):
            node, position = key
            twin = self._nodes[node][position]
            return self._nodes[twin.node][twin.position]  # twin of twin = canonical

        raise KeyError(f"{key}")

    # Set methods

    def __contains__(self, key: object) -> bool:
        """Return whether an endpoint (or pair) belongs to the diagram.

        Args:
            key: Endpoint instance or pair ``(node, position)``.

        Returns:
            bool: ``True`` if it resolves to an endpoint in the diagram.
        """
        try:
            if isinstance(key, Endpoint):
                node, pos = key.node, key.position
            elif isinstance(key, tuple) and len(key) == 2:
                node, pos = key
            else:
                return False
            return node in self._nodes and 0 <= pos < len(self._nodes[node])
        except Exception:
            return False

    def __str__(self) -> str:
        """Return the string representation (delegates to :meth:`__repr__`)."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a readable summary of endpoints per node.

        Returns:
            str: Node → list of endpoints.
        """
        return ", ".join(
            [
                f"{v} \u2192 ({' '.join(str(e[0] if e is not None else '?') for e in u)})"
                for v, u in sorted(self._nodes.items())
            ]
        )


class ArcView(NodeView):
    """View over arcs (pairs of endpoints)."""

    # Mapping methods

    def __len__(self) -> int:
        """Return the number of arcs.

        Returns:
            int: Half the number of endpoints across all nodes.
        """
        return sum(len(self._nodes[node]) for node in self._nodes) // 2

    def __iter__(self) -> Iterator[FrozenSet[Endpoint]]:
        """Iterate over unique arcs.

        Yields:
            frozenset[Endpoint]: Unique arc as an unordered pair of endpoints.
        """
        visited_endpoints: set[Endpoint] = set()
        iter_endpoints = iter(chain(*self._nodes.values()))
        for endpoint in iter_endpoints:
            if endpoint not in visited_endpoints:
                adjacent_endpoint = self._nodes[endpoint.node][endpoint.position]
                visited_endpoints.add(adjacent_endpoint)
                yield frozenset((adjacent_endpoint, endpoint))

    def __getitem__(self, key: Any) -> FrozenSet[Endpoint] | list[FrozenSet[Endpoint]]:
        """Return an arc for an endpoint/pair, or a list of arcs for a node.

        Args:
            key: :class:`Endpoint`, pair ``(node, position)``, or node id.

        Returns:
            frozenset[Endpoint] | list[frozenset[Endpoint]]: The arc or arcs.

        Raises:
            ValueError: If slicing is attempted or key is invalid.
            NotImplementedError: If Node-type key access is not yet implemented.
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")

        if isinstance(key, Endpoint) or (isinstance(key, tuple) and len(key) == 2 and key and key[0] in self._nodes):
            if isinstance(key, Endpoint):
                return frozenset((self._nodes[key.node][key.position], key))
            twin = self._nodes[key[0]][key[1]]
            twin_twin = self._nodes[twin.node][twin.position]
            return frozenset((twin, twin_twin))

        if isinstance(key, Node):
            # Return arcs connected to a Node instance (not just an id)
            raise NotImplementedError()

        if key in self._nodes:
            # Arcs emanating from a node id; unique by ordering rule
            return [
                frozenset((self._nodes[ep.node][ep.position], ep))
                for ep in self._nodes[key]
                if ep.node != self._nodes[ep.node][ep.position].node
                or ep.position > self._nodes[ep.node][ep.position].position
            ]

        raise ValueError(f"{key} is not a valid arc key.")

    # Set methods

    def __contains__(self, arc: object) -> bool:
        """Return whether an arc exists.

        Args:
            arc: Pair ``(ep1, ep2)`` of endpoints.

        Returns:
            bool: ``True`` if endpoints are mutual twins.
        """
        try:
            ep1, ep2 = arc  # type: ignore[misc]
            adj1 = self._nodes[ep1.node][ep1.position]
            adj2 = self._nodes[ep2.node][ep2.position]
            return adj2 == ep1 and adj1 == ep2
        except Exception:
            return False

    def __str__(self) -> str:
        """Return the string representation (delegates to :meth:`__repr__`)."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a readable summary of arcs per node.

        Returns:
            str: Node → arc endpoints.
        """
        return ", ".join(
            [
                f"{v} \u2194 ({' '.join(str(e.node if e is not None else '?') for e in u)})"
                for v, u in sorted(self._nodes.items())
            ]
        )


class FaceView(NodeView):
    """View over faces (regions) of a planar diagram.

    A face (region, area) is modeled as a sequence of endpoints. Given a face
    on the plane, its boundary is returned by traversing in CCW fashion, using
    the target (second) endpoint at each step.
    """

    # Mapping methods

    def __len__(self) -> int:
        """Return the number of faces via the Euler characteristic on the sphere.

        Returns:
            int: ``F = 2 - V + E`` where ``V`` is nodes and ``E`` is arcs.
        """
        number_of_nodes = len(self._nodes)
        number_of_arcs = sum(len(self._nodes[node]) for node in self._nodes) // 2
        return 2 - number_of_nodes + number_of_arcs

    def __iter__(self) -> Iterator[tuple[Endpoint, ...]]:
        """Return an iterator over faces as endpoint cycles.

        Returns:
            iterator: Iterator yielding tuples of endpoints along each face boundary.
        """
        # Collect all endpoints in a set to track unused ones
        endpoints = set(chain(*self._nodes.values()))
        self._unused_endpoints: set[Endpoint] = set(endpoints)
        return self

    def __next__(self) -> tuple[Endpoint, ...]:
        """Return the next face as a tuple of endpoints.

        Returns:
            tuple[Endpoint, ...]: One face boundary.

        Raises:
            StopIteration: When all faces are exhausted.
        """
        if self._unused_endpoints:
            ep = self._unused_endpoints.pop()
            region: list[Endpoint] = []
            while True:
                region.append(ep)
                ep = self._nodes[ep.node][(ep.position - 1) % len(self._nodes[ep.node])]
                if ep in self._unused_endpoints:
                    self._unused_endpoints.remove(ep)
                else:
                    return tuple(region)
        raise StopIteration

    def __getitem__(self, key: Any) -> Any:
        """Random access to face-related elements (not implemented yet).

        Args:
            key: Endpoint or node.

        Raises:
            NotImplementedError: Always (placeholder).
        """
        if isinstance(key, slice):
            raise ValueError(f"{type(self).__name__} does not support slicing.")
        raise NotImplementedError()

    # Set methods

    def __contains__(self, key: object) -> bool:
        """Return whether a face is present (not implemented).

        Raises:
            NotImplementedError: Always (placeholder).
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """Return the string representation (delegates to :meth:`__repr__`)."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a readable summary for faces per node.

        Returns:
            str: Node → endpoints on the boundary list.
        """
        return ", ".join(
            [
                f"{v} \u2192 ({' '.join(str(e.node if e is not None else '?') for e in u)})"
                for v, u in sorted(self._nodes.items())
            ]
        )


if __name__ == "__main__":
    pass

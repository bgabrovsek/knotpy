from __future__ import annotations

"""Base node type used by planar diagram structures.

Node kinds include:
- Node (abstract base)
- Vertex: list of n incident endpoints
- Crossing: list of 4 incident endpoints; positions 0 & 2 are under, 1 & 3 over
- Bivalent vertex: list of 2 incident endpoints
- Terminal: list of 1 incident endpoint
- Bond: list of 4 incident endpoints (0/1 share a strand; 2/3 share another)
"""

from abc import ABC
from typing import Any, Iterator, Sequence

from knotpy.utils.dict_utils import compare_dicts
from knotpy.utils.decorators import total_ordering_from_compare

__all__ = ["Node"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


# Optional type rank to keep ordering stable if needed elsewhere.
_node_name_sort_rank = {"Vertex": 0, "Crossing": 1, "VirtualCrossing": 2}


@total_ordering_from_compare
class Node(ABC):
    """Abstract node that holds incident endpoints and attributes.

    Endpoints are stored in CCW order in ``_inc``; individual subclasses
    (e.g., ``Crossing``, ``Vertex``) may impose constraints on length/meaning.

    Attributes:
        attr (dict[str, Any]): Node attributes (e.g., color, weight).
        _inc (list[Any]): Incident endpoints in CCW order (endpoint objects).
    """

    attr: dict[str, Any]
    _inc: list[Any]

    def __init__(
        self,
        incoming_node_data: Sequence[Any] | None = None,
        degree: int | None = None,
        **attr: Any,
    ) -> None:
        """Initialize a node with optional incident endpoints and attributes.

        Args:
            incoming_node_data: Existing sequence of incident endpoints; if shorter than
                ``degree``, it will be padded with ``None``.
            degree: Desired degree (len of incident endpoints). If omitted, inferred
                from ``incoming_node_data`` (or 0 if not provided).
            **attr: Node attributes to set.

        Raises:
            ValueError: If ``incoming_node_data`` is longer than ``degree``.
        """
        incoming_node_data = list(incoming_node_data or [])
        if degree is None:
            degree = len(incoming_node_data) if incoming_node_data is not None else 0

        if len(incoming_node_data) > degree:
            raise ValueError(
                f"Cannot create node {incoming_node_data} larger than its degree ({degree})"
            )

        if len(incoming_node_data) < degree:
            incoming_node_data += [None] * (degree - len(incoming_node_data))

        self.attr = dict(attr)
        self._inc = list(incoming_node_data)
        super().__init__()

    # List-like protocol over incident endpoints

    def __iter__(self) -> Iterator[Any]:
        """Iterate over incident endpoints in CCW order.

        Returns:
            iterator: Iterator of endpoints.
        """
        return iter(self._inc)

    def __getitem__(self, position: int) -> Any:
        """Return the endpoint at a given position.

        Args:
            position: Position index.

        Returns:
            Any: Endpoint at ``position``.
        """
        return self._inc[position]

    def __setitem__(self, position: int, endpoint: Any) -> "Node":
        """Set an endpoint at a given position.

        Args:
            position: Position index.
            endpoint: New endpoint object.

        Returns:
            Node: ``self`` for chaining.
        """
        self._inc[position] = endpoint
        return self

    def __delitem__(self, position: int) -> None:
        """Delete the endpoint at a given position.

        Args:
            position: Position index to delete.
        """
        del self._inc[position]

    def append(self, item: Any) -> None:
        """Append an endpoint at the end.

        Args:
            item: Endpoint to append.
        """
        self._inc.append(item)

    def __len__(self) -> int:
        """Return the node degree.

        Returns:
            int: Number of incident endpoints.
        """
        return len(self._inc)

    def __hash__(self) -> int:
        """Return a stable hash for the node.

        Notes:
            Mirrors endpoint hashing behavior by including optional ``color``
            and the incident endpoints.

        Returns:
            int: Hash value.
        """
        return hash((type(self), self.attr.get("color", None), *self._inc))

    def _compare(self, other: "Node", compare_attributes: bool | Sequence[str] = False) -> int:
        """Three-way compare by degree, type, endpoints, and (optionally) attributes.

        Args:
            other: Node to compare with.
            compare_attributes: If falsy, ignore attributes. If truthy and a collection
                of keys, compare only those keys; if ``True``, compare all attributes.

        Returns:
            int: ``1`` if ``self > other``, ``-1`` if ``self < other``, else ``0``.
        """
        # 1) degree
        s_deg, o_deg = len(self._inc), len(other._inc)
        if s_deg != o_deg:
            return -1 if s_deg < o_deg else 1

        # 2) class name (stable ordering across node types)
        s_name, o_name = type(self).__name__, type(other).__name__
        if s_name != o_name:
            return 1 if s_name > o_name else -1
            # REVIEW: To lock an explicit order, use _node_name_sort_rank.get(name, 99).

        # 3) length (redundant with degree, but kept from original)
        if len(self) != len(other):
            return 1 if len(self) > len(other) else -1

        # 4) endpoint-by-endpoint comparison
        for ep, ep_other in zip(self, other):
            cmp = ep._compare(ep_other, compare_attributes)  # relies on endpoint API
            if cmp:
                return int(cmp)

        # 5) attributes
        if compare_attributes:
            if isinstance(compare_attributes, (set, list, tuple)):
                return compare_dicts(self.attr, other.attr, include_only_keys=compare_attributes)
            return compare_dicts(self.attr, other.attr)

        return 0

    def degree(self) -> int:
        """Return the node degree (number of incident endpoints).

        Returns:
            int: Degree.
        """
        return len(self)

    def __str__(self) -> str:
        """Return a compact string; NodeView typically renders nodes in diagrams.

        Returns:
            str: ``(e0 e1 e2 ...)[k=v ...]`` with ``?`` for missing endpoints.
        """
        adj_str = " ".join(str(ep) if ep is not None else "?" for ep in self._inc)
        attr_str = "".join(f" {k}={v}" for k, v in self.attr.items())
        return f"({adj_str}){attr_str}"


if __name__ == "__main__":
    pass

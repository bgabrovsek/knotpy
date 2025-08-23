from __future__ import annotations

from collections.abc import Hashable
from typing import Any
from collections.abc import Iterable

from knotpy.utils.decorators import total_ordering_from_compare
from knotpy.utils.dict_utils import compare_dicts

__all__ = ["Endpoint", "IngoingEndpoint", "OutgoingEndpoint", "Arc"]
__version__ = "0.1"

def _dict2str(d: dict[str, Any] | dict[Any, Any]) -> str:
    """Return a compact, stable string for attribute dicts.

    Booleans are rendered as bare flags: ``k`` for True, ``!k`` for False.
    Other values are rendered as ``key=value``.

    Args:
        d: Attribute mapping.

    Returns:
        str: Bracketed, comma-separated key/value list; empty string if ``d`` is falsy.

    Examples:
        >>> _dict2str({"color": "red", "locked": True, "hidden": False})
        '[color=red,locked,!hidden]'
    """
    if not d:
        return ""
    items: list[str] = []
    for k, v in d.items():
        if isinstance(v, bool):
            items.append(f"{k}" if v else f"!{k}")
        else:
            items.append(f"{k}={v}")
    return "[" + ",".join(items) + "]"


@total_ordering_from_compare
class Endpoint:
    """Endpoint at a given node and position, with optional attributes.

    Endpoints are incidences of nodes in a planar diagram. Oriented variants are
    represented by subclasses :class:`IngoingEndpoint` and :class:`OutgoingEndpoint`.

    Attributes:
        node (Hashable): Node identifier.
        position (int): Position index at the node (counter-clockwise order).
        attr (dict[str, Any]): Arbitrary endpoint attributes (e.g., colors).
    """

    node: Hashable
    position: int
    attr: dict[str, Any]

    def __init__(self, node: Hashable, position: int, **attr: Any) -> None:
        """Construct an endpoint.

        Args:
            node: Node identifier.
            position: Position index at the node.
            **attr: Arbitrary endpoint attributes.
        """
        self.node = node
        self.position = int(position)
        self.attr = dict(attr)

    def __iter__(self):
        """Allow tuple-unpacking into ``(node, position)``.

        Returns:
            iterator: Iterator over ``(node, position)``.
        """
        return iter((self.node, self.position))

    def __str__(self) -> str:
        """Return a compact string representation.

        Returns:
            str: String like ``a0i[color=red]`` / ``(3,2)o`` / ``x1`` etc.
        """
        if isinstance(self.node, str):
            s = f"{self.node}{self.position}"
        else:
            s = f"({self.node},{self.position})"

        if type(self) is IngoingEndpoint:
            s += "i"
        elif type(self) is OutgoingEndpoint:
            s += "o"

        s += _dict2str(self.attr)
        return s

    def __hash__(self) -> int:
        """Return a stable hash.

        Notes:
            Includes endpoint type, optional color, node, and position.

        Returns:
            int: Hash value.
        """
        return hash((type(self), self.attr.get("color", None), self.node, self.position))

    def _compare(self, other: "Endpoint", compare_attributes: bool | list[str] | set[str] | tuple[str, ...] = False) -> int:
        """Three-way compare with optional attribute comparison.

        Ordering rules:
        1) Oriented type: ``IngoingEndpoint`` > ``OutgoingEndpoint``; unoriented only comparable to unoriented.
        2) Node identifier.
        3) Position index.
        4) Optional attribute comparison (by selected keys or all).

        Args:
            other: Endpoint to compare with.
            compare_attributes: If truthy, compare attributes. If a collection of keys,
                compare only those keys; if ``True``, compare all keys.

        Returns:
            int: ``1`` if ``self > other``, ``-1`` if ``self < other``, else ``0``.

        Raises:
            TypeError: If comparing oriented with unoriented endpoints.
        """
        # oriented vs unoriented compatibility
        if type(self) is Endpoint and type(other) in (IngoingEndpoint, OutgoingEndpoint):
            raise TypeError("Cannot compare unoriented endpoints with oriented endpoints")
        if type(other) is Endpoint and type(self) in (IngoingEndpoint, OutgoingEndpoint):
            raise TypeError("Cannot compare oriented endpoints with unoriented endpoints")

        # oriented ordering: Ingoing > Outgoing
        if type(self) is IngoingEndpoint and type(other) is OutgoingEndpoint:
            return 1
        if type(self) is OutgoingEndpoint and type(other) is IngoingEndpoint:
            return -1

        # node id
        if self.node != other.node:
            return 1 if self.node > other.node else -1

        # position
        if self.position != other.position:
            return 1 if self.position > other.position else -1

        # attributes (optional)
        if compare_attributes:
            if isinstance(compare_attributes, (set, list, tuple)):
                return compare_dicts(self.attr, other.attr, include_only_keys=compare_attributes)
            return compare_dicts(self.attr, other.attr)

        return 0

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute key/value.

        Args:
            key: Attribute key.
            value: Attribute value.
        """
        self.attr[key] = value

    def __getitem__(self, key: str) -> Any:
        """Return an attribute value (or ``None``).

        Args:
            key: Attribute key.

        Returns:
            Any: Stored value or ``None`` if missing.
        """
        return self.attr.get(key, None)

    def get(self, key: str, __default: Any = None) -> Any:
        """Return an attribute value with a default.

        Args:
            key: Attribute key.
            __default: Default value if key is missing.

        Returns:
            Any: Stored value or ``__default``.
        """
        return self.attr.get(key, __default)

    def __contains__(self, key: str) -> bool:
        """Return whether an attribute key is present.

        Args:
            key: Attribute key.

        Returns:
            bool: ``True`` if present, else ``False``.
        """
        return key in self.attr

    @staticmethod
    def reverse_type() -> type["Endpoint"]:
        """Return the opposite endpoint type.

        Returns:
            type[Endpoint]: For base ``Endpoint``, returns ``Endpoint`` itself.
        """
        return Endpoint

    @staticmethod
    def is_oriented() -> bool:
        """Return whether this endpoint type is oriented.

        Returns:
            bool: ``False`` for base ``Endpoint``.
        """
        return False

    def __repr__(self) -> str:
        """Return ``repr(self)`` (delegates to ``__str__``).

        Returns:
            str: Representation string.
        """
        return str(self)


class IngoingEndpoint(Endpoint):
    """Oriented incoming endpoint."""

    @staticmethod
    def reverse_type() -> type["OutgoingEndpoint"]:
        """Return the opposite endpoint type.

        Returns:
            type[OutgoingEndpoint]: The outgoing endpoint class.
        """
        return OutgoingEndpoint

    @staticmethod
    def is_oriented() -> bool:
        """Return whether the endpoint type is oriented.

        Returns:
            bool: Always ``True``.
        """
        return True


class OutgoingEndpoint(Endpoint):
    """Oriented outgoing endpoint."""

    @staticmethod
    def reverse_type() -> type["IngoingEndpoint"]:
        """Return the opposite endpoint type.

        Returns:
            type[IngoingEndpoint]: The ingoing endpoint class.
        """
        return IngoingEndpoint

    @staticmethod
    def is_oriented() -> bool:
        """Return whether the endpoint type is oriented.

        Returns:
            bool: Always ``True``.
        """
        return True


def ensure_endpoint(k, ep_like) -> Endpoint:
    """Return an Endpoint for an endpoint-like input.

    Args:
        k (PlanarDiagram): A planar diagram providing ``endpoint_from_pair``.
        ep_like: Either an Endpoint instance or a pair ``(node, position)``.

    Returns:
        Endpoint: The concrete endpoint object in ``k``.
    """
    if isinstance(ep_like, Endpoint):
        return ep_like
    node, pos = ep_like
    return k.endpoint_from_pair((node, pos))


def ensure_arc(k, arc_like) -> frozenset[Endpoint]:
    """
    Convert various arc-like inputs into a frozenset of two Endpoints.

    Args:
        k: A PlanarDiagram containing the arc.
        arc_like: Either a frozenset, set, list, or tuple containing two endpoints
                  (Endpoints or (node, position) tuples).

    Returns:
        frozenset[Endpoint]: The arc as a frozenset of two validated Endpoints.
    """
    if not isinstance(arc_like, Iterable) or len(arc_like) != 2:
        raise TypeError(f"Arc must be an iterable of two endpoints, got: {arc_like!r}")

    ep1, ep2 = (ensure_endpoint(k, ep) for ep in arc_like)
    return frozenset({ep1, ep2})


Arc = frozenset[Endpoint]
EndpointLike = Endpoint | tuple

if __name__ == "__main__":
    pass

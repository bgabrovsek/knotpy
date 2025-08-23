# knotpy/algorithms/attributes.py

"""
Utilities for clearing attributes on diagrams (node, endpoint, and diagram-level attributes).

These helpers work both on a single diagram and on collections (list, set, tuple)
of diagrams. Attribute selection can be a single string or an iterable of strings.
"""

__all__ = [
    "clear_node_attributes",
    "clear_endpoint_attributes",
    "clear_diagram_attributes",
    "clear_attributes",
    "clear_temporary_node_attributes",
    "clear_temporary_endpoint_attributes",
    "clear_temporary_diagram_attributes",
    "clear_temporary_attributes",
]
__version__ = "0.3"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import (
    PlanarDiagram,
    OrientedPlanarDiagram,
    Diagram,             # type alias: PlanarDiagram | OrientedPlanarDiagram
    DiagramCollection,   # type alias: list[Diagram] | set[Diagram] | tuple[Diagram, ...]
)


def _as_attr_list(attr) -> list[str] | None:
    """Normalize `attr` to a list of strings (or None)."""
    if attr is None:
        return None
    if isinstance(attr, (list, set, tuple)):
        return [str(a) for a in attr]
    return [str(attr)]


def _iter_diagrams(obj: Diagram | DiagramCollection):
    """Yield diagrams from a diagram or a collection of diagrams."""
    if isinstance(obj, (list, set, tuple)):
        for d in obj:
            yield from _iter_diagrams(d)
    else:
        yield obj


def clear_node_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear node attributes.

    Args:
        k: A diagram or a collection of diagrams.
        attr: Attribute name or iterable of names to remove. If None, clear all node attrs.

    Raises:
        TypeError: If any element is not a PlanarDiagram/OrientedPlanarDiagram.
    """
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        if not isinstance(d, (PlanarDiagram, OrientedPlanarDiagram)):
            raise TypeError(f"k should be a PlanarDiagram, got {type(d)}")
        for node in d.nodes:
            if attrs is None:
                d.nodes[node].attr.clear()
            else:
                for key in attrs:
                    d.nodes[node].attr.pop(key, None)


def clear_endpoint_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear endpoint attributes.

    Args:
        k: A diagram or a collection of diagrams.
        attr: Attribute name or iterable of names to remove. If None, clear all endpoint attrs.
    """
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        for ep in d.endpoints:
            ep_attr = d.nodes[ep.node][ep.position].attr
            if attrs is None:
                ep_attr.clear()
            else:
                for key in attrs:
                    ep_attr.pop(key, None)


def clear_diagram_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear diagram-level attributes.

    Args:
        k: A diagram or a collection of diagrams.
        attr: Attribute name or iterable of names to remove. If None, clear all diagram attrs.
    """
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        if attrs is None:
            d.attr.clear()
        else:
            for key in attrs:
                d.attr.pop(key, None)


def clear_attributes(k: Diagram | DiagramCollection) -> None:
    """Clear all attributes (nodes, endpoints, diagram-level)."""
    clear_node_attributes(k)
    clear_endpoint_attributes(k)
    clear_diagram_attributes(k)


def clear_temporary_node_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear temporary node attributes (keys starting with '_').

    Args:
        k: A diagram or a collection of diagrams.
        attr: Optional specific temporary key(s) to remove (must start with '_').
              If None, remove all temporary node keys.
    """
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        if attrs is None:
            for node in d.nodes:
                for key in list(d.nodes[node].attr):
                    if isinstance(key, str) and key.startswith("_"):
                        d.nodes[node].attr.pop(key, None)
        else:
            for node in d.nodes:
                for key in attrs:
                    if isinstance(key, str) and key.startswith("_"):
                        d.nodes[node].attr.pop(key, None)


def clear_temporary_endpoint_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear temporary endpoint attributes (keys starting with '_')."""
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        if attrs is None:
            for ep in d.endpoints:
                ep_attr = d.nodes[ep.node][ep.position].attr
                for key in list(ep_attr):
                    if isinstance(key, str) and key.startswith("_"):
                        ep_attr.pop(key, None)
        else:
            for ep in d.endpoints:
                ep_attr = d.nodes[ep.node][ep.position].attr
                for key in attrs:
                    if isinstance(key, str) and key.startswith("_"):
                        ep_attr.pop(key, None)


def clear_temporary_diagram_attributes(k: Diagram | DiagramCollection, attr: str | list[str] | set[str] | tuple[str, ...] | None = None) -> None:
    """Clear temporary diagram-level attributes (keys starting with '_')."""
    attrs = _as_attr_list(attr)
    for d in _iter_diagrams(k):
        if attrs is None:
            for key in list(d.attr):
                if isinstance(key, str) and key.startswith("_"):
                    d.attr.pop(key, None)
        else:
            for key in attrs:
                if isinstance(key, str) and key.startswith("_"):
                    d.attr.pop(key, None)


def clear_temporary_attributes(k: Diagram | DiagramCollection) -> None:
    """Clear all temporary attributes (keys starting with '_') at all levels."""
    clear_temporary_node_attributes(k)
    clear_temporary_endpoint_attributes(k)
    clear_temporary_diagram_attributes(k)


if __name__ == "__main__":
    pass
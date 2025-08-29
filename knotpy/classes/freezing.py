from __future__ import annotations

from knotpy.classes.planardiagram import OrientedPlanarDiagram, PlanarDiagram

__all__ = ["freeze", "unfreeze", "lock"]


def frozen(*_: object, **__: object) -> None:
    """Dummy method used on frozen diagrams to block mutation.

    Raises:
        RuntimeError: Always (frozen diagrams cannot be modified).
    """
    raise RuntimeError("Frozen diagrams cannot be modified")


# All mutating instance methods we disable/restore while frozen.
# Keeping this list in one place avoids drift between freeze() and unfreeze().
_MUTATING_METHODS: tuple[str, ...] = (
    "add_node",
    "add_nodes_from",
    "add_crossing",
    "add_crossings_from",
    "add_virtual_crossing",
    "add_virtual_crossings_from",
    "add_vertex",
    "add_vertices_from",
    "permute_node",
    "convert_node",
    "remove_node",
    "remove_nodes_from",
    "relabel_nodes",
    "set_endpoint",
    "remove_endpoint",
    "remove_endpoints_from",
    "set_arc",
    "set_arcs_from",
    "remove_arc",
    "remove_arcs_from",
)



def freeze(k: PlanarDiagram | OrientedPlanarDiagram, inplace: bool = True) -> PlanarDiagram:
    """Freeze a planar diagram so it cannot be modified.

    Freezing monkey-patches mutating methods on the instance to a dummy
    method that raises ``RuntimeError``. The diagram’s data stays intact.

    Args:
        k: Diagram to freeze.
        inplace: If ``True``, freeze ``k`` in place; otherwise work on a shallow copy.

    Returns:
        PlanarDiagram: The frozen diagram (``k`` or its copy).

    Examples:
        >>> from knotpy.classes.planardiagram import PlanarDiagram
        >>> d = PlanarDiagram()
        >>> d.add_vertices_from(["a", "b"])
        >>> freeze(d)
        PlanarDiagram(...)  # doctest: +ELLIPSIS
        >>> d.is_frozen()
        True
        >>> d.add_vertex("c")
        Traceback (most recent call last):
            ...
        RuntimeError: Frozen diagrams cannot be modified
    """
    diag = k if inplace else k.copy()

    if diag.is_frozen():
        return diag

    diag.frozen = True  # used by is_frozen()

    # Patch mutating methods that exist on this type
    for name in _MUTATING_METHODS:
        if hasattr(diag, name):
            setattr(diag, name, frozen)

    # NOTE: The framing setter already checks is_frozen(); further override not needed.
    # TODO: Consider recursively freezing node/endpoint attribute containers if needed.

    return diag

def lock(k: PlanarDiagram | OrientedPlanarDiagram, inplace: bool = True) -> PlanarDiagram:
    """Lock a planar diagram so it cannot be modified. Unlike freezing, a diagram cannot be unlocked.
    Used for knot tables, so the user cannot modify a knot in a precomputed knot table.
    """
    diag = freeze(k, inplace=inplace)
    diag.frozen = "locked"  # used by is_frozen()
    return diag

def unfreeze(k: PlanarDiagram | OrientedPlanarDiagram, inplace: bool = True) -> PlanarDiagram:
    """Unfreeze a planar diagram so it can be modified again.

    Restores original bound methods from the diagram’s class. Useful when a
    frozen diagram was used as a dict/set key and you want to mutate it again.

    Args:
        k: Diagram to unfreeze.
        inplace: If ``True``, unfreeze ``k`` in place; otherwise operate on a shallow copy.

    Returns:
        PlanarDiagram: The unfrozen diagram (``k`` or its copy).

    Examples:
        >>> from knotpy.classes.planardiagram import PlanarDiagram
        >>> d = PlanarDiagram()
        >>> freeze(d)
        PlanarDiagram(...)  # doctest: +ELLIPSIS
        >>> unfreeze(d)
        PlanarDiagram(...)  # doctest: +ELLIPSIS
        >>> d.is_frozen()
        False
        >>> d.add_vertex("x")  # works again
    """
    diag = k if inplace else k.copy()

    if not diag.is_frozen():
        return diag

    if diag.frozen == "locked":
        raise ValueError("Cannot unfreeze a locked diagram.")

    diag.frozen = False

    # Rebind original instance methods from the class descriptors
    cls = type(diag)
    for name in _MUTATING_METHODS:
        if hasattr(cls, name):  # only restore methods that exist on this class
            setattr(diag, name, getattr(cls, name).__get__(diag))

    # NOTE: The framing setter remains as defined on the class and will now permit changes again.

    return diag


if __name__ == "__main__":
    pass

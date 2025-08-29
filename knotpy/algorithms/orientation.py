# knotpy/algorithms/orientation.py

"""
Algorithms that deal with orientation.
"""

__all__ = ["orient", "unorient", "orientations", "reverse"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import itertools as it

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.algorithms.topology import edges as compute_edges


def orient_edges(k: PlanarDiagram, edge_paths: list[list[Endpoint]]) -> OrientedPlanarDiagram:
    """Orient an unoriented diagram along given edge paths.

    Each item in ``edge_paths`` is a sequence of endpoints describing an edge
    as a chain of alternating endpoints. The orientation is assigned along each
    path by pairing consecutive endpoints: (0→1), (2→3), ...

    Args:
        k: Unoriented diagram to orient.
        edge_paths: List of edge endpoint sequences. For each path, orientation
            goes from index 0 to 1, 2 to 3, etc. If you want the opposite
            orientation for a particular edge, reverse that list.

    Returns:
        A new :class:`OrientedPlanarDiagram`.

    Example:
        >>> # Given an unoriented diagram k:
        >>> paths = compute_edges(k)               # list of edges (endpoint sequences)
        >>> ok = orient_edges(k, paths)            # orient along the given direction
    """
    new_k = OrientedPlanarDiagram(**k.attr)

    # copy nodes
    for node, inst in k.nodes.items():
        new_k.add_node(
            node_for_adding=node,
            create_using=type(inst),
            degree=len(inst),
            **inst.attr,
        )

    # wire oriented endpoints
    for path in edge_paths:
        # pair up (0->1), (2->3), ...
        for ep, twin_ep in zip(path[::2], path[1::2]):
            # forward direction
            new_k.set_endpoint(
                endpoint_for_setting=(ep.node, ep.position),
                adjacent_endpoint=(twin_ep.node, twin_ep.position),
                create_using=OutgoingEndpoint,
                **ep.attr,
            )
            # reverse direction
            new_k.set_endpoint(
                endpoint_for_setting=(twin_ep.node, twin_ep.position),
                adjacent_endpoint=(ep.node, ep.position),
                create_using=IngoingEndpoint,
                **twin_ep.attr,
            )

    return new_k


def orientations(k: PlanarDiagram, up_to_reversal: bool = False) -> list[OrientedPlanarDiagram]:
    """Generate all orientations of an unoriented diagram.

    If ``up_to_reversal`` is True, the first edge is always oriented “forward”
    and only the remaining edges are flipped (removing a global reversal).

    Args:
        k: Unoriented diagram.
        up_to_reversal: If True, return orientations modulo global reversal.

    Returns:
        List of :class:`OrientedPlanarDiagram`.

    Notes:
        - If ``k`` is already oriented, it is first “unoriented” (structure
          preserved) and then all orientations are generated.
        - If ``k.name`` is set, each result’s name is suffixed with a string of
          “+”/“–” per-edge choices (useful for debugging).

    Example:
        >>> import knotpy as kp
        >>> k = kp.knot("3_1")
        >>> k1, k2 = kp.orientations(k)
        >>> print(f'Oriented trefoils: {k1} and {k2}')
        Oriented diagrams: Diagram named 3_1+ a → X(b3o c0i c3i b0o), b → X(a3i c2o c1o a0i), c → X(a1o b2i b1i a2o) and Diagram named 3_1- a → X(b3i c0o c3o b0i), b → X(a3o c2i c1i a0o), c → X(a1i b2o b1o a2i)
    """
    if k.is_oriented():
        k = unorient(k)

    edge_list = sorted(compute_edges(k))
    m = len(edge_list)

    if up_to_reversal:
        # fix first edge to True, vary the rest
        flip_choices = [(True,) + rest for rest in it.product((True, False), repeat=m - 1)]
    else:
        flip_choices = list(it.product((True, False), repeat=m))

    results: list[OrientedPlanarDiagram] = []
    for choice in flip_choices:
        oriented_paths = [e if keep else e[::-1] for e, keep in zip(edge_list, choice)]
        ok = orient_edges(k, oriented_paths)

        if k.name:
            suffix = "".join("+" if keep else "-" for keep in choice)
            ok.name = f"{k.name}{suffix}"
        results.append(ok)

    return results


def orient(k: PlanarDiagram) -> OrientedPlanarDiagram:
    """Orient an unoriented diagram using the default edge directions.

    This picks the natural direction for every edge returned by
    :func:`knotpy.algorithms.topology.edges`.

    Args:
        k: Unoriented diagram.

    Returns:
        Oriented diagram.

    Example:
        >>> import knotpy as kp
        >>> k = kp.knot("3_1")
        >>> kp.orient(k)
        Diagram named 3_1 a → X(b3o c0i c3i b0o), b → X(a3i c2o c1o a0i), c → X(a1o b2i b1i a2o)
    """
    return orient_edges(k, compute_edges(k))


def reverse(k: OrientedPlanarDiagram, inplace: bool = False) -> OrientedPlanarDiagram:
    """Reverse orientation of an oriented diagram.

    Swaps each arc's endpoint types (ingoing/outgoing) accordingly.

    Args:
        k: Oriented planar diagram to reverse.
        inplace: If ``True``, modify ``k`` in place, otherwise return a copy.

    Returns:
        The orientation-reversed diagram.

    Raises:
        TypeError: If ``k`` is an unoriented ``PlanarDiagram``.
    """
    if type(k) is PlanarDiagram:
        raise TypeError("Cannot reverse an unoriented planar diagram")

    if not inplace:
        k = k.copy()

    # Rewrite all arcs with reversed endpoint types.
    for ep1, ep2 in list(k.arcs):
        k.set_endpoint(
            endpoint_for_setting=(ep1.node, ep1.position),
            adjacent_endpoint=(ep2.node, ep2.position),
            create_using=type(ep2).reverse_type(),
            **k.nodes[ep2.node].attr,
        )
        k.set_endpoint(
            endpoint_for_setting=(ep2.node, ep2.position),
            adjacent_endpoint=(ep1.node, ep1.position),
            create_using=type(ep1).reverse_type(),
            **k.nodes[ep1.node].attr,
        )

    if k.name and isinstance(k.name, str):
        if k.name[0] == "+":
            k.name = "-" + k.name[1:]
        elif k.name[0] == "-":
            k.name = "+" + k.name[1:]
        else:
            k.name = "-" + k.name


    return k


def unorient(k: OrientedPlanarDiagram | PlanarDiagram) -> PlanarDiagram:
    """Return an unoriented copy of the diagram."""
    return k.copy(copy_using=PlanarDiagram)


if __name__ == "__main__":
    pass
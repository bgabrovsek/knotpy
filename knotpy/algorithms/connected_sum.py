""""
Two knots (or links or planar diagrams) can be summed by placing them side by side
and joining them by straight bars so that orientation is preserved in the sum.
The knot sum is also known as composition (Adams 1994) or connected sum (Rolfsen 1976, p. 40).
"""
__all__ = ['is_connected_sum', 'is_connected_sum_third_order', "connected_sum_decomposition", "connected_sum"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from collections import deque

from knotpy.classes.planardiagram import Diagram
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.disjoint_union import disjoint_union_decomposition, disjoint_union
from knotpy.algorithms.cut_set import find_arc_cut_set


def is_connected_sum(k: PlanarDiagram | OrientedPlanarDiagram) -> bool:
    """Determine if the given planar diagram represents a connected sum.

    A connected sum is checked if there is an arc-cut-set of order 2, i.e. removing two arcs from the
    diagram disconnects it into two components.

    Args:
        k (PlanarDiagram | OrientedPlanarDiagram): A planar diagram to check for connected sum property.

    Returns:
        bool: True if the diagram is a connected sum; otherwise, False.
    """
    return find_arc_cut_set(k, order=2, minimum_partition_nodes=2) is not None

def _split_at_arcs(k: Diagram, arcs: tuple[frozenset[Endpoint], frozenset[Endpoint]]) -> list[Diagram]:
    """Split a planar diagram at the given arcs."""
    (e, f) = arcs  # get the two edges of the cut-set
    e_a, e_b = e
    f_a, f_b = f

    faces = list(k.faces)  # maybe list is not needed

    # cross-edges
    aa = {e_a, f_a}
    bb = {e_b, f_b}
    ab = {e_a, f_b}
    ba = {e_b, f_a}

    if any(aa.issubset(f) for f in faces) and any(bb.issubset(f) for f in faces):
        a, b, x, y = e_a, f_b, e_b, f_a  # connect a b and x y
    elif any(ab.issubset(f) for f in faces) and any(ba.issubset(f) for f in faces):
        a, b, x, y = e_a, f_a, e_b, f_b  # connect a b and x y
    else:
        raise ValueError(f"Cannot determine how to cut a composite knot {k}")

    # redirect endpoint, so that we get a split (disjoint sum)
    s = k.copy()
    s.set_endpoint(a, b, create_using=type(a), **a.attr)
    s.set_endpoint(b, a, create_using=type(b), **b.attr)
    s.set_endpoint(x, y, create_using=type(y), **y.attr)
    s.set_endpoint(y, x, create_using=type(x), **x.attr)

    return disjoint_union_decomposition(s)


def connected_sum_decomposition(k: PlanarDiagram) -> list:
    """Return a list of connected sum components."""

    result = []
    stack = deque([k])
    while stack:
        k = stack.pop()
        if (splitting_arcs := find_arc_cut_set(k, order=2, minimum_partition_nodes=2)) is None:
            # k cannot be split
            result.append(k)
        else:
            stack.extend(_split_at_arcs(k, splitting_arcs))

    if k.framing is not None:
        result[0].framing = k.framing
        for g in result[1:]:
            g.framing = 0

    return sorted(result)


def is_connected_sum_third_order(g: PlanarDiagram) -> bool:
    """Return True if g is a 3rd order connected sum diagram and False otherwise."""
    return find_arc_cut_set(g, order=3, minimum_partition_nodes=2) is not None


def connected_sum(a: Diagram, b: Diagram, arcs:None | list | tuple = None) -> Diagram:

    if type(a) != type(b):
        raise TypeError("The two diagrams must be of the same type.")

    # get the two arcs or take first available ones if they are not given
    arc_a, arc_b = arcs if arcs is not None else (next(iter(a.arcs)), next(iter(b.arcs)))

    ep_a_1, ep_a_2 = arc_a
    ep_b_1, ep_b_2 = arc_b

    ab, node_relabel_dicts = disjoint_union(a, b, return_relabel_dicts=True)

    # Switch endpoints if orientation does not match
    if type(ep_a_1) is not Endpoint and type(ep_a_1) == type(ep_b_1):
        ep_b_1, ep_b_2 = ep_b_2, ep_b_1

    # pairs where nodes are new
    p_ep_a_1 = (node_relabel_dicts[0][ep_a_1.node], ep_a_1.position)
    p_ep_a_2 = (node_relabel_dicts[0][ep_a_2.node], ep_a_2.position)
    p_ep_b_1 = (node_relabel_dicts[1][ep_b_1.node], ep_b_1.position)
    p_ep_b_2 = (node_relabel_dicts[1][ep_b_2.node], ep_b_2.position)

    ab.set_endpoint(p_ep_a_1, p_ep_b_1, create_using=type(ep_b_1), **ep_b_1.attr)
    ab.set_endpoint(p_ep_b_1, p_ep_a_1, create_using=type(ep_a_1), **ep_a_1.attr)
    ab.set_endpoint(p_ep_a_2, p_ep_b_2, create_using=type(ep_b_2), **ep_b_2.attr)
    ab.set_endpoint(p_ep_b_2, p_ep_a_2, create_using=type(ep_a_2), **ep_a_2.attr)

    if a.framing is not None or b.framing is not None:
        ab.framing = (a.framing or 0) + (b.framing or 0)

    return ab


if __name__ == "__main__":
    pass


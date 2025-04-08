""""
Two knots (or links or planar diagrams) can be summed by placing them side by side
and joining them by straight bars so that orientation is preserved in the sum.
The knot sum is also known as composition (Adams 1994) or connected sum (Rolfsen 1976, p. 40).
"""

# TODO: write tests

__all__ = ['is_connected_sum', 'is_connected_sum_third_order', "split_connected_sum"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.disjoint_sum import split_disjoint_sum
from knotpy.algorithms.cut_set import arc_cut_sets

def is_connected_sum(g: PlanarDiagram) -> bool:
    """Determine if the given planar diagram represents a connected sum.

    A connected sum is checked if there is an arc-cut-set of order 2, i.e. removing two arcs from the
    diagram disconnects it into two components.

    Args:
        g (PlanarDiagram): A planar diagram to check for connected sum property.

    Returns:
        bool: True if the diagram is a connected sum; otherwise, False.
    """
    return len(arc_cut_sets(g, order=2, max_cut_sets=1)) > 0


def split_connected_sum(k: PlanarDiagram) -> list:
    """Return a list of connected sum components."""

    if is_connected_sum(k):
        raise ValueError("Cannot spit disjoint sum into a connected sum (ambiguity)")

    cs = arc_cut_sets(k, order=2, max_cut_sets=1)
    if not cs:
        return [k]

    (e, f), = cs  # get the two edges of the cut-set
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

    return split_disjoint_sum(s)

def is_connected_sum_third_order(g: PlanarDiagram) -> bool:
    """Return True if g is a 3rd order connected sum diagram and False otherwise."""
    return len(arc_cut_sets(g, order=3, max_cut_sets=1)) > 0

# TODO: make connected sum

if __name__ == "__main__":
    pass
    # import knotpy as kp
    # k = kp.from_pd_notation("X[0,1,2,3],X[1,0,3,4],X[5,2,6,7],X[4,5,7,6]")
    # print(k)
    # print(cut_sets(k, order=2, max_cut_sets=1))


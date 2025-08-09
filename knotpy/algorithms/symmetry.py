# knotpy/algorithms/symmetry.py

"""
Symmetry operations on planar knot diagrams.
"""

__all__ = ["mirror", "flip", "reverse"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

# Oriented
# chiral K, K*, -K, -K*
# fully amphicheiral K = K* = -K = -K*
# negative amphicheiral K = -K*, K* = -K
# positive amphicheiral K = K*, -K = -K*
# reversible K = -K. *K = -*K
#
# Non-oriented
# chiral K, K*
# fully amphicheiral, K = K*
# negative amphicheiral, K = K*
# positive amphicheiral, K = K*
# reversible K, K*
#
# 1 chiral, noninvertible
# 1, 3 + amphichiral, noninvertible
# 1, 4 - amphichiral, noninvertible
# 1, 2, chiral, invertible
# 1,2,3,4 + and - amphichiral, invertible
#
# 1. preserves R^3, preserves K
# 2. preserves R^3, reverses K
# 3. reverses R^3, preserces K,
# 4. reverses R^4, reverses K

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.rewire import permute_node


def mirror(
    k: PlanarDiagram | OrientedPlanarDiagram,
    crossings: set | list | tuple | None = None,
    inplace: bool = False,
):
    """Mirror a planar diagram.

    For each crossing in ``crossings`` (or all crossings, if omitted), apply the
    permutation ``(1,2,3,0)`` which performs a quarter-rotation that mirrors the
    local crossing structure. Works for oriented and unoriented diagrams.

    Args:
        k: Diagram to mirror.
        crossings: Optional container of crossing node labels to mirror.
            If ``None``, all crossings are mirrored.
        inplace: If ``True``, modify ``k`` in place, otherwise return a copy.

    Returns:
        The mirrored diagram (``k`` if ``inplace=True``; otherwise a new instance).
    """
    if not inplace:
        k = k.copy()

    if crossings is None:
        crossings = set(k.crossings)

    # Apply the same permutation in both oriented and unoriented cases.
    for c in crossings:
        permute_node(k, c, (1, 2, 3, 0))

    return k


def flip(
    k: PlanarDiagram | OrientedPlanarDiagram,
    nodes: set | list | tuple | None = None,
    inplace: bool = False,
):
    """Flip the diagram by 180° around each selected node.

    This reverses the cyclic order of incident endpoints at the specified nodes.
    In S³ / ℝ³ this does not change the knot type or planar diagram type.

    Args:
        k: Diagram to flip.
        nodes: Optional container of node labels to flip. If ``None``, all nodes are flipped.
        inplace: If ``True``, modify ``k`` in place, otherwise return a copy.

    Returns:
        The flipped diagram (``k`` if ``inplace=True``; otherwise a new instance).
    """
    if not inplace:
        k = k.copy()

    if nodes is None:
        nodes = list(k.nodes)

    for node in nodes:
        deg = k.degree(node)
        # Reverse order: [deg-1, deg-2, ..., 0]
        permute_node(k, node, list(range(deg - 1, -1, -1)))

    return k


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

    return k


if __name__ == "__main__":
    pass
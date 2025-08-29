# knotpy/algorithms/symmetry.py

"""
Symmetry operations on planar knot diagrams.
"""

__all__ = ["mirror", "flip"]
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

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram, Diagram
from knotpy.algorithms.rewire import permute_node


def mirror(
    k: Diagram,
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

    if k.name and isinstance(k.name, str):
        # if the link is oriented, add a '*' to the name before orientation signs
        i = len(k.name)
        while i > 0 and k.name[i - 1] in "+-":
            i -= 1
        orientation_str = k.name[i:]
        base_str = k.name[:i]
        if base_str.endswith("*"):
            k.name = base_str[:-1] + orientation_str
        else:
            k.name = base_str + "*" +orientation_str

    return k


def flip(
    k: Diagram,
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


if __name__ == "__main__":
    pass
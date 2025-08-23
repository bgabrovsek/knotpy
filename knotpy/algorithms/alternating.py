# knotpy/algorithms/alternating.py

"""
Algorithms for detecting whether a planar diagram is alternating.
"""

__all__ = ["is_alternating", "is_face_alternating"]
__version__ = "0.3"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import Diagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.topology import edges


def _parity_diff(values: list[int], cyclic: bool = False) -> list[int]:
    """Return (mod 2) differences of consecutive entries.

    Args:
        values: List of integers.
        cyclic: If True, treat the list as cyclic (compare last with first).

    Returns:
        List of differences modulo 2.

    """
    if not values:
        return []
    data = values + values[:1] if cyclic else values
    return [(b - a) % 2 for a, b in zip(data, data[1:])]


def is_alternating(k: Diagram) -> bool:
    """Check if a diagram is alternating.

    A diagram is alternating if each edge meets consecutive endpoints of alternating parity around crossings.

    Args:
        k: Planar diagram.

    Returns:
        True if `k` is alternating, False otherwise.

    Example:
        >>> import knotpy as kp
        >>> k = kp.knot("8_19")
        >>> kp.is_alternating(k)
        False
    """

    def _edge_is_alternating(edge: list) -> bool:
        # An edge is a list of endpoints; use their .position modulo 2.
        starts_at_crossing = (
            isinstance(k.nodes[edge[0].node], Crossing)
            and isinstance(k.nodes[edge[-1].node], Crossing)
            and edge[0].node == edge[-1].node
        )
        if starts_at_crossing:
            seq = [ep.position for ep in edge]
            # Two rounds of parity differences must all be 1 for a 4-valent crossing alternation.
            return all(x == 1 for x in _parity_diff(_parity_diff(seq, cyclic=True), cyclic=True))
        else:
            # Skip the free endpoints at ends; check interior parity alternation.
            seq = [ep.position for ep in edge[1:-1]]
            return all(x == 1 for x in _parity_diff(_parity_diff(seq, cyclic=False), cyclic=False))

    return all(_edge_is_alternating(edge) for edge in edges(k))


# def alternating_crossings(k: Diagram) -> list:
#     """Return crossings that have at least two alternating neighbours.
#
#     Args:
#         k: Planar diagram.
#
#     Returns:
#         List of crossing identifiers that satisfy the alternation criterion.
#     """
#     result = []
#     for c in k.crossings:
#         inc = k.nodes[c]
#         cond_over = (inc[0].position % 2 == 1) and (inc[2].position % 2 == 1) and inc[0].node != c and inc[2].node != c
#         cond_under = (inc[1].position % 2 == 0) and (inc[3].position % 2 == 0) and inc[1].node != c and inc[3].node != c
#         if cond_over or cond_under:
#             result.append(c)
#     return result


def is_face_alternating(face: tuple) -> bool:
    """Check if the arcs of the bounding the face are alternating. Used e.g. by detecting a Reidemeister 3-face.

    Args:
        face: A list of endpoints forming a face boundary in CCW order.

    Returns:
        True if all positions share the same parity as face[0], else False.
    """
    return all(ep.position % 2 == face[0].position % 2 for ep in face)


if __name__ == "__main__":
    pass
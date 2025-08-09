# knotpy/algorithms/degree_sequence.py

"""
Degree and neighborhood growth sequences for planar diagrams.
"""

__all__ = ["degree_sequence", "neighbour_sequence"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.set_utils import LeveledSet


def degree_sequence(k: PlanarDiagram) -> tuple[int, ...]:
    """
    Return the sorted degree sequence of all nodes.

    Args:
        k: Unoriented planar diagram.

    Returns:
        Tuple of node degrees in nondecreasing order.
    """
    return tuple(sorted(k.degree(v) for v in k.nodes))


def neighbour_sequence(k: PlanarDiagram, node) -> tuple[int, ...]:
    """
    Return the BFS layer sizes starting from ``node``.

    This is the “neighbor sequence” used in canonicalization: perform a BFS
    from ``node`` and record how many *new* nodes appear at each distance.

    Args:
        k: Unoriented planar diagram.
        node: Starting node.

    Returns:
        Tuple where the i-th entry is the number of nodes at distance i from
        ``node`` (i ≥ 1). The 0-th layer (the start) is not included.

    Raises:
        KeyError: If ``node`` is not present in the diagram.
    """
    if node not in k.nodes:
        raise KeyError(f"Node {node!r} not found in the diagram.")

    seq = LeveledSet([node])

    # Build successive BFS layers until the last layer is empty.
    while not seq.is_level_empty(-1):
        seq.new_level()
        seq.extend(ep.node for v in seq.iter_level(-2) for ep in k.nodes[v])

    # Drop the last (empty) layer count.
    return seq.level_sizes()[:-1]


if __name__ == "__main__":
    pass
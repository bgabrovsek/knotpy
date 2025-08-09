# knotpy/algorithms/cycles.py

"""
Enumerate simple cycles of a given length.
"""

__all__ = ["cycles"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from knotpy.classes.planardiagram import PlanarDiagram


def cycles(g: PlanarDiagram, n: int) -> set[tuple]:
    """
    Return all simple cycles of length ``n`` in the diagram.

    Cycles are reported in a canonical form: among all rotations and the reversed
    cycle’s rotations, the lexicographically smallest tuple is kept. This avoids
    duplicates caused by different starting points or direction.

    Args:
        g: Unoriented planar diagram.
        n: Target cycle length (must be ≥ 1).

    Returns:
        A set of node-tuples, each tuple representing a simple cycle of length ``n``.
    """
    if n < 1:
        raise ValueError("Length must be at least 1")

    # Precompute neighbors (by node only; ignore endpoint positions)
    neighbors: dict = {v: [adj.node for adj in g.nodes[v]] for v in g.nodes}

    found: set[tuple] = set()

    def dfs(path: list, visited: set) -> None:
        curr = path[-1]
        start = path[0]

        if len(path) == n:
            # close the cycle if there is an edge back to start
            if start in neighbors[curr]:
                can = _min_lex_rotation(tuple(path))
                found.add(can)
            return

        for nb in neighbors[curr]:
            if nb in visited:
                continue
            dfs(path + [nb], visited | {nb})

    for v in g.nodes:
        dfs([v], {v})

    return found


def _min_lex_rotation(cycle: tuple) -> tuple:
    """
    Canonical representative of a cycle under rotation and reversal.
    """
    L = len(cycle)
    rots = [cycle[i:] + cycle[:i] for i in range(L)]
    rev = tuple(reversed(cycle))
    rev_rots = [rev[i:] + rev[:i] for i in range(L)]
    return min(rots + rev_rots)


if __name__ == "__main__":
    pass
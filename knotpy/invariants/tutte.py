# knotpy/invariants/tutte.py
"""
Tutte polynomial for planar graphs represented as ``PlanarDiagram`` objects.

This computes the Tutte polynomial ``T(_x, _y)`` for planar graphs (no crossings)
using the standard deletion–contraction recursion until only loops and bridges remain,
where each terminal graph contributes ``_x^(#bridges) * _y^(#loops)``.
"""

from __future__ import annotations

__all__ = ["tutte"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque
import sympy as sp

from knotpy.invariants._symbols import _x, _y
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.topology import (
    is_planar_graph,
    is_loop,
    is_bridge,
    bridges,
    loops,
)
from knotpy.algorithms.contract import contract_arc
from knotpy.algorithms.remove import remove_arc
from knotpy.algorithms.orientation import unorient


def deletion_contraction(k: PlanarDiagram, *, contract_bridges: bool = True) -> list[PlanarDiagram]:
    """Return terminal diagrams after recursive deletion–contraction.

    Args:
        k: Input planar diagram (graph, no crossings).
        contract_bridges: If False, skip contracting bridges (useful for Tutte T(x,y)).

    Returns:
        A list of diagrams in which every arc is a loop or a bridge.
    """
    if "_deletions" not in k.attr:
        k.attr["_deletions"] = 0
    if "_contractions" not in k.attr:
        k.attr["_contractions"] = 0

    resolved: list[PlanarDiagram] = []
    stack: deque[PlanarDiagram] = deque([k])

    while stack:
        k = stack.pop()

        has_regular_arcs = False
        for arc in k.arcs:
            # Only branch on non-loops; contract bridges only if allowed.
            if not is_loop(k, arc) and (contract_bridges or not is_bridge(k, arc)):
                k_delete = remove_arc(k, arc_for_removing=arc, inplace=False)
                k_delete.attr["_deletions"] += k.attr["_deletions"] + 1

                k_contract = contract_arc(k, arc_for_contracting=arc, inplace=False)
                k_contract.attr["_contractions"] += k.attr["_contractions"] + 1

                stack.append(k_delete)
                stack.append(k_contract)
                has_regular_arcs = True
                break  # process one arc at a time for a binary recursion

        if not has_regular_arcs:
            resolved.append(k)

    return resolved


def tutte(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Compute the Tutte polynomial ``T(_x, _y)`` of a planar graph (no crossings).

    Args:
        k: Planar diagram representing a planar graph (unoriented or oriented).

    Returns:
        SymPy expression ``T(_x, _y)``.

    Raises:
        ValueError: If ``k`` is not a planar graph (contains crossings).
    """
    if not is_planar_graph(k):
        raise ValueError("Tutte polynomial can only be computed on planar graphs without crossings.")

    # Work on an unoriented copy; ensure framing exists
    k = unorient(k) if k.is_oriented() else k.copy()
    if not k.is_framed():
        k.framing = 0
    k.attr["_deletions"] = 0
    k.attr["_contractions"] = 0

    # Expand via deletion–contraction without contracting bridges in the recursion
    terminal_graphs = deletion_contraction(k, contract_bridges=False)

    # Each terminal graph contributes _x^(#bridges) * _y^(#loops)
    polynomial = sp.Integer(0)
    for g in terminal_graphs:
        b = len(bridges(g))
        l = len(loops(g))
        if b + l != len(g.arcs):
            raise ValueError("Terminal diagram contains a non-loop, non-bridge arc.")
        polynomial += (_x ** b) * (_y ** l)

    return polynomial


if __name__ == "__main__":
    pass

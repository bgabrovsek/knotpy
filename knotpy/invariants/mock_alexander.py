# knotpy/invariants/mock_alexander.py
"""
Mock Alexander-like polynomial (face-marking heuristic).

This is a heuristic invariant built by marking at most one crossing per
non-starred face and multiplying weights depending on local data at the
marked endpoint.

Notes:
    - Orientation is ensured internally (via :func:`orient`).
    - The outgoing terminal endpoint determines the starred face set.
    - Only endpoints on crossings contribute nontrivial weights.

Returns:
    A SymPy expression in the symbol ``w``.
"""

from __future__ import annotations

__all__ = ["mock_alexander_polynomial"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque
import sympy as sp

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import OutgoingEndpoint
from knotpy.invariants._symbols import _w


def mock_alexander_polynomial(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Compute the mock Alexander polynomial via face marking.

    Args:
        k: Planar or oriented diagram. If not oriented, it will be oriented internally.

    Returns:
        SymPy expression in the symbol ``w``.
    """
    k = k if k.is_oriented() else orient(k)

    # Choose the outgoing terminal of degree 1 as the starting endpoint (starred face selector).
    terminals = [
        ep for ep in k.endpoints if k.degree(ep.node) == 1 and isinstance(ep, OutgoingEndpoint)
    ]
    if not terminals:
        # For links without such an endpoint, this heuristic returns 0.
        return sp.Integer(0)
    out_ep = terminals[0]

    # Unstarred faces are those not incident to the chosen outgoing terminal.
    unstarred_faces = [face for face in k.faces if out_ep not in face]

    # Stack holds pairs of (weight, marked_vertices_set)
    stack: deque[tuple[sp.Expr, set]] = deque([(sp.Integer(1), set())])

    for face in unstarred_faces:
        new_stack: deque[tuple[sp.Expr, set]] = deque()
        while stack:
            weight, marked_vertices = stack.pop()
            for ep in face:
                # Mark at most one crossing per face; skip already marked vertices.
                if ep.node not in marked_vertices and isinstance(k.nodes[ep.node], Crossing):
                    is_outgoing = isinstance(ep, OutgoingEndpoint)
                    is_over = bool(ep.position % 2)
                    is_positive = k.nodes[ep.node].sign() > 0

                    if is_outgoing and (not is_over) and is_positive:
                        new_weight = _w
                    elif (not is_outgoing) and is_over and (not is_positive):
                        new_weight = -_w
                    elif is_outgoing and is_over and (not is_positive):
                        new_weight = _w ** (-1)
                    elif (not is_outgoing) and (not is_over) and is_positive:
                        new_weight = -_w ** (-1)
                    else:
                        new_weight = sp.Integer(1)

                    new_stack.append((weight * new_weight, marked_vertices | {ep.node}))
        stack = new_stack

    polynomial = sum(w for w, _ in stack) if stack else sp.Integer(0)
    return sp.expand(polynomial)


if __name__ == "__main__":
    pass

# knotpy/invariants/affine_index.py
"""
Affine index polynomial for knotoids.
"""

__all__ = ["affine_index_polynomial"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import sympy as sp

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import OutgoingEndpoint, IngoingEndpoint
from knotpy.invariants._symbols import _t


def affine_index_polynomial(k: PlanarDiagram | OrientedPlanarDiagram) -> sp.Expr:
    """Compute the affine index polynomial of a **knotoid**.

    The algorithm follows the standard labeling along the open arc starting from the
    outgoing terminal. Crossings receive weights that depend on the traversal label
    and crossing sign; the polynomial is then
    :math:`\\sum_{c \\in \\text{crossings}} \\operatorname{sign}(c) (t^{w(c)} - 1)`.

    Args:
        k: A planar diagram of a knotoid. If not oriented, it will be oriented internally.

    Returns:
        A SymPy expression in the symbol ``t`` representing the affine index polynomial.

    Raises:
        ValueError: If a valid outgoing terminal endpoint of degree 1 cannot be found.

    Examples:
        >>> from knotpy.io import read_pd  # example-only; adjust to your API #TODO: !!!
        >>> K = read_pd("knotoid_example")  # doctest: +SKIP
        >>> affine_index_polynomial(K)      # doctest: +SKIP
        t**2 - 2*t + 1
    """
    k = k if k.is_oriented() else orient(k)

    # Initialize crossing weights with -sign(c): (+1 for negative, -1 for positive)
    weights: dict[Crossing, int] = {cross: -k.nodes[cross].sign() for cross in k.crossings}

    # Find the outgoing terminal of degree 1 and jump over its incident arc.
    terminals = [
        ep for ep in k.endpoints if k.degree(ep.node) == 1 and isinstance(ep, OutgoingEndpoint)
    ]
    if not terminals:
        raise ValueError("No outgoing terminal endpoint of degree 1 found; is this a knotoid?")
    ep = k.twin(terminals[0])  # start just after the outgoing terminal (ingoing endpoint)

    label = 0
    while isinstance(k.nodes[ep.node], Crossing):
        # Counterclockwise adjacent endpoint at this crossing
        ccw_ep = k.endpoint_from_pair((ep.node, (ep.position - 1) % 4))

        # Update crossing weight depending on sign and whether ccw_ep is ingoing
        if (k.nodes[ep.node].sign() > 0) ^ isinstance(ccw_ep, IngoingEndpoint):
            weights[ep.node] += label
        else:
            weights[ep.node] -= label

        # Move across the crossing, then along the arc to the next endpoint
        ep = k.endpoint_from_pair((ep.node, (ep.position + 2) % 4))
        ep = k.twin(ep)

        # Update traversal label
        label += 1 if isinstance(ccw_ep, IngoingEndpoint) else -1

    polynomial = sum(
        k.nodes[c].sign() * (_t ** weights[c] - 1) for c in k.crossings
    )
    return sp.expand(polynomial)


if __name__ == "__main__":
    pass

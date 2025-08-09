# knotpy/invariants/arrow.py
"""
Arrow polynomial for knotoids (per Kauffman et al.).
"""

__all__ = ["arrow_polynomial"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

import sympy as sp
from itertools import product

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.invariants.skein import smoothen_crossing
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.classes.endpoint import OutgoingEndpoint
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.invariants.writhe import writhe
from knotpy.invariants._symbols import _A


def disoriented_smoothing(k: OrientedPlanarDiagram, crossing) -> None:
    """Apply the disoriented smoothing at a crossing.

    Follows Fig. 36 on p.40 of arXiv:1602.03579.

    Args:
        k: Oriented planar diagram to modify in-place.
        crossing: Crossing identifier in ``k``.

    Returns:
        None. The diagram ``k`` is modified in-place.
    """
    node_inst = k.nodes[crossing]
    # If both incident endpoints at positions 0 and 1 have the same type, join (0,1) and (2,3);
    # otherwise join (1,2) and (3,0).
    same_type = node_inst[0].__class__ is node_inst[1].__class__
    pos = 0 if same_type else 1

    node0 = unique_new_node_name(k)
    k.add_vertex(node0, degree=2)
    node1 = unique_new_node_name(k)
    k.add_vertex(node1, degree=2)

    k.set_endpoint((node0, 0), node_inst[pos])
    k.set_endpoint(
        node_inst[pos],
        (node0, 0),
        create_using=type(node_inst[pos]).reverse_type(),
        acute=False,
    )
    k.set_endpoint((node0, 1), node_inst[pos + 1])
    k.set_endpoint(
        node_inst[pos + 1],
        (node0, 1),
        create_using=type(node_inst[pos + 1]).reverse_type(),
        acute=True,
    )

    k.set_endpoint((node1, 0), node_inst[pos + 2])
    k.set_endpoint(
        node_inst[pos + 2],
        (node1, 0),
        create_using=type(node_inst[pos + 2]).reverse_type(),
        acute=False,
    )
    k.set_endpoint((node1, 1), node_inst[(pos + 3) % 4])
    k.set_endpoint(
        node_inst[(pos + 3) % 4],
        (node1, 1),
        create_using=type(node_inst[(pos + 3) % 4]).reverse_type(),
        acute=True,
    )

    k.remove_node(crossing, remove_incident_endpoints=False)


def _components_paths(k: PlanarDiagram):
    """Return (circular_components, long_components) as endpoint paths."""
    long_components = []
    circ_components = []

    available_endpoints = set(k.endpoints)

    # Long components: start from outgoing terminal of degree 1.
    for ep in k.endpoints:
        if k.degree(ep.node) == 1 and isinstance(ep, OutgoingEndpoint):
            path = []
            while True:
                path.append(ep)
                ep = k.twin(ep)
                path.append(ep)
                if k.degree(ep.node) == 1:
                    break
                ep = k.endpoint_from_pair((ep.node, (ep.position + 1) % 2))
            long_components.append(path)
            available_endpoints = available_endpoints.difference(path)

    # Circular components: consume remaining endpoints by walking cycles.
    while available_endpoints:
        path = []
        ep = next(iter(available_endpoints))
        while ep in available_endpoints:
            path.append(ep)
            available_endpoints.remove(ep)
            ep = k.twin(ep)
            path.append(ep)
            available_endpoints.remove(ep)
            ep = k.endpoint_from_pair((ep.node, (ep.position + 1) % 2))
        circ_components.append(path)

    return circ_components, long_components


def _remove_consecutive_cusps(k: PlanarDiagram) -> None:
    """Reduce consecutive acute–obtuse cusp pairs along arcs, in-place."""
    # Brute loop until no reductions are made.
    reductions_were_made = True
    while reductions_were_made:
        reductions_were_made = False
        nodes = list(k.vertices)
        for node in nodes:
            for pos in (0, 1):
                if node in k.nodes and k.degree(node) == 2:
                    ep = k.endpoint_from_pair((node, pos))  # endpoint in the "valley"
                    twin = k.twin(ep)  # the other endpoint in the "valley"
                    adj_node = twin.node  # potential paired degree-2 node
                    if k.degree(adj_node) != 2:  # skip terminals
                        break
                    if ep["acute"] != twin["acute"]:
                        # Remove opposite-acuteness consecutive cusps.
                        ep0 = k.nodes[node][(pos + 1) % 2]
                        ep1 = k.nodes[twin.node][(twin.position + 1) % 2]

                        if ep0.node == adj_node and ep1.node == node:
                            add_unknot(k)

                        k.set_endpoint(ep0, ep1, type(ep1), acute=ep1["acute"])
                        k.set_endpoint(ep1, ep0, type(ep0), acute=ep0["acute"])
                        k.remove_node(node, remove_incident_endpoints=False)
                        k.remove_node(adj_node, remove_incident_endpoints=False)
                        reductions_were_made = True


def _generator_to_variables(k: PlanarDiagram) -> sp.Expr:
    """Return the monomial in K_i/L_j variables for a reduced diagram.

    The reduced diagram (no consecutive acute cusps) contributes factors:
    - For circular components: ``K_{len/4}`` unless the component is a trivial 2-endpoint loop,
      in which case it contributes the Kauffman bracket term ``-A^2 - A^{-2}``.
    - For long components: ``L_{(len-2)/4}`` unless trivial (length 2), contributing ``1``.

    Args:
        k: Reduced (by cusp removal) planar diagram.

    Returns:
        SymPy expression in ``_A`` and formal variables ``K*``, ``L*``.
    """
    polynomial = sp.Integer(1)
    kaufman_term = (-_A**2 - _A ** (-2))

    circ_comp, line_comp = _components_paths(k)

    for c in circ_comp:
        polynomial *= kaufman_term if len(c) == 2 else sp.symbols(f"K{len(c) // 4}")
    for c in line_comp:
        polynomial *= 1 if len(c) == 2 else sp.symbols(f"L{(len(c) - 2) // 4}")

    return polynomial


def arrow_polynomial(
    k: PlanarDiagram | OrientedPlanarDiagram,
    normalize: bool = True,
) -> sp.Expr:
    """Compute the arrow polynomial of a knotoid (arXiv:1602.03579).

    Args:
        k: Planar diagram of a knotoid. If not oriented, it will be oriented internally.
        normalize: If True, multiply by ``(-A^3)^(-writhe)`` to ignore framing.

    Returns:
        A SymPy expression in ``A`` and formal variables ``K_i, L_j``.

    Notes:
        The state sum expands over oriented/disoriented smoothings. After smoothing, consecutive
        opposite-acuteness cusps are reduced; each component contributes a factor as described in
        :func:`_generator_to_variables`.
    """
    polynomial = sp.Integer(0)

    original_knot = k if k.is_oriented() else orient(k)
    crossings = tuple(original_knot.crossings)

    # State expansions over all crossings.
    for state in product((1, -1), repeat=len(crossings)):
        k = original_knot.copy()
        for method, node in zip(state, crossings):
            if (method > 0) ^ (k.nodes[node].sign() < 0):  # "A" oriented smoothing
                smoothen_crossing(k, crossing_for_smoothing=node, method="O", inplace=True)
            else:  # "B" disoriented smoothing
                disoriented_smoothing(k, node)

        _remove_consecutive_cusps(k)
        polynomial += _A ** sum(state) * _generator_to_variables(k)

    factor = (-_A**3) ** (-writhe(original_knot) if normalize else -original_knot.framing)
    polynomial *= factor

    return sp.expand(polynomial)


if __name__ == "__main__":
    pass

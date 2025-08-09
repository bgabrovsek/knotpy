# knotpy/invariants/yamada.py
"""
Compute the Yamada polynomial of a knotted planar diagram described in
[Yamada, S. (1989). An invariant of spatial graphs. Journal of Graph Theory, 13(5), 537-551].

Optimizations:
* precomputed powers of sigma = A + 1 + 1/A,
* simplification of the knotted graphs mid-computation (reducing crossings via R1 unkinks and R2 unpokes,...)
* caching of the Yamada polynomials for planar graphs,
* caching of the Yamada polynomials for knotted graphs.
"""

from __future__ import annotations

__all__ = ["yamada"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque
import sympy as sp

from knotpy.algorithms.canonical import canonical
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import unorient
from knotpy.invariants.skein import smoothen_crossing, crossing_to_vertex
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.algorithms.topology import bridges, loops
from knotpy.algorithms.remove import remove_arc, remove_bivalent_vertices
from knotpy.algorithms.contract import contract_arc
from knotpy.utils.cache import Cache
from knotpy._settings import settings
from knotpy.classes.freezing import freeze
from knotpy.invariants._symbols import _A, _YAMADA_SIGMA

# Yamada settings
_YAMADA_KNOTTED_CACHE = True
_YAMADA_GRAPH_CACHE = True
_YAMADA_SIMPLIFY = True  # simplify the diagrams during computation

_sigma_power = [sp.Integer(1)]  # dynamically expanded: [σ^0, σ^1, σ^2, ...]

# The global cache storing precomputed Yamada polynomials of planar graphs (≈7KB per diagram).
# 'max_key_length' limits the number of vertices for caching.
_yamada_graph_cache = Cache(max_cache_size=10000, max_key_length=6)

# The global cache storing precomputed Yamada polynomials of knotted graphs (≈7KB per diagram).
# 'max_key_length' limits the number of vertices for caching.
_yamada_knotted_cache = Cache(max_cache_size=1000, max_key_length=5)


def yamada(k: PlanarDiagram, normalize: bool = True) -> sp.Expr:
    """Return the Yamada polynomial of a given planar diagram.

    Args:
        k: Planar diagram (knotted spatial graph allowed).
        normalize: If True, multiply by a power of ``(-A)`` so the lowest term is constant.

    Returns:
        SymPy expression for the Yamada polynomial.
    """
    global _sigma_power

    # Adjust settings needed for the correct computation of the Yamada polynomial.
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    # Extend the sigma lookup table up to number of arcs (safe upper bound).
    _sigma_power.extend([sp.expand(_YAMADA_SIGMA ** i) for i in range(len(_sigma_power), len(k.arcs) + 1)])

    # Initialize the input diagram (unoriented for Yamada).
    if k.is_oriented():
        k = unorient(k)

    # Compute the unnormalized Yamada polynomial.
    polynomial = _compute_yamada(k)

    if normalize:
        # Normalize so the lowest A-exponent term becomes constant (handles R1/R4 framing effects).
        lowest = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = sp.expand(polynomial * (-_A) ** (-lowest))

    settings.load(settings_dump)
    return polynomial


def _compute_yamada(k: PlanarDiagram, first_pass_use_cache: bool = True) -> sp.Expr:
    """Compute the (unnormalized) Yamada polynomial by a state sum and graph evaluations."""
    # Initialize the diagram.
    k = k.copy()
    k.attr["_A"], k.attr["_B"], k.attr["_X"], k.attr["framing"] = 0, 0, 0, 0
    k.attr["_loops"], k.attr["_isolated_vertices"] = 0, 0

    polynomial = sp.Integer(0)

    # Phase 1: resolve the crossings (state sum).
    stack: deque[PlanarDiagram] = deque([k])
    graphs: list[PlanarDiagram] = []  # resulting planar graphs (states without crossings)

    while stack:
        k = stack.pop()

        if _YAMADA_SIMPLIFY:
            k = simplify_decreasing(k, inplace=True)

        if k.crossings:
            if _YAMADA_KNOTTED_CACHE and first_pass_use_cache and len(k) <= _yamada_knotted_cache.max_key_length:
                polynomial += _yamada_knotted_from_cache(k)
                first_pass_use_cache = True
                continue
            first_pass_use_cache = True

            crossing = next(iter(k.crossings))
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A", inplace=False)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B", inplace=False)
            kX = crossing_to_vertex(k, crossing=crossing, inplace=False)
            kA.attr["_A"] = k.attr["_A"] + 1
            kB.attr["_B"] = k.attr["_B"] + 1
            kX.attr["_X"] = k.attr["_X"] + 1
            stack.extend([kA, kB, kX])
        else:
            graphs.append(k)

    # Phase 2: evaluate planar graphs (no crossings).
    polynomial += sum(_yamada_graph(g) for g in graphs)

    return sp.expand(polynomial)


def _yamada_graph(g: PlanarDiagram) -> sp.Expr:
    """Compute the Yamada polynomial of a planar graph (without crossings).

    Warning:
        Modifies ``g`` in-place during evaluation.
    """
    g.attr["_A"] = g.attr.get("_A", 0)
    g.attr["_B"] = g.attr.get("_B", 0)
    g.attr["_X"] = g.attr.get("_X", 0)
    g.attr["_loops"] = g.attr.get("_loops", 0)
    g.attr["_isolated_vertices"] = g.attr.get("_isolated_vertices", 0)
    g.attr["framing"] = g.attr.get("framing", 0) or 0

    stack: deque[PlanarDiagram] = deque([g])
    polynomial = sp.Integer(0)

    while stack:
        g = stack.pop()
        _remove_loops_isolated_and_bivalent_vertices(g)

        if bridges(g):
            continue  # graphs with bridges evaluate to 0

        # contraction-deletion on a remaining edge
        arc = next(iter(g.arcs), None)
        if arc is not None:
            if _YAMADA_GRAPH_CACHE and len(g) <= _yamada_graph_cache.max_key_length:
                polynomial += _yamada_graph_from_cache(g)
            else:
                g_delete = remove_arc(g, arc_for_removing=arc, inplace=False)
                g_contract = contract_arc(g, arc_for_contracting=arc, inplace=False)
                stack.extend([g_delete, g_contract])
        else:
            # Only isolated vertices and loops remain (final state).
            polynomial += (
                (-1 if (g.attr["_isolated_vertices"] + g.attr["_loops"]) % 2 else 1)
                * _sigma_power[g.attr["_loops"]]
                * _A ** (g.attr["_A"] - g.attr["_B"])
                * (-_A) ** int(-2 * g.framing)
            )

    return polynomial


def _yamada_knotted_from_cache(k: PlanarDiagram) -> sp.Expr:
    """Retrieve or compute the Yamada polynomial for a knotted graph from cache."""
    global _yamada_knotted_cache
    attr = k.attr
    k = canonical(k)
    k.attr = {}

    polynomial = _yamada_knotted_cache.get(k, None)
    if polynomial is None:
        _yamada_knotted_cache[freeze(k)] = polynomial = _compute_yamada(k, first_pass_use_cache=False)

    polynomial *= (
        (-1 if (attr["_isolated_vertices"] + attr["_loops"]) % 2 else 1)
        * _sigma_power[attr["_loops"]]
        * _A ** (attr["_A"] - attr["_B"])
        * (-_A) ** int(-2 * attr["framing"])
    )
    return polynomial


def _yamada_graph_from_cache(g: PlanarDiagram) -> sp.Expr:
    """Retrieve or compute the Yamada polynomial for a planar graph from cache.

    Warning:
        Modifies ``g`` in-place during evaluation.
    """
    global _yamada_graph_cache

    attr = g.attr
    g = canonical(g)  # makes a copy
    g.attr = {}

    polynomial = _yamada_graph_cache.get(g, None)
    if polynomial is None:
        arc = next(iter(g.arcs))
        _yamada_graph_cache[freeze(g)] = polynomial = (
            _yamada_graph(remove_arc(g, arc_for_removing=arc, inplace=False))
            + _yamada_graph(contract_arc(g, arc_for_contracting=arc, inplace=False))
        )

    polynomial *= (
        (-1 if (attr["_isolated_vertices"] + attr["_loops"]) % 2 else 1)
        * _sigma_power[attr["_loops"]]
        * _A ** (attr["_A"] - attr["_B"])
        * (-_A) ** int(-2 * attr["framing"])
    )

    return sp.expand(polynomial)


def _remove_loops_isolated_and_bivalent_vertices(g: PlanarDiagram) -> None:
    """Remove all loops and isolated vertices (and bivalent vertices) in-place, updating counters."""
    remove_bivalent_vertices(g)

    while (L := loops(g)):
        remove_arc(g, arc_for_removing=L[0], inplace=True)
        g.attr["_loops"] += 1

    for v in [v for v in g.vertices if g.degree(v) == 0]:
        g.remove_node(v, remove_incident_endpoints=False)
        g.attr["_isolated_vertices"] += 1


def _print_cache() -> None:
    import sys

    print("Knotted cache size:", len(_yamada_knotted_cache), "items", f"({sys.getsizeof(_yamada_knotted_cache)/1024} KB)")
    for k in sorted(_yamada_knotted_cache)[:25]:
        print("  ", k)

    print("  Graph cache size:", len(_yamada_graph_cache), "items", f"({sys.getsizeof(_yamada_graph_cache) / 1024} KB)")
    for k in sorted(_yamada_graph_cache)[:25]:
        print("  ", k)


# Naive recursive Yamada implementation for testing purposes

def _yamada_rec(k: PlanarDiagram) -> sp.Expr:
    # basic recursive yamada for testing purposes

    if k.crossings:
        crossing = next(iter(k.crossings))
        return (
            _A * _yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="A"))
            + (_A ** -1) * _yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="B"))
            + _yamada_rec(crossing_to_vertex(k, crossing=crossing))
        )

    if bridges(k):
        return sp.Integer(0)

    if L := loops(k):
        return -(_A + sp.Integer(1) + _A ** -1) * _yamada_rec(remove_arc(k, arc_for_removing=L[0], inplace=False))

    if vs := [v for v in k.vertices if k.degree(v) == 0]:
        return sp.Integer(-1) * _yamada_rec(k.copy().remove_node(vs[0], remove_incident_endpoints=False))

    if (arc := next(iter(k.arcs), None)) is not None:
        return _yamada_rec(remove_arc(k, arc_for_removing=arc, inplace=False)) + _yamada_rec(
            contract_arc(k, arc_for_contracting=arc, inplace=False)
        )

    if len(k) == 0:
        return sp.Integer(1)

    # Fallback (should not happen)
    return sp.Integer(0)


def _naive_yamada_polynomial(k: PlanarDiagram, normalize: bool = True) -> sp.Expr:
    polynomial = sp.expand(_yamada_rec(k.copy()))
    if normalize:
        lowest_exponent = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = sp.expand(polynomial * (-_A) ** (-lowest_exponent))
    return polynomial

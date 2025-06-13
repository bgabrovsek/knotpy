"""
Compute the Yamada polynomial of a knotted planar diagram described in
[Yamada, S. (1989). An invariant of spatial graphs. Journal of Graph Theory, 13(5), 537-551].

Optimizations:
* precomputed powers of sigma = A + 1 + 1/A,
* simplification of the knotted graphs mid-computation (reducing crossings via R1 unkinks and R2 unpokes,...)
* caching of the Yamada polynomials for planar graphs,
* caching of the Yamada polynomials for knotted graphs.
"""

__all__ = ['yamada_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import expand, Integer, symbols, Expr
from collections import deque

from knotpy import canonical, sanity_check
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import unorient
from knotpy.algorithms.skein import smoothen_crossing, crossing_to_vertex
from knotpy.reidemeister.simplify import simplify_greedy_decreasing
from knotpy.algorithms.topology import bridges, loops
from knotpy.manipulation.remove import remove_arc, remove_bivalent_vertices
from knotpy.manipulation.contract import contract_arc
from knotpy.utils.cache import Cache
from knotpy._settings import settings
from knotpy.classes.freezing import freeze
# Yamada settings
_YAMADA_KNOTTED_CACHE = True
_YAMADA_GRAPH_CACHE = True
_YAMADA_SIMPLIFY = True  # simplify the diagrams during computation

_A = symbols("A")
# Precompute powers of A + 1 + 1/A.
_sigma = _A + 1 + _A ** (-1)
_sigma_power = [Integer(1)]  # this will dynamically expend to consist of [σ^0, σ^1, σ^2, σ^3, ...]

"""
The global cache storing precomputed Yamada polynomials of planar graphs without crossings (approx. 7KB per diagram).
The 'max_key_length' argument limits the number of vertices a graph should have to be stored in the cache,
"""
_yamada_graph_cache = Cache(max_cache_size=10000, max_key_length=6)  # stores the pre-computed yamada of the planar graphs
"""
The global cache storing precomputed Yamada polynomials of knotted graphs (approx. 7KB per diagram).
The 'max_key_length' argument limits the number of vertices a graph should have to be stored in the cache,
"""
_yamada_knotted_cache = Cache(max_cache_size=1000, max_key_length=5)  # stores pre-computed yamada polynomials for the knotted graphs


def yamada_polynomial(k: PlanarDiagram, normalize=True) -> Expr:
    """Return the value of the Yamada polynomial of a given planar diagram."""
    global _sigma, _sigma_power

    # adjust global settings needed for the correct computation of the Yamada polynomial
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    # Extend the sigma lookup table to the number of arcs, just to be safe.
    _sigma_power.extend([expand(_sigma**_) for _ in range(len(_sigma_power), len(k.arcs) + 1)])  # should we extend to the number of faces - 1?

    # Initialize the input diagram.
    if k.is_oriented():
        k = unorient(k)

    # Compute the unnormalized Yamada polynomial
    polynomial = _compute_yamada(k)

    if normalize:
        # Normalize by multiplying by (-A)^n, so that the lowest term of the polynomial a constant term (this translates to applying R1 moves or R4 twists).
        polynomial = expand(polynomial * (-_A) ** (-min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())))

    settings.load(settings_dump)

    return polynomial


def _compute_yamada(k: PlanarDiagram, first_pass_use_cache=True) -> Expr:

    # TODO: test if removing loops in compute yamada increases speed

    # Initialize the diagram.
    k = k.copy()
    k.attr["_A"], k.attr["_B"], k.attr["_X"], k.attr["framing"] = 0, 0, 0, 0
    k.attr["_loops"], k.attr["_isolated_vertices"] = 0, 0

    polynomial = Integer(0)  # store the Yamada here

    # Phase 1: resolve the crossings (compute the state sum)
    stack = deque([k])  # use a stack to simulate recursive calls for the smoothened states, add the initial diagram to the stack
    graphs = []  # here we store the resulting planar graphs without crossings (so-called "states")

    while stack:
        k = stack.pop()

        if _YAMADA_SIMPLIFY:
            k = simplify_greedy_decreasing(k, inplace=True)

        # resolve a crossing
        if k.crossings:

            if _YAMADA_KNOTTED_CACHE and first_pass_use_cache and len(k) <= _yamada_knotted_cache.max_key_length:
                polynomial += _yamada_knotted_from_cache(k)
                first_pass_use_cache = True
                continue
            first_pass_use_cache = True

            crossing = next(iter(k.crossings))  # pop a crossing to smoothen
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A", inplace=False)
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B", inplace=False)
            kX = crossing_to_vertex(k, crossing=crossing, inplace=False)
            kA.attr["_A"] = k.attr["_A"] + 1
            kB.attr["_B"] = k.attr["_B"] + 1
            kX.attr["_X"] = k.attr["_X"] + 1
            stack.extend([kA, kB, kX])  # push partial states to the stack
        else:
            graphs.append(k)  # if there are no crossings, push it to the resulting states

    # Phase 2: compute the Yamada polynomial of diagrams without crossings
    polynomial += sum(_yamada_graph(g) for g in graphs)

    return expand(polynomial)


def _yamada_graph(g: PlanarDiagram) -> Expr:
    """Compute the Yamada polynomial of a given graph (without crossings)."""
    # WARNING: g is modified

    g.attr["_A"] = g.attr.get("_A",0)
    g.attr["_B"] = g.attr.get("_B",0)
    g.attr["_X"] = g.attr.get("_X",0)
    g.attr["_loops"] = g.attr.get("_loops", 0)
    g.attr["_isolated_vertices"] = g.attr.get("_isolated_vertices", 0)
    g.attr["framing"] = g.attr.get("framing", 0) or 0

    stack = deque([g])
    polynomial = Integer(0)

    while stack:

        g = stack.pop()
        _remove_loops_isolated_and_bivalent_vertices(g)  # clean up the graph

        if bridges(g):
            continue  # ignore graphs with bridges (evaluate to 0)


        # contraction-deletion of "normal" edges
        if (arc := next(iter(g.arcs), None)) is not None:

            # Try to obtain precomputed Yamada of the graph from the cache.
            if _YAMADA_GRAPH_CACHE and len(g) <= _yamada_graph_cache.max_key_length:
                polynomial += _yamada_graph_from_cache(g)
            else:
                # We found a non-trivial edge
                g_delete = remove_arc(g, arc_for_removing=arc, inplace=False)
                # sanity_check(g_delete)
                g_contract = contract_arc(g, arc_for_contracting=arc, inplace=False)
                # sanity_check(g_contract)
                stack.extend([g_delete, g_contract])
        else:
            # Evaluate the final state (graphs that consist only of isolated vertices and loops).
            polynomial += (-1 if (g.attr["_isolated_vertices"] + g.attr["_loops"]) % 2 else 1) \
                          * _sigma_power[g.attr["_loops"]] \
                          * _A ** (g.attr["_A"] - g.attr["_B"]) * (-_A) ** int(- 2 * g.framing)

    return polynomial

def _yamada_knotted_from_cache(k: PlanarDiagram) -> Expr:
    global _yamada_knotted_cache
    attr = k.attr
    k = canonical(k)
    k.attr = {}

    if (polynomial := _yamada_knotted_cache.get(k, None)) is None:
        # k not in cache
        _yamada_knotted_cache[freeze(k)] = polynomial = _compute_yamada(k, first_pass_use_cache=False)

    polynomial *= (-1 if (attr["_isolated_vertices"] + attr["_loops"]) % 2 else 1) \
                  * _sigma_power[attr["_loops"]] \
                  * _A ** (attr["_A"] - attr["_B"]) * (-_A) ** int(- 2 * attr["framing"])
    return polynomial


def _yamada_graph_from_cache(g: PlanarDiagram) -> Expr:
    """Try to retrieve the Yamada polynomial for a knotted graph from a cache, otherwise compute it recursively."""
    # WARNING: This function modifies g
    global _yamada_graph_cache

    attr = g.attr  # save the attributes
    g = canonical(g) # makes a copy
    g.attr = {}

    if (polynomial := _yamada_graph_cache.get(g, None)) is None:
        # g is not in the cache
        arc = next(iter(g.arcs))
        # make a copy, since g is modified
        _yamada_graph_cache[freeze(g)] = polynomial \
            = _yamada_graph(remove_arc(g, arc_for_removing=arc, inplace=False)) \
            + _yamada_graph(contract_arc(g, arc_for_contracting=arc, inplace=False))

    polynomial *= (-1 if (attr["_isolated_vertices"] + attr["_loops"]) % 2 else 1) \
                  * _sigma_power[attr["_loops"]] \
                  * _A ** (attr["_A"] - attr["_B"]) * (-_A) ** int(- 2 * attr["framing"])

    return expand(polynomial)

def _remove_loops_isolated_and_bivalent_vertices(g:PlanarDiagram):
    """
    Remove all loops and isolated vertices in a given planar graph inplace.
    This method serves for faster cache usage, since computing isolated vertices
    and loops is relative simple, so we can cache more elements if we remove them.

    The number of removed loops is stored in the diagram's attribute `_loops`
    and the number of removed isolated vertices is stored in the attribute
    `_isolated_vertices`. It does not put the diagram in the canonical form.

    Args:
        g (PlanarDiagram): The input planar graph where loops are to be removed.
    """
    remove_bivalent_vertices(g)

    while L := loops(g):
        remove_arc(g, arc_for_removing=L[0], inplace=True)
        g.attr["_loops"] += 1

    for v in [v for v in g.vertices if g.degree(v) == 0]:
        g.remove_node(v, remove_incident_endpoints=False)
        g.attr["_isolated_vertices"] += 1

def _print_cache():
    import sys
    print("Knotted cache size:", len(_yamada_knotted_cache), "items", f"({sys.getsizeof(_yamada_knotted_cache)/1024} KB)")
    for k in sorted(_yamada_knotted_cache)[:25]:
        print("  ",k)

    print("  Graph cache size:", len(_yamada_graph_cache), "items", f"({sys.getsizeof(_yamada_graph_cache) / 1024} KB)")
    for k in sorted(_yamada_graph_cache)[:25]:
        print("  ", k)


# Naive recursive Yamada implementation for testing purposes

def _yamada_rec(k: PlanarDiagram):
    # basic recursive yamada for testing purposes

    # we have a crossing
    if k.crossings:
        crossing = next(iter(k.crossings))
        return (_A * _yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")) +
                (_A ** -1) * _yamada_rec(smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")) +
                _yamada_rec(crossing_to_vertex(k, crossing=crossing)))

    # we have a bridge
    if bridges(k):
        return Integer(0)

    # we have a loop
    if L := loops(k):
        return -(_A + Integer(1) + _A**-1) *  _yamada_rec(remove_arc(k, arc_for_removing=L[0], inplace=False))

    # we have an isolated vertex
    if vs := [v for v in k.vertices if k.degree(v) == 0]:
        return Integer(-1) * _yamada_rec(k.copy().remove_node(vs[0], remove_incident_endpoints=False))

    # we have a normal edge
    if (arc := next(iter(k.arcs), None)) is not None:
        return _yamada_rec(remove_arc(k, arc_for_removing=arc, inplace=False)) + _yamada_rec(contract_arc(k, arc_for_contracting=arc, inplace=False))

    # empty graph
    if len(k) == 0:
        return Integer(1)

def _naive_yamada_polynomial(k: PlanarDiagram, normalize=True):
    polynomial = expand(_yamada_rec(k.copy()))

    if normalize:
        lowest_exponent = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = expand(polynomial * (-_A) ** (-lowest_exponent))
    return polynomial
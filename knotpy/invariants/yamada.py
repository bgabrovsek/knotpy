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

from knotpy import canonical
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import unorient
from knotpy.algorithms.skein import smoothen_crossing, crossing_to_vertex
from knotpy.reidemeister.simplify import simplify_crossing_reducing
from knotpy.algorithms.topology import bridges, loops
from knotpy.manipulation.remove import remove_arc, remove_bivalent_vertices
from knotpy.manipulation.contract import contract_arc
from knotpy.utils.cache import Cache
from knotpy._settings import settings
from knotpy.notation import from_knotpy_notation

# TODO: Implement that the framing/A/B/X markers are kept in _yamada_from_cache (simplify code)
# TODO: Do not perform crossing smoothings and deletion-contraction in the caching function (simplify code)

# Yamada settings
_YAMADA_USE_CACHE = True
_YAMADA_SIMPLIFY = True

# Precompute powers of A + 1 + 1/A.
_A = symbols("A")
_sigma = _A + 1 + _A ** (-1)
_sigma_power = [Integer(1)]  # this will dynamically expend to consist of [σ^0, σ^1, σ^2, σ^3, ...]


"""
The global cache storing precomputed Yamada polynomials of planar graphs without crossings (approx. 7KB per diagram).
The 'max_key_length' argument limits the number of vertices a graph should have to be stored in the cache,
"""
_yamada_planar_graph_cache = Cache(max_cache_size=1000, max_key_length=6)  # stores the pre-computed yamada of the planar graphs

"""
The global cache storing precomputed Yamada polynomials of knotted graphs (approx. 7KB per diagram).
The 'max_key_length' argument limits the number of vertices a graph should have to be stored in the cache,
"""
_yamada_cache = Cache(max_cache_size=1000, max_key_length=5)  # stores pre-computed yamada polynomials for the knotted graphs


def _yamada_from_cache(k: PlanarDiagram) -> Expr:
    """
    Try to retrieve the Yamada polynomial for a knotted graph from a cache, otherwise compute it recursively.

    Args:
        k (PlanarDiagram): The planar diagram for which the Yamada polynomial is returned.

    Returns:
        sympy.Expr: The Yamada polynomial of the knotted graph 'k'.
    """
    global _yamada_cache

    # The coefficient from the A/B smoothing states of the input diagram already performed.
    coefficient = _A ** (k.attr["_A"] - k.attr["_B"]) * (-_A) ** int(- 2 * k.framing)
    k = canonical(k)

    # Clear the attributes, since we do not store them in knots in the cache.
    k.framing = 0
    k.attr["_A"] = k.attr["_B"] = k.attr["_X"] = 0

    # Obtain the polynomial from the cache or compute it and store it to the cache.
    if k in _yamada_cache:
        polynomial = _yamada_cache[k]
    else:
        polynomial = _compute_yamada_unnormalized(k, first_pass_use_cache=False)
        _yamada_cache[k] = polynomial

    return polynomial * coefficient  # adjust the framing and A/B coefficients of the input graph


def _state_sum_yamada(k: PlanarDiagram, first_pass_use_cache=True):
    """
    Calculate the Yamada polynomial states of a planar diagram by iteratively applying smoothing operations
    (remove crossings via A/B/X states) on crossings and reducing the diagram step by step.
    Each state in the result is represented as a reduced diagram without crossings.

    Args:
        k (PlanarDiagram): The initial planar diagram for which the Yamada polynomial
            states are to be calculated.

    Returns:
        list: A list of diagrams (states) obtained after all crossings have been
            resolved through the application of specific Yamada smoothing methods.
    """

    # Store in diagram's attributes the number of A/B/X smoothings performed.
    k.attr["_A"] = 0
    k.attr["_B"] = 0
    k.attr["_X"] = 0

    stack = deque([k])  # use a stack to simulate recursive calls for the smoothened states, add the initial diagram to the stack
    states = []  # here we store the resulting planar graphs without crossings (so-called "states")
    other_polynomials = []  # here we store other polynomials computed from cache

    while stack:
        k = stack.pop()
        if _YAMADA_SIMPLIFY:
            k = simplify_crossing_reducing(k, inplace=True)

        if k.crossings:

            # For small diagrams, get the value form cache.
            if _YAMADA_USE_CACHE and first_pass_use_cache and len(k) <= _yamada_cache.max_key_length:
                other_polynomials.append(_yamada_from_cache(k))
                continue
            first_pass_use_cache = True  # on every other pass, we can use cache

            crossing = next(iter(k.crossings))  # pop a crossing to smoothen
            kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")
            kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")
            kX = crossing_to_vertex(k, crossing=crossing)

            kA.attr["_A"] = k.attr["_A"] + 1
            kB.attr["_B"] = k.attr["_B"] + 1
            kX.attr["_X"] = k.attr["_X"] + 1

            stack.extend([kA, kB, kX])
        else:
            states.append(k)  # if there are no crossings, push it to the resulting states

    return states, other_polynomials


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

    if "_loops" not in g.attr:
        g.attr["_loops"] = 0
    if "_isolated_vertices" not in g.attr:
        g.attr["_isolated_vertices"] = 0

    remove_bivalent_vertices(g)

    while L := loops(g):
        remove_arc(g, arc_for_removing=L[0], inplace=True)
        g.attr["_loops"] += 1

    for v in [v for v in g.vertices if g.degree(v) == 0]:
        g.remove_node(v, remove_incident_endpoints=False)
        g.attr["_isolated_vertices"] += 1



def _yamada_planar_graph_from_cache(g: PlanarDiagram) -> Expr:
    """
    Try to retrieve the Yamada polynomial for a planar graph from a cache. If the
    polynomial is not found in the cache, compute it recursively using the
    deletion-contraction algorithm.

    Args:
        g (PlanarDiagram): The planar graph diagram for which the Yamada polynomial is returned.

    Returns:
        sympy.Expr: The Yamada polynomial of the graph 'g'.
    """
    global _yamada_planar_graph_cache

    number_isolated_vertices = g.attr.get("_isolated_vertices", 0)
    number_loops = g.attr.get("_loops", 0)

    g = canonical(g)
    g.attr.clear()



    if g in _yamada_planar_graph_cache:
        polynomial = _yamada_planar_graph_cache[g]
    else:
        # If the Yamada is not in the cache, compute it by the deletion-contraction operation.
        polynomial = _yamada_graph(g, first_pass_use_cache=False)
        _yamada_planar_graph_cache[g] = polynomial


    polynomial *= (-1 if (number_isolated_vertices + number_loops) % 2 else 1) * _sigma_power[number_loops]
    return polynomial


def _yamada_graph(g: PlanarDiagram, first_pass_use_cache=True) -> Expr:
    """
    Evaluate the Yamada polynomial of a planar graph without crossings.

    Args:
        g (PlanarDiagram): The input planar graph diagram.

    Returns:
        Expr: The computed Yamada polynomial of the graph 'g'.
    """
    # clear attributes
    g.attr = {"_loops": g.attr.get("_loops", 0), "_isolated_vertices": g.attr.get("_isolated_vertices", 0)}

    polynomial = Integer(0)  # store the main result (the Yamada polynomial)

    stack = deque([g])

    while stack:
        g = stack.pop()
        _remove_loops_isolated_and_bivalent_vertices(g)

        # If there is a bridge, just ignore it (this effectively evaluates it to 0).
        if bridges(g):
            continue

        if (arc := next(iter(g.arcs), None)) is not None:
            # We found a non-trivial edge

            if _YAMADA_USE_CACHE and first_pass_use_cache and len(g) <= _yamada_planar_graph_cache.max_key_length :
                polynomial += _yamada_planar_graph_from_cache(g)
            else:
                first_pass_use_cache = True

                k_delete = remove_arc(g, arc_for_removing=arc, inplace=False)
                k_contract = contract_arc(g, arc_for_contracting=arc, inplace=False)


                stack.append(k_delete)
                stack.append(k_contract)
        else:
            # The graph consist only of isolated vertices and loops.
            polynomial += (-1 if (g.attr["_isolated_vertices"] + g.attr["_loops"]) % 2 else 1) * _sigma_power[g.attr["_loops"]]

        #
        # # For small diagrams, get the value form cache.
        # if _YAMADA_USE_CACHE and first_pass_use_cache and len(g) <= _yamada_planar_graph_cache.max_key_length:
        #     polynomial += _yamada_planar_graph_from_cache(g)
        #     continue
        # first_pass_use_cache = True
        #
        # has_regular_arcs = False
        #
        # # Loop through all the arcs, by the nature of the algorithm, there should be no loops or bridges.
        # for arc in g.arcs:
        #
        #     break

        # Evaluate the result if there was no deletion-contraction operation made (i.e. only loops and bridges exist).
        #if not has_regular_arcs:


    return expand(polynomial)


def _compute_yamada_unnormalized(k: PlanarDiagram, first_pass_use_cache=True):
    """
    Actually compute the unnormalized Yamada polynomial of a given planar diagram.
    """
    # Phase 1: Resolve (smoothen) all crossings.
    no_crossing_states, other_polynomials = _state_sum_yamada(k, first_pass_use_cache)

    # Phase 2: Use deletion-contraction operations all non-loops and non-bridges (i.e. regular arcs)
    # Warning: we must fist get g.attr, since _evaluate_yamada removes the attributes (TODO: maybe fix this?)
    polynomial = sum(_A ** (g.attr["_A"] - g.attr["_B"]) * (-_A) ** int(- 2 * g.framing) * _yamada_graph(g) for g in no_crossing_states)
    polynomial += sum(other_polynomials)
    return expand(polynomial)


def yamada_polynomial(k: PlanarDiagram, normalize=True):
    """
    Computes the Yamada polynomial of a given planar diagram using the skein relation and the contraction-deletion
    operation as defined in
    [Yamada, S. (1989). An invariant of spatial graphs. Journal of Graph Theory, 13(5), 537-551].

    Args:
        k (PlanarDiagram): The input planar diagram representation
        normalize (bool, optional): Indicates whether to normalize the computed polynomial
            by shifting the lowest degree term to ensure consistent representation.
            Defaults to True.

    Returns:
        sympy.Expr: The expanded polynomial expression representing the Yamada polynomial
        of the input diagram.

    Raises:
        ValueError: If the deletion-contraction process results in mismatched loop
            and arc counts, which violates the consistency of the diagram's graphical
            properties.

    """

    # Do not allow R5 moves in general when simplifying yamada states, Yamada needs different settings than the global diagram
    settings_dump = settings.dump()
    settings.update({"trace_moves": False, "r5_only_trivalent": True, "framed": True})

    # Extend the sigma lookup table to the number of arcs, just to be safe.
    global _sigma, _sigma_power
    _sigma_power.extend([expand(_sigma**_) for _ in range(len(_sigma_power), len(k.arcs) + 1)])  # should we extend to the number of faces - 1?

    # Initialize the input diagram.
    k = unorient(k) if k.is_oriented() else k.copy()

    if "framing" not in k.attr:
        k.framing = 0  # framing not yet supported

    # Actually compute the Yamada polynomial.
    polynomial = _compute_yamada_unnormalized(k)

    if normalize:
        # Normalize by multiplying by A^(2n) * (-A^m), so that the lowest term of the polynomial is 1 (constant) or A.
        # This normalization translates to adding some framing (R1 move) or twist at the vertex (R4 move).
        lowest_exponent = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = expand(polynomial * (-_A) ** (-lowest_exponent))

    settings.load(settings_dump)

    return polynomial



if __name__ == "__main__":

    k = from_knotpy_notation("a → V(b0 b2 b1), b → V(a0 a2 a1)")
    print(k)
    print(yamada_polynomial(k))

    k = from_knotpy_notation("a → V(b0 b1), b → V(a0 a1)")
    print(yamada_polynomial(k))

    k = from_knotpy_notation("a → V(b0 c0 d0), b → V(a0 d3 c1), c → V(a1 b2 d2 d1), d → V(a2 c3 c2 b1)")
    print(yamada_polynomial(k))
    pass

"""

-A**4 - A**3 - 2*A**2 - A - 1
-A**2 - A - 1
-A**8 - A**7 - 5*A**6 - 4*A**5 - 8*A**4 - 4*A**3 - 5*A**2 - A - 1

-A**4 - A**3 - 2*A**2 - A - 1
-A**2 - A - 1
-A**8 - A**7 - 5*A**6 - 4*A**5 - 8*A**4 - 4*A**3 - 5*A**2 - A - 1

"""
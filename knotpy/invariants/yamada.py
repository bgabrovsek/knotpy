"""
Compute the Yamada polynomial of a knotted planar diagram.
The Yamada polynomial is described in
[Yamada, S. (1989). An invariant of spatial graphs. Journal of Graph Theory, 13(5), 537-551].
"""

__all__ = ['yamada_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import expand, Integer, symbols, Expr
from collections import deque

from knotpy import canonical
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.orientation import unoriented
from knotpy.algorithms.skein import smoothen_crossing, crossing_to_vertex
from knotpy.reidemeister.simplify import simplify_crossing_reducing
from knotpy.algorithms.topology import bridges, loops
from knotpy.manipulation.remove import remove_arc
from knotpy.manipulation.contract import contract_arc
from knotpy.utils.cache import Cache

# TODO: Implement that the framing/A/B/X markers are kept in _yamada_from_cache (simplify code)
# TODO: Do not perform crossing smoothings and deletion-contraction in the caching function (simplify code)

# Precompute powers of A + 1 + 1/A.
_A = symbols("A")
_sigma = _A + 1 + _A ** (-1)
_sigma_power = [Integer(1)]  # this will dynamically expend to consist of [σ^0, σ^1, σ^2, σ^3, ...]

"""
Initialize the global cache for the Yamada values of planar graphs without crossings.
Note that the cache takes about 7KB per element, so we need to limit the number of vertices in the cache.
The 'max_key_length' arguemnt limits the number of vertices a graph should have to be stored in the cache,
we prefer to store smaller graphs in the cache, since they are more likely to be used.
Ideal sizes are subject to testing.
"""
_yamada_planar_graph_cache = Cache(max_cache_size=1000, max_key_length=6)

"""
Initialize the global cache for the Yamada of knotted graphs.
Note that the cache takes about 7KB per element, so we need to limit the number of vertices in the cache.
The 'max_key_length' arguemnt limits the number of crossings and vertices a knotted graph should have to 
be stored in the cache, we prefer to store smaller knots in the cache, since they are more likely to be used.
Ideal sizes are subject to testing.
"""
_yamada_cache = Cache(max_cache_size=1000, max_key_length=5)  # stores pre-computed yamada polynomials for the knotted graphs

def _yamada_from_cache(k: PlanarDiagram) -> Expr:
    """
    Try to retrieve the Yamada polynomial for a knotted graph from a cache. If the
    polynomial is not found in the cache, compute it recursively using the
    A/B/X smoothing algorithm.

    Args:
        k (PlanarDiagram): The planar diagram for which the Yamada polynomial is returned.

    Returns:
        sympy.Expr: The Yamada polynomial of the knotted graph 'k'.
    """
    global _yamada_cache

    coefficient = _A ** (k.attr["_A"] - k.attr["_B"] - 2 * k.framing)
    k = canonical(k)
    k.framing = 0
    k.attr["_A"] = k.attr["_B"] = k.attr["_X"] = 0

    if k in _yamada_cache:
        polynomial = _yamada_cache[k]
    else:
        # We know that there is a crossing, since this function is called inside the "crossing loop" in _state_sum_yamada().
        crossing = next(iter(k.crossings))  # pop a crossing to smoothen
        kA = smoothen_crossing(k, crossing_for_smoothing=crossing, method="A")
        kB = smoothen_crossing(k, crossing_for_smoothing=crossing, method="B")
        kX = crossing_to_vertex(k, crossing=crossing)

        no_crossing_states_A, other_polynomials_A = _state_sum_yamada(kA)
        no_crossing_states_B, other_polynomials_B = _state_sum_yamada(kB)
        no_crossing_states_X, other_polynomials_X = _state_sum_yamada(kX)

        polyA = sum(_A ** (g.attr["_A"] - g.attr["_B"] - 2 * g.framing + 1) * _evaluate_yamada_planar_graph(g) for g in no_crossing_states_A)
        polyB = sum(_A ** (g.attr["_A"] - g.attr["_B"] - 2 * g.framing - 1) * _evaluate_yamada_planar_graph(g) for g in no_crossing_states_B)
        polyC = sum(_A ** (g.attr["_A"] - g.attr["_B"] - 2 * g.framing) * _evaluate_yamada_planar_graph(g) for g in no_crossing_states_X)

        polyA += _A * sum(other_polynomials_A)
        polyB += _A**(-1) * sum(other_polynomials_B)
        polyC += sum(other_polynomials_X)

        polynomial = polyA + polyB + polyC

    # Current "polynomial" does not account for framing, A/B coefficients of the input graph
    polynomial = expand(polynomial)

    # store the new graph into the cache
    _yamada_cache[k] = polynomial

    polynomial *= coefficient  # adjust framing and A/B coefficients of the input graph

    return polynomial


def _state_sum_yamada(k: PlanarDiagram):
    """
    Calculate the Yamada polynomial states of a planar diagram by iteratively
    applying smoothing operations (remove crossings via "A", "B", and "X" state)
    on crossings and reducing the diagram step by step.
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

    stack = deque()  # use a stack to simulate recursive calls for the smoothened states
    stack.append(k)  # add the initial diagram to the stack
    states = []  # here we store the resulting diagrams without crossings (states)
    other_polynomials = []  # here we store other polynomials computed from cache

    while stack:
        k = stack.pop()
        simplify_crossing_reducing(k, inplace=True)


        if k.crossings:

            # For small diagrams, get the value form cache.
            if len(k) <= _yamada_cache.max_key_length:
                other_polynomials.append(_yamada_from_cache(k))
                continue

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


def _remove_loops_and_isolated_vertices(g:PlanarDiagram):
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
        return _yamada_planar_graph_cache[g] * (-1 if (number_isolated_vertices + number_loops) % 2 else 1) * _sigma_power[number_loops]

    # If the Yamada is not in the cache, compute it by the deletion-contraction operation.
    if arcs := list(g.arcs):
        k_delete = remove_arc(g, arc_for_removing=arcs[0], inplace=False)
        k_contract = contract_arc(g, arc_for_contracting=arcs[0], inplace=False)
        p_k_del = _evaluate_yamada_planar_graph(k_delete)
        p_k_con = _evaluate_yamada_planar_graph(k_contract)
        polynomial =  p_k_del + p_k_con
    else:
        polynomial = Integer(1)

    # Put the newly computed polynomial in the cache (if the cache has not reached its limit).
    polynomial = expand(polynomial)
    _yamada_planar_graph_cache[g] = polynomial

    polynomial *= (-1 if (number_isolated_vertices + number_loops) % 2 else 1) * _sigma_power[number_loops]
    return polynomial


def _evaluate_yamada_planar_graph(g: PlanarDiagram) -> Expr:
    """
    Evaluate the Yamada polynomial of a planar graph without crossings.

    The function computes the Yamada polynomial of a graph by iteratively applying
    the deletion-contraction operations over arcs in the graph.

    Args:
        g (PlanarDiagram): The input planar graph diagram.

    Returns:
        Expr: The computed Yamada polynomial of the graph 'g'.
    """

    for key in set(g.attr):
        if key not in ["_loops", "_isolated_vertices"]:
            del g.attr[key]

    polynomial = Integer(0)  # store the main result (the Yamada polynomial)

    stack = deque()
    _remove_loops_and_isolated_vertices(g)
    stack.append(g)

    while stack:
        g = stack.pop()

        # If there is a bridge, just ignore it (this effectively evaluates it to 0).
        if bridges(g):
            continue

        # For small diagrams, get the value form cache.
        if len(g) <= _yamada_planar_graph_cache.max_key_length:
            polynomial += _yamada_planar_graph_from_cache(g)
            continue

        has_regular_arcs = False

        # Loop through all the arcs, by the nature of the algorithm, there should be no loops or bridges.
        for arc in g.arcs:
            k_delete = remove_arc(g, arc_for_removing=arc, inplace=False)
            k_contract = contract_arc(g, arc_for_contracting=arc, inplace=True)

            _remove_loops_and_isolated_vertices(k_delete)
            _remove_loops_and_isolated_vertices(k_contract)

            stack.append(k_delete)
            stack.append(k_contract)
            has_regular_arcs = True
            break

        # Evaluate the result if there was no deletion-contraction operation made (i.e. only loops and bridges exist).
        if not has_regular_arcs:
            polynomial += (-1 if (g.attr["_isolated_vertices"] + g.attr["_loops"]) % 2 else 1) * _sigma_power[g.attr["_loops"]]

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
    # Extend the sigma lookup table to the number of arcs, just to be safe.
    global _sigma, _sigma_power
    _sigma_power.extend([expand(_sigma**_) for _ in range(len(_sigma_power), len(k.arcs) + 1)])  # should we extend to the number of faces - 1?

    # Initialize the input diagram.
    k = unoriented(k) if k.is_oriented() else k.copy()
    k.framing = 0  # framing not yet supported

    #simplify_crossing_reducing(k, inplace=True)  # state sum already simplifies

    # Phase 1: Resolve (smoothen) all crossings.
    no_crossing_states, other_polynomials = _state_sum_yamada(k)

    # Phase 2: Use deletion-contraction operations all non-loops and non-bridges (i.e. regular arcs)
    # Warning: we must fist get g.attr, since _evaluate_yamada removes the attributes (TODO: maybe fix this?)
    polynomial = sum(_A ** (g.attr["_A"] - g.attr["_B"] - 2 * g.framing) * _evaluate_yamada_planar_graph(g) for g in no_crossing_states)
    polynomial += sum(other_polynomials)
    polynomial = expand(polynomial)

    if normalize:
        # Normalize by multiplying by A^(2n) * (-A^m), so that the lowest term of the polynomial is 1 (constant) or A.
        # This normalization translates to adding some framing (R1 move) or twist at the vertex (R4 move).
        lowest_exponent = min(term.as_coeff_exponent(_A)[1] for term in polynomial.as_ordered_terms())
        polynomial = expand((-1 if lowest_exponent % 2 else 1) * polynomial * _A**(-lowest_exponent))

    return expand(polynomial)



if __name__ == "__main__":
    pass

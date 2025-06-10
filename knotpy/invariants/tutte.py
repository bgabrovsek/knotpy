__all__ = ['tutte_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from sympy import Integer, symbols, Symbol
from collections import deque

from knotpy import from_pd_notation, bridges, is_loop, loops, is_bridge, OrientedPlanarDiagram
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import is_planar_graph
from knotpy.catalog.graphs import wheel_graph
from knotpy.manipulation.contract import contract_arc
from knotpy.manipulation.remove import remove_arc
from knotpy.algorithms.orientation import unorient

_X, _Y = symbols("x y")

def deletion_contraction(k: PlanarDiagram, contract_bridges=True):
    if "_deletions" not in k.attr:
        k.attr["_deletions"] = 0
    if "_contractions" not in k.attr:
        k.attr["_contractions"] = 0

    resolved = []
    stack = deque()
    stack.append(k)

    while stack:
        k = stack.pop()

        has_regular_arcs = False
        for arc in k.arcs:

            if not is_loop(k, arc) and (not is_bridge(k, arc) or contract_bridges):
                k_delete = remove_arc(k, arc_for_removing=arc, inplace=False)
                k_delete.attr["_deletions"] += k.attr["_deletions"] + 1
                k_contract = contract_arc(k, arc_for_contracting=arc, inplace=False)
                k_contract.attr["_contractions"] += k.attr["_contractions"] + 1
                stack.append(k_delete)
                stack.append(k_contract)
                has_regular_arcs = True
                break  # TODO: optimize

        if not has_regular_arcs:
            resolved.append(k)
    return resolved

def tutte_polynomial(k: PlanarDiagram | OrientedPlanarDiagram, variables="xy"):
    """
    Compute the Tutte polynomial of a planar graph represented as a PlanarDiagram.

    The Tutte polynomial is a two-variable polynomial known for its applications
    in graph theory, combinatorics, and statistical physics. This function
    computes the Tutte polynomial for planar graphs without crossings.

    Parameters:
    -----------
    k : PlanarDiagram
        A planar graph represented as a PlanarDiagram object. The input graph must be free of crossings.

    variables : str or iterable[Symbol], optional, default="xy"
        A string (of length 2) or an iterable containing two variables to be used
        in the Tutte polynomial (e.g., "xy" or [x, y]). If using a string, its two
        characters will be interpreted as symbolic variables.

    Raises:
    -------
    ValueError
        If `k` is not a planar graph (i.e., it contains crossings).

    Returns:
    --------
    sympy.Expr
        The symbolic representation of the Tutte polynomial as a `sympy.Expr` object.

    Notes:
    ------
    1. The function uses a recursive contraction-deletion approach to compute the
       polynomial by traversing and simplifying the arcs in the graph.

    Examples:
    ---------
    Compute the Tutte polynomial for a wheel graph with 4 nodes:

    ```python
    from knotpy.catalog.graphs import wheel_graph
    from tutte import tutte_polynomial

    w = wheel_graph(4)
    polynomial = tutte_polynomial(w)
    print(polynomial)
    ```
    """

    if len(variables) != 2:
        raise ValueError("Two variables mst be given for the tutte polynomial")

    if not is_planar_graph(k):
        raise ValueError("Tutte polynomial can only be computed on planar graphs without crossings")

    k = unorient(k) if k.is_oriented() else k.copy()

    x = variables[0] if isinstance(variables[0], Symbol) else symbols(variables[0])
    y = variables[1] if isinstance(variables[1], Symbol) else symbols(variables[1])

    stack = deque()  # keep diagrams with non-loop and non-bridges
    resolved = []

    if not k.is_framed():
        k.framing = 0

    k.attr["_deletions"] = 0
    k.attr["_contractions"] = 0

    resolved = deletion_contraction(k, contract_bridges=False)
    # resolved graphs consists of only of loops and bridges
    polynomial = Integer(0)
    for g in resolved:
        # ignore number of deletions/contractions
        b, l = len(bridges(g)), len(loops(g))
        if b + l != len(g.arcs):  # just a quick check
            raise ValueError("Not all arcs are bridges or loops")

        polynomial += x ** b * y ** l

    return polynomial


if __name__ == "__main__":

    m = from_pd_notation("V[0,1,2],V[0,3,4],V[4,5,6,1],V[2,6,7,8],V[8,7,5,3],V[9,9]")
    print(m)
    for q in deletion_contraction(m, contract_bridges=False):
        print("  ", q)

    for a in m.arcs:
        print("arc", a, "->", is_loop(m, a), is_bridge(m, a))
    exit()


    g = wheel_graph(7)  # works!!!!
    print(tutte_polynomial(g))

    # g = PlanarDiagram()
    # g.set_arcs_from("a0a3,a1b0,a2b1")
    # # print(g)
    # # g_ = contract_arc(g, arc_for_contracting=(("b",0),("a",1)))
    # # print(g_)
    # print(tutte_polynomial(g))
    #
    #


    exit()

    # g = PlanarDiagram()
    # g.add_vertices_from("abd")
    # g.set_arc((("a",0),("d",1)))
    # g.set_arc((("a", 1), ("d", 0)))
    # g.set_arc((("b", 0), ("d", 2)))
    # print(g)
    # for arc in g.arcs:
    #     print(arc)
    #     print(is_bridge(g, arc),is_loop(g, arc) )
    # exit()

    # q = PlanarDiagram()
    # q.add_vertices_from("ab")
    # q.set_arc((("a",0),("b",0)))
    # arc = list(q.arcs)[0]
    # print(is_bridge(q,arc))
    # print(q)
    # exit()

    for i in range(1):
        w = wheel_graph(4)

        print(tutte_polynomial(w))
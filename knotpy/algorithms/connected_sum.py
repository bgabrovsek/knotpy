"""" Connected sum components are the factors of a composite knot diagram. Here we also include cut-sets.
"""

__all__ = ['is_connected_sum', 'is_connected_sum_third_order',"cut_sets", "to_connected_sum"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from copy import deepcopy
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation

from knotpy.algorithms.disjoint_sum import to_disjoint_sum
from knotpy.classes.composite import ConnectedSum

import knotpy


def is_connected_sum(g: PlanarDiagram) -> bool:
    """Return True if g is a connected sum diagram and False otherwise."""
    return len(cut_sets(g, order=2, max_cut_sets=1)) > 0


def to_connected_sum(k: PlanarDiagram) -> ConnectedSum:
    """Return a list of connected sum components."""

    if is_connected_sum(k):
        raise ValueError("Cannot spit disjoint sum into a connected sum (ambiguity)")

    cs = cut_sets(k, order=2, max_cut_sets=1)
    if not cs:
        return ConnectedSum(k)

    (e, f), = cs  # get the two edges of the cut-set
    e_a, e_b = e
    f_a, f_b = f

    faces = list(k.faces)  # maybe list is not needed

    # cross-edges
    aa = {e_a, f_a}
    bb = {e_b, f_b}
    ab = {e_a, f_b}
    ba = {e_b, f_a}

    if any(aa.issubset(f) for f in faces) and any(bb.issubset(f) for f in faces):
        a, b, x, y = e_a, f_b, e_b, f_a  # connect a b and x y
    elif any(ab.issubset(f) for f in faces) and any(ba.issubset(f) for f in faces):
        a, b, x, y = e_a, f_a, e_b, f_b  # connect a b and x y
    else:
        raise ValueError(f"Cannot determine how to cut a composite knot {k}")

    # redirect endpoint, so that we get a split (disjoint sum)
    s = k.copy()
    s.set_endpoint(a, b, create_using=type(a), *a.attr)
    s.set_endpoint(b, a, create_using=type(b), *b.attr)
    s.set_endpoint(x, y, create_using=type(y), *y.attr)
    s.set_endpoint(y, x, create_using=type(x), *x.attr)

    ds = to_disjoint_sum(s)
    return ConnectedSum(to_connected_sum(_) for _ in ds) # recursively split even further
    #
    #
    #
    # splitting = to_disjoint_sum(s)
    # if not s.name:
    #     for i, s in enumerate(splitting):
    #         s.name = f"({i})"
    #
    # # recursively split the knot even further
    # splitting = [c for s in splitting for c in (to_connected_sum(s) if is_connected_sum(s) else (s,))]


def is_connected_sum_third_order(g: PlanarDiagram) -> bool:
    """Return True if g is a 3rd order connected sum diagram and False otherwise."""
    return len(cut_sets(g, order=3, max_cut_sets=1)) > 0


def cut_sets(k: PlanarDiagram, order: int, max_cut_sets=None) -> list:
    """Finds all k-cut of a graph. A k-cut-set of a graph is a set of k edges that when removed disconnects the graph
    into two or more components. In our case, we assume the components have more than one node. This may cause potential
    problems, for example, if the cut-set disconnects the graph into three components, and only one component has one
    node, the algorithm does not find this cut-set. If needed, the algorithm can be easily adopted for this situation.
    :param k: knot/graph
    :param order: number of arcs in the cut-set (k)
    :param max_cut_sets: if not None, finds up to max_cut k-cut-sets
    :return: a list of cut-sets consisting of tuples of arcs
    """

    if max_cut_sets is not None and max_cut_sets == 0:
        return []

    all_arcs = list(k.arcs)
    all_cut_sets = []

    for cut_set in combinations(all_arcs, order):
        node_er = EquivalenceRelation(k.nodes)  # let nodes be equivalence classes
        for ep1, ep2 in set(all_arcs) - set(cut_set):  # loop through all arcs not in the potential cut-set
            node_er[ep1.node] = ep2.node

        classes = list(node_er.classes())
        if any(len(c) <= 1 for c in classes):  # a single vertex cannot be a "cut-set" component
            continue
        # it can happen that a cut set has three components, e.g. in knotoids
        # if len(classes) >= 3:
        #     warnings.warn(f"The cut-set {cut_set} contains three components.")
        #     print("ERROR", k)
        #     print("ERROR", knotpy.notation.to_pd_notation(k))
        #     print("ERROR", classes)

        if len(classes) >= 2:  # normal "cut-set"
            if all(node_er[arc0.node] != node_er[arc1.node] for arc0, arc1 in cut_set):  # do we need to check this?
                all_cut_sets.append(cut_set)
                if max_cut_sets is not None and len(all_cut_sets) >= max_cut_sets:
                    break

    return all_cut_sets


if __name__ == "__main__":
    import knotpy as kp
    k = kp.from_pd_notation("X[0,1,2,3],X[1,0,3,4],X[5,2,6,7],X[4,5,7,6]")
    print(k)
    print(cut_sets(k, order=2, max_cut_sets=1))

    components = to_connected_sum(k)
    for c in components:
        print("  ", c)
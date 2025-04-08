"""
This module provides tools for identifying and analyzing (arc) cut sets in planar diagrams.

Ana arc cut set in a graph or diagram is a set of edges (arcs) that, when removed,
disconnects the graph into two or more disjoint components.
These functions are designed to work with planar diagram representations,
allowing the detection of such critical subsets of arcs and vertices.
"""

__all__ = ["is_arc_cut_set", "arc_cut_sets"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

from collections import Counter
from itertools import combinations

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.disjoint_union_set import DisjointSetUnion
from knotpy.algorithms.disjoint_sum import number_of_disjoint_components


def is_arc_cut_set(k: PlanarDiagram, arcs, include_singletons=True) -> bool:
    """Checks if the given list of arcs forms a cut set in the planar diagram.
    
    A cut set is a subset of arcs whose removal breaks the diagram into two or more disjoint components.
    
    Args:
        k (PlanarDiagram): The planar diagram representing the knot or graph.
        arcs (iterable): A list or set of arcs to check if they form a cut set.
        include_singletons (bool): Whether to count disconnected single nodes in the resulting components (default: True).
    
    Returns:
        bool: True if the given arcs form a cut set, False otherwise.
    """

    ndc = number_of_disjoint_components(k)
    n_singletons = [k.degree(node) == 0 for node in k.nodes]  # number of singletons

    dsu = DisjointSetUnion(k.nodes)  # stores sets of nodes which are connected

    for arc in k.arcs:
        if arc in arcs:
            continue
        ep1, ep2 = arc
        dsu[ep1.node] = ep2.node  # put the nodes in the same set if they are connected

    if include_singletons:
        return len(dsu) > ndc
    else:
        return sum(len(c) > 1 for c in dsu) > ndc - sum(n_singletons)



def arc_cut_sets(k: PlanarDiagram, order: int, max_cut_sets=None) -> list:
    """
        Find all arc cut sets of size `k` in a planar diagram.
        
        A k-cut-set is a subset of `k` arcs that, when removed, disconnects the diagram into two or more components. 
        This function identifies all such subsets of arcs that meet the criteria, ensuring all resulting components 
        have more than one node unless `include_singletons=True` is set in the helper function.
        
        Args:
            k (PlanarDiagram): The planar diagram representing the knot or graph.
            order (int): The size of the arc cut sets to be identified.
            max_cut_sets (int, optional): The maximum number of cut sets to return. If None, all possible cut sets are found.
        
        Returns:
            list: A list of tuples, where each tuple represents a cut set containing `order` arcs.

        Args:
            k (PlanarDiagram): The planar diagram representing the knot or graph.
            order (int): The number of arcs in the cut-set (k).
            max_cut_sets (int, optional): The maximum number of k-cut-sets to find. If None, all possible cut-sets are found.

        Returns:
            list: A list of cut-sets, where each cut-set is a tuple of arcs.

        Raises:
            Warning: If a cut-set results in three disconnected components, such as in knotoids.

        Example:
            >>> import knotpy as kp
            >>> k = kp.from_pd_notation("X[0,1,2,3],X[1,0,3,4],X[5,2,6,7],X[4,5,7,6]")
            >>> arc_cut_sets(k, order=2, max_cut_sets=1)
            [(arc1, arc2)]
    """

    if max_cut_sets == 0:
        return []

    all_arcs = list(k.arcs)
    all_cut_sets = []

    for cut_set in combinations(all_arcs, order):
        if is_arc_cut_set(k, cut_set):
            all_cut_sets.append(cut_set)
            if max_cut_sets is not None and len(all_cut_sets) >= max_cut_sets:
                break

    return all_cut_sets

#def articulation_nodes(k: PlanarDiagram) -> set:

def cut_vertices(k: PlanarDiagram) -> set:
    """
    Identify the cut vertices (articulation nodes) in a planar diagram.
    
    A cut vertex is a node whose removal increases the number of connected components in the diagram. 
    In the context of this function, it detects nodes that belong to multiple faces in the planar diagram.
    
    Args:
        k (PlanarDiagram): The planar diagram to analyze.
    
    Returns:
        set: A set of nodes that are cut vertices (articulation points) in the diagram.
    """
    nodes = set()
    for f in k.faces:
        # keep nodes that repeat twice or more in a face
        counts = Counter(ep.node for ep in f)
        nodes |= {node for node, count in counts.items() if count >= 2}

    return nodes

if __name__ == "__main__":
    pass

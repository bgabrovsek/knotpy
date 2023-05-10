"""Computes various decompositions of knotted objects, namely:

- "link components" are connected components of a link, e.g. a knot has 1 link component, the Hopf link has 2 link
  components and the Borromean Link has 3 link components,

- "disjoint components": are the components that do not share a common node (crossing or vertex),

- "connected sum components" are the factors of a composite knot diagram.
"""

__all__ = ['disjoint_components_nodes', 'number_of_disjoint_components', 'disjoint_components', ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from copy import deepcopy
from itertools import combinations
import warnings

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation



#  Link components


def number_of_link_components(K):
    return len(link_component_endpoints(K))

def link_component_endpoints(K):
    er = EquivalenceRelation(K.adj)
    crossings = set(K.crossings)
    vertices = set(K.vertices)

    for v in K.nodes:
        pass


    pass


# Disjoint components

def disjoint_components_nodes(self):
    er = EquivalenceRelation(self._adj)
    for v in self._adj:
        for u, u_pos in self._adj[v]:
            er[v] = u

    return er.classes()


def number_of_disjoint_components(self):
    return len(self._connected_components_nodes())


def disjoint_components(K):
    components = []
    for component_nodes in sorted(K._connected_components_nodes(), reverse=True):
        g = K.__class__()
        g.attr = deepcopy(K.attr)
        g._adj = {node: deepcopy(K._adj[node]) for node in component_nodes}
        g._node_attr = {node: deepcopy(K._node_attr[node]) for node in component_nodes}
        g._endpoint_attr = {deepcopy(ep): deepcopy(K._endpoint_attr[ep])
                            for ep in K._endpoint_attr if ep[0] in component_nodes}
        components.append(g)

    for g in components[1:]:
        g.framing = 0
    return components


# Connected sum components


def is_connected_sum(g: PlanarDiagram) -> bool:
    """Return True if g is a connected sum diagram and False otherwise."""
    return len(cut_sets(g, order=2, max_cut_sets=1)) > 0


def is_connected_sum_third_order(g: PlanarDiagram) -> bool:
    """Return True if g is a 3rd order connected sum diagram and False otherwise."""
    return len(cut_sets(g, order=3, max_cut_sets=1)) > 0


def cut_sets(g: PlanarDiagram, order: int, max_cut_sets=None) -> list:
    """Finds all k-cut of a graph. A k-cut-set of a graph is a set of k edges that when removed disconnects the graph
    into two or more components. In our case, we assume the components have more than one node. This may cause potential
    problems, for example, if the cut-set disconnects the graph into three components, and only one component has one
    node, the algorithm does not find this cut-set. If needed, the algorithm can be easily adopted for this situation.
    :param g: graph
    :param order: number of arcs in the cut-set (k)
    :param max_cut_sets: if not None, finds up to max_cut k-cut-sets
    :return: a list of cut-sets consisting of tuples of arcs
    """

    if max_cut_sets is not None and max_cut_sets == 0: return []

    all_arcs = g.arcs()
    all_cut_sets = []


    for cut_set in combinations(all_arcs, order):
        node_er = EquivalenceRelation([ep[0] for arc in cut_set for ep in arc])  # let nodes be equivalence classes
        for ep1, ep2 in set(all_arcs) - set(cut_set):  # loop through all arcs not in the potential cut-set
            node_er[ep1[0]] = ep2[0]

        classes = list(node_er.classes())
        if any(len(c) <= 1 for c in classes):
            continue
        if len(classes) > 2:
            warnings.warn(f"Third order connected sum connects three components {cut_set}.")

        if len(classes) >= 2:
            if all(node_er[arc[0][0]] != node_er[arc[1][0]] for arc in cut_set):
                all_cut_sets.append(cut_set)
                if max_cut_sets is not None and len(all_cut_sets) >= max_cut_sets:
                    break

    return all_cut_sets



if __name__ == "__main__":
    pass
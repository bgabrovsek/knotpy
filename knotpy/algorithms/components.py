"""Computes various decompositions of knotted objects, namely:

- "link components" are connected components of a link, e.g. a knot has 1 link component, the Hopf link has 2 link
  components and the Borromean Link has 3 link components,

- "disjoint components": are the components that do not share a common node (crossing or vertex),

- "connected sum components" are the factors of a composite knot diagram.
"""

__all__ = ['disjoint_components_nodes', 'number_of_disjoint_components', 'disjoint_components',
           'is_connected_sum', 'is_connected_sum_third_order', 'add_unknot_in_place',
           'number_of_link_components']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from copy import deepcopy
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_algorithms import name_for_new_node
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation


#  Link components

def add_unknot_in_place(k):
    node = name_for_new_node(k)
    try:
        k.add_bivalent_vertex(node)
    except AttributeError:
        k.add_vertex(node)
    k.set_arc(((node, 0), (node, 1)))


def number_of_link_components(k: PlanarDiagram):
    return len(link_components_endpoints(k))


def link_components_endpoints(k: PlanarDiagram):
    er = EquivalenceRelation(k.endpoints)

    # endpoints from arcs are on the same component
    for arc in k.arcs:
        er[arc[0]] = arc[1]

    # endpoints from crossings/vertices
    for node in k.nodes:
        if isinstance(k.nodes[node], kp.Crossing):  # k.nodes[node].is_crossing(): # toDO:fix
            er[k.nodes[node][0]] = k.nodes[node][2]
            er[k.nodes[node][1]] = k.nodes[node][3]
        else:
            # assume that everything that is not a crossing is a connected
            for ep0, ep1 in combinations(k.nodes[node], r=2):
                er[ep0] = ep1

    return er.classes()
    pass


def path_from_endpoint(k: PlanarDiagram, endpoint: Endpoint):
    path = []
    while True:
        path.append(endpoint)
        node_ = k.nodes[endpoint.node]
        if node_.is_crossing():
            endpoint = node_[(endpoint.position + 2) & 3]
        elif node_.is_bivalent_vertex():
            endpoint = node_[(endpoint.position + 1) & 1]
        else:
            # the path ends if we come across a vertex
            break
        if endpoint == path[0]:
            break
    return path


# Disjoint components

def disjoint_components_nodes(k):
    er = EquivalenceRelation(k.nodes)
    for ep0, ep1 in k.arcs:
        er[ep0.node] = ep1.node
    return er.classes()


def number_of_disjoint_components(k):
    return len(disjoint_components_nodes(k))


def disjoint_components(K):
    raise NotImplementedError()
    # components = []
    # for component_nodes in sorted(K._connected_components_nodes(), reverse=True):
    #     g = K.__class__()
    #     g.attr = deepcopy(K.attr)
    #     g._adj = {node: deepcopy(K._adj[node]) for node in component_nodes}
    #     g._node_attr = {node: deepcopy(K._node_attr[node]) for node in component_nodes}
    #     g._endpoint_attr = {deepcopy(ep): deepcopy(K._endpoint_attr[ep])
    #                         for ep in K._endpoint_attr if ep[0] in component_nodes}
    #     components.append(g)
    #
    # for g in components[1:]:
    #     g.framing = 0
    # return components


def disjoint_sum(*knots, return_relabel_dicts=False, create_using=None):
    """Return the disjoint sum, k[0] ⊔ k[1] ⊔ ... The nodes are relabelled to be "a", "b",... or in case of many
    nodes, 0, 1,...
    :param create_using: structure type of disjoint sum
    :param knots: list of components
    :param return_relabel_dicts:
    :return: disjoint sum ⊔k
    """
    if len(knots) <= 1:
        raise ValueError("Cannot create disjoint sum of one or less knots.")

    new_knot_name = u"\u2294".join(str(k.name) for k in knots)
    new_knot_framing = sum(k.framing for k in knots)

    new_knot = (create_using or type(knots[0]))()
    num_nodes = sum(len(k) for k in knots)
    node_label_iter = iter(ascii_letters[:num_nodes] if num_nodes <= len(ascii_letters) else range(num_nodes))

    relabel_dicts = []  # dicts that map the node of the component to the new (integer) node in the disjoint sum
    for k in knots:

        new_knot.attr.update(k.attr)  # update attributes
        relabel_dicts.append(relabelling := dict())  # create new node dict for the component

        for node, inst in k.nodes.items():
            node_label = next(node_label_iter)
            relabelling[node] = node_label
            # add the relabelled node
            new_knot.add_node(
                node_for_adding=node_label,
                create_using=type(inst),
                degree=len(inst),
                **inst.attr
            )

        for arc in k.arcs:
            for ep0, ep1 in permutations(arc):
                new_knot.set_endpoint(
                    endpoint_for_setting=(relabelling[ep0.node], ep0.position),
                    adjacent_endpoint=(relabelling[ep1.node], ep1.position),
                    create_using=type(ep1),
                    **ep1.attr
                )

    new_knot.name = new_knot_name
    new_knot.framing = new_knot_framing

    return (new_knot, relabel_dicts) if return_relabel_dicts else new_knot







# Connected sum components


def is_connected_sum(g: PlanarDiagram) -> bool:
    """Return True if g is a connected sum diagram and False otherwise."""
    return len(cut_sets(g, order=2, max_cut_sets=1)) > 0


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
        if len(classes) >= 3:
            warnings.warn(f"The cut-set {cut_set} contains three components.")

        if len(classes) >= 2:  # normal "cut-set"
            if all(node_er[arc[0].node] != node_er[arc[1].node] for arc in cut_set):  # do we need to check this?
                all_cut_sets.append(cut_set)
                if max_cut_sets is not None and len(all_cut_sets) >= max_cut_sets:
                    break

    return all_cut_sets


if __name__ == "__main__":
    g = kp.from_plantri_notation("bcde,aedc,abd,acbe,adb")
    print(g)


    gu = g.copy()
    add_unknot_in_place(gu)
    print(gu)

    print("Number dc", number_of_disjoint_components(gu))
    print("DC nodes",disjoint_components_nodes(gu))
    #print("Disjoint components", disjoint_components(gu))
    print("link_components", link_components_endpoints(gu))

    pass

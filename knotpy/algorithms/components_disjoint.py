"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).
"""

__all__ = ['disjoint_components_nodes', 'number_of_disjoint_components', 'disjoint_components',
           'add_unknot_in_place',
           ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation


def add_unknot_in_place(k: PlanarDiagram, number_of_unknots=1):
    """Add unknot to k (in place). If the planar diagram instance does not contain vertices (e.g. knots), adds the
    "unknots" attribute.
    :param k: input planar diagram
    :param number_of_unknots: number of unknots (default is 1)
    :return: k with a disjoint unknot
    """
    for _ in range(number_of_unknots):
        if hasattr(k, 'vertices'):
            node = name_for_new_node(k)
            k.add_vertex(node)
            k.set_arc(((node, 0), (node, 1)))
        else:
            # if structure has no vertices, increase the number of unknots in the attribute
            k.attr["unknots"] = k.attr.get("unknots", 0) + 1




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

    if create_using is not None and type(create_using) is not type:
        raise TypeError("Creating disjoint sum with create_using instance not yet supported.")

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


def disjoint_components_nodes(k):
    er = EquivalenceRelation(k.nodes)
    for ep0, ep1 in k.arcs:
        er[ep0.node] = ep1.node
    return er.classes()










# Connected sum components



if __name__ == "__main__":
    # g = kp.from_plantri_notation("bcde,aedc,abd,acbe,adb")
    # print(g)
    #
    #
    # gu = g.copy()
    # add_unknot_in_place(gu)
    # print(gu)
    #
    # print("Number dc", number_of_disjoint_components(gu))
    # print("DC nodes",disjoint_components_nodes(gu))
    # #print("Disjoint components", disjoint_components(gu))
    # print("link_components", link_components_endpoints(gu))

    pass

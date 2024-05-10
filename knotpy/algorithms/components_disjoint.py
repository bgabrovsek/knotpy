"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).
"""

__all__ = ['number_of_disjoint_components', 'disjoint_components',
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
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation


def add_unknot_in_place(k: PlanarDiagram, number_of_unknots=1):
    """Add unknot to k (in place). An unknot is a vertex with one edge (loop).
    :param k: input planar diagram
    :param number_of_unknots: number of unknots (default is 1)
    :return: k with a disjoint unknot
    """
    for _ in range(number_of_unknots):
        node = name_for_new_node(k)
        k.add_vertex(node)
        k.set_arc(((node, 0), (node, 1)))


def _disjoint_components_nodes(k: PlanarDiagram) -> list:
    """ Return a list of sets of nodes that belong to the same disjoint components.
    :param k: (disjoint) planar diagram
    :return: list of sets of nodes
    """
    er = EquivalenceRelation(k.nodes)
    for ep0, ep1 in k.arcs:
        er[ep0.node] = ep1.node
    return er.classes()


def number_of_disjoint_components(k):
    return len(_disjoint_components_nodes(k))


def disjoint_components(k: PlanarDiagram) -> list:
    """If k is a disjoint sum, return a list  of disjoint components.
    :param k:
    :return:
    """
    components = []

    # add components
    for component_nodes in sorted(_disjoint_components_nodes(k), reverse=True):
        g = k.copy()
        g.name = f"{g.name} ({len(components)})"
        g.remove_nodes_from(set(g.nodes) - component_nodes, remove_incident_endpoints=False)  # incident ep will be removed automatically
        components.append(g)

    # # add unknot components
    # for g in range(k.attr.get("unknots", 0)):
    #     h = type(k)()  # trivial planar diagram
    #     g.name = f"{g.name} ({len(components)})"
    #     components.append(g)

    components[0].framing = k.framing  # this should hold automatically
    for g in components[1:]:
        g.framing = 0

    return components


def disjoint_sum(*knots, return_relabel_dicts=False):
    """Return the disjoint sum, k[0] ⊔ k[1] ⊔ ... The nodes are relabelled to be "a", "b",... or in case of many
    nodes, 0, 1,...
    :param create_using: structure type of disjoint sum
    :param knots: list of components
    :param return_relabel_dicts:
    :return: disjoint sum ⊔k
    """

    if all(isinstance(k, PlanarDiagram) for k in knots):
        create_using = PlanarDiagram
    elif all(isinstance(k, OrientedPlanarDiagram) for k in knots):
        create_using = OrientedPlanarDiagram
    else:
        raise TypeError("Cannot create disjoint sum using oriented and non-oriented diagrams.")

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

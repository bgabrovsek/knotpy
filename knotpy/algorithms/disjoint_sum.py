"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).

A disjoint sum, in the context of planar knot diagrams, is the combination of two or more planar diagrams 
such that they remain independent and do not share any nodes or arcs.
"""

# TODO: write tests

__all__ = ['number_of_disjoint_components', 'split_disjoint_sum',
           'add_unknot', "number_of_unknots", "remove_unknots", "is_disjoint_sum",
           "disjoint_sum"
           ]
__version__ = '0.2'
__author__ = 'Boštjan Gabrovšek'

from string import ascii_letters
from itertools import permutations

from knotpy.algorithms.naming import unique_new_node_name
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.disjoint_union_set import DisjointSetUnion


def add_unknot(k: PlanarDiagram, number_of_unknots=1, inplace=True):
    """Disjointly adds an unknot (or multiple unknots) to the given planar diagram.

    An unknot is represented as a vertex with a single edge forming a loop. The function modifies the diagram in place
    unless specified otherwise.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :param number_of_unknots: The number of unknots to add. Default is 1.
    :type number_of_unknots: int, optional
    :param inplace: If True, modifies the diagram in place; otherwise, returns a copy.
    :type inplace: bool, optional
    :return: The modified planar diagram with added unknots.
    :rtype: PlanarDiagram

    .. note::
       - The function supports both oriented and unoriented planar diagrams.
    """
    if not inplace:
        k = k.copy()
    oriented = k.is_oriented()
    for _ in range(number_of_unknots):
        node = unique_new_node_name(k)
        k.add_vertex(node, degree=2)
        k.set_endpoint((node, 0), (node, 1), IngoingEndpoint if oriented else Endpoint)
        k.set_endpoint((node, 1), (node, 0), OutgoingEndpoint if oriented else Endpoint)
    return k


def _disjoint_components_nodes(k: PlanarDiagram) -> list:
    """
    Return a list of sets of nodes that belong to the same disjoint components.

    :param k: (disjoint) planar diagram
    :return: list of sets of nodes
    """
    dsu = DisjointSetUnion(k.nodes)  # TODO: replace with DSU
    for ep0, ep1 in k.arcs:
        dsu[ep0.node] = ep1.node
    return list(dsu.classes())


def number_of_disjoint_components(k: PlanarDiagram):
    """
    Return the number of disjoint components in the given planar diagram.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :return: The number of disjoint components.
    :rtype: int
    """
    return len(_disjoint_components_nodes(k))


def is_disjoint_sum(k: PlanarDiagram):
    """
    Return whether the given planar diagram consists of multiple disjoint components.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :return: True if the diagram has more than one disjoint component, False otherwise.
    :rtype: bool
    """
    return len(_disjoint_components_nodes(k)) > 1


def split_disjoint_sum(k: PlanarDiagram) -> list:
    """
    Return a list of disjoint components of the given planar diagram.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :return: A list of disjoint components as `PlanarDiagram` instances.
    :rtype: list
    """

    list_of_knot_components = []

    for component_nodes in sorted(_disjoint_components_nodes(k), reverse=True):
        g = k.copy(name=f"{k.name} (disjoint component)")
        g.remove_nodes_from(set(g.nodes) - component_nodes,
                            remove_incident_endpoints=False)  # incident ep will be removed automatically

        list_of_knot_components.append(g)
    return list_of_knot_components

# def disjoint_components(k: PlanarDiagram) -> list:
#     """If k is a disjoint sum, return a list  of disjoint components.
#     :param k:
#     :return:
#     """
#     components = []
#
#     # add components
#     for component_nodes in sorted(_disjoint_components_nodes(k), reverse=True):
#         g = k.copy()
#         g.name = f"{g.name} ({len(components)})"
#         g.remove_nodes_from(set(g.nodes) - component_nodes, remove_incident_endpoints=False)  # incident ep will be removed automatically
#         components.append(g)
#
#     # # add unknot components
#     # for g in range(k.attr.get("unknots", 0)):
#     #     h = type(k)()  # trivial planar diagram
#     #     g.name = f"{g.name} ({len(components)})"
#     #     components.append(g)
#
#     components[0].framing = k.framing  # this should hold automatically
#     for g in components[1:]:
#         g.framing = None if k.framing is None else 0
#
#     return components


def disjoint_sum(*knots):
    """
    Return the disjoint sum of the given planar diagrams.

    The function takes multiple `PlanarDiagram` instances and constructs their disjoint sum.
    Nodes in the resulting diagram are relabeled to ensure uniqueness, using either letters ("a", "b", ...) or integers
    if necessary.

    :param knots: The planar diagrams to be combined.
    :type knots: tuple[PlanarDiagram]
    :raises TypeError: If a mix of oriented and non-oriented diagrams is provided.
    :raises ValueError: If fewer than two diagrams are given.
    :return: The disjoint sum of the input diagrams.
    :rtype: PlanarDiagram

    .. note::
       - The function ensures that the result retains attributes of the input diagrams.
    """

    if all(isinstance(k, PlanarDiagram) for k in knots):
        create_using = PlanarDiagram
    elif all(isinstance(k, OrientedPlanarDiagram) for k in knots):
        create_using = OrientedPlanarDiagram
    else:
        raise TypeError(
            "Cannot create a disjoint sum with a mix of oriented and non-oriented diagrams.\n"
            "Ensure that all input diagrams are either `PlanarDiagram` or `OrientedPlanarDiagram`, but not both."
        )

    if len(knots) == 0:
        raise ValueError("At least one planar diagram must be provided.")
    elif len(knots) == 1:
        return knots[0].copy()

    new_knot_name = u"\u2294".join(str(k.name) for k in knots)
    new_knot_framing = sum(k.framing for k in knots) if all(k.framing is not None for k in knots) else None

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

    # # node relabelling is obsolete
    # relabel_dicts_inv = [{value: key for key, value in d.items()} for d in relabel_dicts]
    # return (new_knot, relabel_dicts_inv) if return_relabel_dicts else new_knot

    return new_knot


def _is_vertex_an_unknot(k: PlanarDiagram, vertex):
    """
    Return True if the given vertex is an unknot, i.e., a degree-2 vertex with both endpoints forming a loop to itself.

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :param vertex: The vertex to check.
    :type vertex: Hashable
    :return: True if the vertex is an unknot, False otherwise.
    :rtype: bool
    """
    return len(k.nodes[vertex]) == 2 and k.nodes[vertex][0].node == k.nodes[vertex][1].node == vertex


def number_of_unknots(k: PlanarDiagram):
    """
    Return the number of unknots (degree-1 vertices with a self-loop).

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :return: The count of unknots.
    :rtype: int
    """
    return sum(1 for v in k.vertices if _is_vertex_an_unknot(k, v))


def remove_unknots(k: PlanarDiagram, max_unknots=None):
    """
    Remove unknots from the diagram (up to `max_unknots` unknots if given).

    :param k: The input planar diagram.
    :type k: PlanarDiagram
    :param max_unknots: Maximum number of unknots to remove (removes all if None).
    :type max_unknots: int, optional
    :return: The number of unknots removed.
    :rtype: int
    """

    vertices_to_remove = []
    for v in k.vertices:
        if max_unknots is not None and len(vertices_to_remove) >= max_unknots:
            break
        if _is_vertex_an_unknot(k, v):
            vertices_to_remove.append(v)

    for v in vertices_to_remove:
        k.remove_node(v, remove_incident_endpoints=True)
    return len(vertices_to_remove)


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

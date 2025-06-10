"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).

A disjoint sum, in the context of planar knot diagrams, is the combination of two or more planar diagrams 
such that they remain independent and do not share any nodes or arcs.
"""


__all__ = ['number_of_disjoint_components', 'disjoint_union_decomposition',
           'add_unknot', "is_disjoint_union",
           "disjoint_union"
           ]
__version__ = '0.2'
__author__ = 'Boštjan Gabrovšek'

from string import ascii_letters
from itertools import permutations

from knotpy.algorithms.naming import unique_new_node_name, generate_node_names
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.disjoint_union_set import DisjointSetUnion


def add_unknot(k: PlanarDiagram, number_of_unknots=1, inplace=True):
    """
    Add one or more unknots disjointly to the given planar diagram.

    An unknot is represented as a vertex with a single edge forming a loop.
    The function modifies the diagram in place unless specified otherwise.

    Args:
        k (PlanarDiagram): The input planar diagram.
        number_of_unknots (int, optional): The number of unknots to add. Defaults to 1.
        inplace (bool, optional): If True, modifies the diagram in place. If False, returns a modified copy.

    Returns:
        PlanarDiagram: The modified planar diagram with added unknots.

    Notes:
        The function supports both oriented and unoriented planar diagrams.
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
    Args:
        k (PlanarDiagram): A (disjoint) planar diagram.
    Returns:
        list[set[int]]: A list where each set contains the node indices of one connected component.
    """
    dsu = DisjointSetUnion(k.nodes)  # TODO: replace with DSU
    for ep0, ep1 in k.arcs:
        dsu[ep0.node] = ep1.node
    return list(dsu.classes())


def number_of_disjoint_components(k: PlanarDiagram):
    """
    Return the number of disjoint (connected) components in the given planar diagram.
    Args:
        k (PlanarDiagram): The input planar diagram.
    Returns:
        int: The number of disjoint components.
    """
    return len(_disjoint_components_nodes(k))


def is_disjoint_union(k: PlanarDiagram):
    """
   Return whether the given planar diagram consists of multiple disjoint components.
   Args:
       k (PlanarDiagram): The input planar diagram.
   Returns:
       bool: True if the diagram has more than one disjoint component, False otherwise.
   """
    return len(_disjoint_components_nodes(k)) > 1


def disjoint_union_decomposition(k: PlanarDiagram) -> list:
    """
    Return a list of disjoint components of the given planar diagram.
    Each component is returned as a separate PlanarDiagram instance.
    Args:
        k (PlanarDiagram): The input planar diagram.
    Returns:
        list[PlanarDiagram]: A list of disjoint components, each as a PlanarDiagram instance.
    """

    list_of_knot_components = []

    for component_nodes in sorted(_disjoint_components_nodes(k), reverse=True):
        g = k.copy(name=f"{k.name} (disjoint component)")
        g.remove_nodes_from(set(g.nodes) - component_nodes,
                            remove_incident_endpoints=False)  # incident ep will be removed automatically

        list_of_knot_components.append(g)

    # put framing only to the first component
    if k.framing is not None:
        list_of_knot_components[0].framing = k.framing
        for g in list_of_knot_components[1:]:
            g.framing = 0

    return list_of_knot_components


def disjoint_union(*knots: PlanarDiagram | OrientedPlanarDiagram, return_relabel_dictionaries=False):
    """
    Create the disjoint sum of planar diagrams.

    The function takes multiple planar diagrams (oriented or not) of the same type and
    generates a new diagram representing their disjoint sum. Attributes are aggregated from the input diagrams,
    and framing is computed or set to None if applicable.

    Raises a ValueError if no diagrams are provided and raises a TypeError if the types
    of the diagrams are inconsistent.

    Parameters:
        knots (tuple[PlanarDiagram | OrientedPlanarDiagram]): A variable number of input planar or
                                                              oriented planar diagrams.

    Returns:
        PlanarDiagram | OrientedPlanarDiagram: A new diagram representing the disjoint sum of
                                               the input diagrams.

    Raises:
        ValueError: If no diagrams are passed to the function.
        TypeError: If the input diagrams have inconsistent types.
    """
    if len(knots) == 0:
        raise ValueError("No diagrams provided")
    if len(knots) == 1:
        return knots[0].copy()

    if len({type(k) for k in knots}) != 1:
        raise TypeError(f"Cannot create a disjoint sum of different type diagrams ({' and '.join({type(k).__name__ for k in knots})})")

    new_knot = type(knots[0])()
    new_node_name_iter = iter(generate_node_names(sum(len(k) for k in knots)))

    # framing
    if any(k.framing is not None for k in knots):
        new_knot.framing = sum(k.framing or 0 for k in knots)


    relabel_dicts = []  # dicts that map the node of the component to the new node in the disjoint sum
    for k in knots:

        new_knot.attr.update(k.attr)  # update attributes
        relabel_dicts.append(relabelling := dict())  # create new node dict for the component

        for node, inst in k.nodes.items():
            relabelling[node] = (node_label := next(new_node_name_iter))
            new_knot.add_node(
                node_for_adding=node_label,
                create_using=type(inst),
                degree=len(inst),
                **inst.attr
            )

        for arc in k.arcs:
            for ep1, ep2 in permutations(arc):
                new_knot.set_endpoint(
                    endpoint_for_setting=(relabelling[ep1.node], ep1.position),
                    adjacent_endpoint=(relabelling[ep2.node], ep2.position),
                    create_using=type(ep2),
                    **ep2.attr
                )

    return (new_knot, relabel_dicts) if return_relabel_dictionaries else new_knot






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

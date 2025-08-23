# knotpy/algorithms/disjoint_union.py

"""Disjoint components and disjoint sums of planar diagrams.

A *disjoint component* is a connected component that shares no nodes (crossings,
vertices, …) with another. The *disjoint sum* of diagrams places them side-by-side
without identifying any nodes or arcs.
"""

__all__ = [
    "number_of_disjoint_components",
    "disjoint_union_decomposition",
    "add_unknot",
    "is_disjoint_union",
    "disjoint_union",
]
__version__ = "0.3"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from itertools import permutations

from knotpy.algorithms.naming import unique_new_node_name, generate_node_names
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.disjoint_union_set import DisjointSetUnion


def add_unknot(k: PlanarDiagram, number_of_unknots: int = 1, inplace: bool = True) -> PlanarDiagram:
    """
    Add one or more unknots disjointly to a diagram.

    Each unknot is represented by a single degree-2 vertex with a loop (two
    opposite endpoints joined).

    Args:
        k: Target diagram.
        number_of_unknots: How many unknots to add.
        inplace: If False, operate on a copy and return it.

    Returns:
        The diagram with the unknots added (same object if ``inplace=True``).
    """
    if not inplace:
        k = k.copy()

    oriented = k.is_oriented()

    for _ in range(number_of_unknots):
        node = unique_new_node_name(k)
        k.add_vertex(node, degree=2)
        # connect the two endpoints of the same vertex
        k.set_endpoint((node, 0), (node, 1), create_using=(IngoingEndpoint if oriented else Endpoint))
        k.set_endpoint((node, 1), (node, 0), create_using=(OutgoingEndpoint if oriented else Endpoint))

    return k


def _disjoint_components_nodes(k: PlanarDiagram) -> list[set]:
    """
    Compute connected components as sets of nodes.

    Args:
        k: Diagram.

    Returns:
        List of node-sets, one per connected component.
    """
    dsu = DisjointSetUnion(k.nodes)
    for ep0, ep1 in k.arcs:
        dsu[ep0.node] = ep1.node
    return list(dsu.classes())


def number_of_disjoint_components(k: PlanarDiagram) -> int:
    """
    Number of connected components.

    Args:
        k: Diagram.

    Returns:
        Count of components.
    """
    return len(_disjoint_components_nodes(k))


def is_disjoint_union(k: PlanarDiagram) -> bool:
    """
    Whether the diagram has more than one connected component.

    Args:
        k: Diagram.

    Returns:
        True if there are ≥ 2 components.
    """
    return number_of_disjoint_components(k) > 1


def disjoint_union_decomposition(k: PlanarDiagram) -> list[PlanarDiagram]:
    """
    Split a diagram into its disjoint (connected) components.

    Components are returned as standalone diagrams. The result is ordered
    deterministically by the tuple of sorted node names in each component.

    Notes:
        If ``k.framing`` is not None, the framing is placed on the first
        returned component and set to 0 on all subsequent ones.

    Args:
        k: Diagram to decompose.

    Returns:
        List of component diagrams.
    """
    components: list[PlanarDiagram] = []

    # Sort deterministically by node-name signature to avoid non-orderable sets
    for comp_nodes in sorted(_disjoint_components_nodes(k), key=lambda s: tuple(sorted(s))):
        g = k.copy()
        if "name" in g.attr:
            del g.attr["name"]
        # Removing all nodes not in this component (incident endpoints fall out)
        g.remove_nodes_from(set(g.nodes) - set(comp_nodes), remove_incident_endpoints=False)
        components.append(g)

    # Put framing only on the first component (if present)
    if components and k.framing is not None:
        components[0].framing = k.framing
        for g in components[1:]:
            g.framing = 0

    return components


def disjoint_union(*knots: PlanarDiagram | OrientedPlanarDiagram, return_relabel_dicts: bool = False
):
    """
    Disjoint sum of multiple diagrams (all of the same type).

    The nodes of each input are relabeled to unique fresh names and placed into
    a single diagram without identifying any nodes or arcs.

    Args:
        *knots: One or more diagrams (all ``PlanarDiagram`` or all ``OrientedPlanarDiagram``).
        return_relabel_dictionaries: If True, also return a list of dictionaries
            mapping old node names (per component) to new node names in the sum.

    Returns:
        The disjoint sum diagram, and optionally the relabeling dictionaries.

    Raises:
        ValueError: If no diagrams are provided.
        TypeError: If input diagrams mix oriented and unoriented types.
    """
    if len(knots) == 0:
        raise ValueError("No diagrams provided.")
    if len(knots) == 1:
        return (knots[0].copy(), [{}]) if return_relabel_dicts else knots[0].copy()

    if len({type(k) for k in knots}) != 1:
        types = ", ".join(sorted({type(k).__name__ for k in knots}))
        raise TypeError(f"Cannot create a disjoint sum of different diagram types ({types}).")

    new_knot = type(knots[0])()
    new_name_iter = iter(generate_node_names(sum(len(k) for k in knots)))

    # framing: sum when any is present; else None
    if any(k.framing is not None for k in knots):
        new_knot.framing = sum(k.framing or 0 for k in knots)

    relabel_dicts: list[dict] = []

    for k in knots:
        new_knot.attr.update(k.attr)

        relabel = {}
        relabel_dicts.append(relabel)

        # create nodes
        for node, inst in k.nodes.items():
            new_name = next(new_name_iter)
            relabel[node] = new_name
            new_knot.add_node(
                node_for_adding=new_name,
                create_using=type(inst),
                degree=len(inst),
                **inst.attr,
            )

        # create arcs
        for arc in k.arcs:
            for ep1, ep2 in permutations(arc):
                new_knot.set_endpoint(
                    endpoint_for_setting=(relabel[ep1.node], ep1.position),
                    adjacent_endpoint=(relabel[ep2.node], ep2.position),
                    create_using=type(ep2),
                    **ep2.attr,
                )

    return (new_knot, relabel_dicts) if return_relabel_dicts else new_knot


if __name__ == "__main__":
    pass
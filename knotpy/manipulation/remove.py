from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import loops

def remove_empty_nodes(k:PlanarDiagram) -> PlanarDiagram:
    """allways inplace"""
    for n in list(k.nodes):
        if not k.nodes[n]:
            k.remove_node(n)
    return k

def remove_arc(k: PlanarDiagram, arc_for_removing: tuple, inplace=True) -> PlanarDiagram:
    """

    Args:
        k:
        arc_for_removing:
        inplace:

    Returns:

    """

    if not inplace:
        k = k.copy()

    k.name = None
    k.remove_arc(arc_for_removing=arc_for_removing)
    return k


def remove_loops(k: PlanarDiagram) -> PlanarDiagram:
    """ Remove loops and return how many loops were removed. Inplace.

    Args:
        k:

    Returns:

    """
    count_removed = 0

    # TODO: speed up, since we compute all loops and remove only one
    while l := loops(k):
        k.remove_arc(l[0])
        count_removed += 1
    k.name = None
    return count_removed





def remove_bivalent_vertex(k:PlanarDiagram, node):

    if k.degree(node) != 2:
        raise ValueError(f"Node {node} is not a bivalent vertex")

    ep_a, ep_b = k.nodes[node]

    k.set_endpoint(ep_a, ep_b)
    k.set_endpoint(ep_b, ep_a)
    k.remove_node(node, remove_incident_endpoints=False)


def remove_bivalent_vertices(k:PlanarDiagram, match_attributes=False):
    """Remove bivalent vertices from knotted graph k
    :param k:
    :param match_attributes: if True, removes bivalent vertices only if all four adjacent/incident endpoints match,
    if False, it removes the bivalent vertices regardless
    :return: None
    """
    if not hasattr(k, "vertices"):
        raise TypeError(f"cannot remove bivalent vertices from an instance of type {type(k)}")

    bivalent_vertices = {node for node in k.vertices if len(k.nodes[node]) == 2}

    while bivalent_vertices:
        node = bivalent_vertices.pop()
        # get the incident endpoints b0 and b1 and the incident endpoints a0 and a1 (ai is the twin of bi for i=0,1)
        b0 = k.endpoint_from_pair((node, 0))
        a0 = k.twin(b0)
        b1 = k.endpoint_from_pair((node, 1))
        a1 = k.twin(b1)

        if match_attributes and (b0.attr == a0.attr == b1.attr == a1.attr):
            continue  # skip removing vertex

        if b0.node == a0.node or b1.node == a1.node:
            continue  # cannot remove loops

        if k.is_oriented() and (type(a0) is type(a1)):
            continue  # skip incoherently ordered endpoints

        k.nodes[a0.node][a0.position] = a1
        k.nodes[a1.node][a1.position] = a0
        k.remove_node(node_for_removing=node, remove_incident_endpoints=False)

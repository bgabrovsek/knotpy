"""
Here are implementations of Skein operations.
The "A"-type smoothing is also referred to as "L_0" smoothing and
the "B"-type smoothing is also referred to as "L_infinity" smoothing,
see [L.H. Kauffman, "State models and the Jones polynomial" Topology , 26 (1987) pp. 395–407]
"""


from knotpy.algorithms.disjoint_sum import add_unknot
from knotpy.algorithms.topology import kinks
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing

def crossing_to_vertex(k: PlanarDiagram, crossing, inplace=False):
    """
    Converts a crossing in a planar diagram to a vertex, by projecting it to a vertex.

    Args:
        k (PlanarDiagram): The planar diagram containing the crossing to be transformed.
        crossing: The crossing that will be converted into a vertex.
        inplace (bool, optional): If True, modifies the PlanarDiagram in place; otherwise,
            creates and returns a copy with the transformation applied.

    Returns:
        PlanarDiagram: The modified PlanarDiagram with the specified crossing converted
        into a vertex.
    """

    #print(k)

    if not inplace:
        k = k.copy()

    c = crossing

    node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
    k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten

    k.add_vertex(c, **node_inst.attr)
    for i, ep in enumerate(node_inst):
        k.set_endpoint((c, i), ep)
    return k

def smoothen_crossing(k: PlanarDiagram, crossing_for_smoothing, method: str, inplace=False):
    """
    Smoothens a specified crossing in a planar diagram using type "A", "B", or oriented ("O") smoothing,
    depending on the method specified. The function modifies the connectivity of the crossing to achieve
    the smoothing and returns a new planar diagram with one less crossing.
    For example, for the crossing [1,3,4,6] and type "A" smoothing, we join the positions (0,1) and
    (2,3). The function will return a knot/link, where we join nodes 1 & 3 and 4 & 6. For type "B", we join positions
    (1, 2) and (3, 0).

    Args:
        k (PlanarDiagram): The planar diagram representing the knot or link.
        crossing_for_smoothing (int): The index or identifier of the crossing in the diagram to smoothen.
        method (str): Specifies the type of smoothing to perform. Can be:
            - "A": Type-A smoothing.
            - "B": Type-B smoothing.
            - "O": Oriented smoothing (applies "B" or "A" based on the diagram's orientation).
        inplace (bool, optional): Indicates whether the operation is performed in-place on the input diagram.
                                  Defaults to False.

    Returns:
        PlanarDiagram: A modified planar diagram with one less crossing after smoothing the specified crossing.

    Raises:
        ValueError: If attempting to perform "A" or "B" smoothing on an oriented diagram, or if
                    an invalid smoothing type is specified for non-oriented diagrams.
        TypeError: If the specified crossing is not of the expected type (Crossing).
    """

    method = method.upper()

    is_oriented = k.is_oriented()

    if is_oriented and method != "O":
        return ValueError(f"Cannot smoothen a crossing by type {method} of an non-oriented diagram")
    if not is_oriented and method != "A" and method != "B":
        raise ValueError(f"Type {method} is an unknown smoothening type (should be 'A' or 'B')")

    c = crossing_for_smoothing

    if method == "O":
        method = "B" if type(k.nodes[c][0]) is type(k.nodes[c][1]) else "A"

    if not isinstance(k.nodes[c], Crossing):
        raise TypeError(f"Cannot smoothen a crossing of type {type(k.nodes[c])}")

    if not inplace:
        k = k.copy()
    node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
    kinks_ = kinks(k, crossing=c)
    k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten

    # TODO: attributes

    if len(kinks_) == 0:
        # there are no kinks

        # is there a circle component around an arc? (does not really depend on the resolution A or b)
        if node_inst[0].node == node_inst[2].node == c:
            k.set_arc((node_inst[1], node_inst[3]))
        elif node_inst[1].node == node_inst[3].node == c:
            k.set_arc((node_inst[0], node_inst[2]))
        else:
            if method == "A":
                # join 0 and 1
                k.set_endpoint(node_inst[0], node_inst[1])  # we should join attributes of [1] and twin of [0]
                k.set_endpoint(node_inst[1], node_inst[0])  # we should join attributes of [0] and twin of [1]
                # join 2 and 3
                k.set_endpoint(node_inst[2], node_inst[3])  # we should join attributes of [3] and twin of [2]
                k.set_endpoint(node_inst[3], node_inst[2])  # we should join attributes of [2] and twin of [3]
            elif method == "B":
                # join 0 and 3
                k.set_endpoint(node_inst[0], node_inst[3])
                k.set_endpoint(node_inst[3], node_inst[0])
                # join 1 and 2
                k.set_endpoint(node_inst[1], node_inst[2])
                k.set_endpoint(node_inst[2], node_inst[1])

    # single kink?
    elif len(kinks_) == 1:
        ep = kinks_.pop()
        if (method == "B") ^ ep.position % 2:
            add_unknot(k)
        k.set_endpoint(node_inst[(ep.position + 1) % 4], node_inst[(ep.position + 2) % 4], **node_inst[(ep.position + 2) % 4].attr)  # just turns out to be so
        k.set_endpoint(node_inst[(ep.position + 2) % 4], node_inst[(ep.position + 1) % 4], **node_inst[(ep.position + 1) % 4].attr)  # just turns out to be so

    # double kink
    else:
        # do kink positions match the join positions
        # TODO: write better
        ep0, ep1 = kinks_
        add_unknot(k, number_of_unknots=1 if (ep0.position % 2) ^ (method == "A") else 2)

    return k


def Kauffman_state_sum(K: PlanarDiagram):
    """
    Calculates the Kauffman state sum for a given planar diagram.

    Args:
        K: A PlanarDiagram object representing the planar diagram of a
            knot or link.

    Returns:
        A float representing the Kauffman state sum for the given planar
        diagram.
    """
    pass





if __name__ == "__main__":
    pass
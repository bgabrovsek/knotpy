"""
Implementations of Skein operations.
The "A"-type smoothing is also referred to as "L_0" smoothing and
the "B"-type smoothing is also referred to as "L_infinity" smoothing,
see [L.H. Kauffman, "State models and the Jones polynomial" Topology , 26 (1987) pp. 395–407]
"""
__all__ = ['smoothen_crossing', 'crossing_to_vertex']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


from knotpy.algorithms.topology import kinks
from knotpy.classes.planardiagram import Diagram, PlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.naming import unique_new_node_name


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

# bivalent: 35% more time (slower)
# def smoothen_crossing(k: PlanarDiagram, crossing_for_smoothing, method: str, inplace=False):
#     """
#     Smoothens a specified crossing in a planar diagram using type "A", "B", or oriented ("O") smoothing,
#     depending on the method specified. The function modifies the connectivity of the crossing to achieve
#     the smoothing and returns a new planar diagram with one less crossing.
#     For example, for the crossing [1,3,4,6] and type "A" smoothing, we join the positions (0,1) and
#     (2,3). The function will return a knot/link, where we join nodes 1 & 3 and 4 & 6. For type "B", we join positions
#     (1, 2) and (3, 0).
#
#     Args:
#         k (PlanarDiagram): The planar diagram representing the knot or link.
#         crossing_for_smoothing (int): The index or identifier of the crossing in the diagram to smoothen.
#         method (str): Specifies the type of smoothing to perform. Can be:
#             - "A": Type-A smoothing.
#             - "B": Type-B smoothing.
#             - "O": Oriented smoothing (applies "B" or "A" based on the diagram's orientation).
#         inplace (bool, optional): Indicates whether the operation is performed in-place on the input diagram.
#                                   Defaults to False.
#
#     Returns:
#         PlanarDiagram: A modified planar diagram with one less crossing after smoothing the specified crossing.
#
#     Raises:
#         ValueError: If attempting to perform "A" or "B" smoothing on an oriented diagram, or if
#                     an invalid smoothing type is specified for non-oriented diagrams.
#         TypeError: If the specified crossing is not of the expected type (Crossing).
#     """
#
#     method = method.upper()
#
#     if k.is_oriented() and method != "O":
#         return ValueError(f"Cannot smoothen a crossing by type {method} of an oriented diagram")
#     if not k.is_oriented() and method != "A" and method != "B":
#         raise ValueError(f"Cannot smoothen a crossing by type {method} of an non-oriented diagram (should be 'A' or 'B')")
#
#     c = crossing_for_smoothing
#
#     if method == "O":
#         method = "B" if type(k.nodes[c][0]) is type(k.nodes[c][1]) else "A"
#
#     if not isinstance(k.nodes[c], Crossing):
#         raise TypeError(f"Cannot smoothen a node of type {type(k.nodes[c])}")
#
#     if not inplace:
#         k = k.copy()
#     node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
#     kinks_ = kinks(k, crossing=c)  # store kinks of the crossing
#
#     attr = [node_inst[i].attr for i in range(4)]
#     twin_attr = [k.twin(node_inst[i]).attr for i in range(4)]
#
#     subdivide_arcs_around_node(k, c)
#     k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten
#     if method == "A":
#         # join 0 and 1
#         k.set_endpoint(node_inst[0], node_inst[1], **(twin_attr[0] | attr[1]))  # we should join attributes of [1] and twin of [0]
#         k.set_endpoint(node_inst[1], node_inst[0], **(twin_attr[1] | attr[0]))  # we should join attributes of [0] and twin of [1]
#         # join 2 and 3
#         k.set_endpoint(node_inst[2], node_inst[3], **(twin_attr[2] | attr[3]))  # we should join attributes of [3] and twin of [2]
#         k.set_endpoint(node_inst[3], node_inst[2], **(twin_attr[2] | attr[2]))  # we should join attributes of [2] and twin of [3]
#     elif method == "B":
#         # join 0 and 3
#         k.set_endpoint(node_inst[0], node_inst[3], **(twin_attr[0] | attr[3]))
#         k.set_endpoint(node_inst[3], node_inst[0], **(twin_attr[3] | attr[0]))
#         # join 1 and 2
#         k.set_endpoint(node_inst[1], node_inst[2], **(twin_attr[1] | attr[2]))
#         k.set_endpoint(node_inst[2], node_inst[1], **(twin_attr[2] | attr[1]))
#
#     remove_bivalent_vertices(k)
#
#     return k


def smoothen_crossing(k: Diagram, crossing_for_smoothing, method: str, inplace=False, **attr) -> Diagram:
    """
    Smoothens a specified crossing in a planar diagram using type "A", "B", or oriented ("O") smoothing,
    depending on the method specified. The function modifies the connectivity of the crossing to achieve
    the smoothing and returns a new planar diagram with one less crossing.
    For example, for the crossing [1,3,4,6] and type "A" smoothing, we join the positions (0,1) and
    (2,3). The function will return a knot/link, where we join nodes 1 & 3 and 4 & 6. For type "B", we join positions
    (1, 2) and (3, 0).

    Args:
        k (PlanarDiagram): The planar diagram representing the knot or link.
        crossing_for_smoothing: The index or identifier of the crossing in the diagram to smoothen.
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
        raise ValueError(f"Cannot smoothen a crossing by type {method} of an non-oriented diagram")
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

    attr0 = (k.twin(node_inst[1]).attr | node_inst[0].attr | attr) if method == "A" else (k.twin(node_inst[3]).attr | node_inst[0].attr | attr)
    attr1 = (k.twin(node_inst[0]).attr | node_inst[1].attr | attr) if method == "A" else (k.twin(node_inst[2]).attr | node_inst[1].attr | attr)
    attr2 = (k.twin(node_inst[3]).attr | node_inst[2].attr | attr) if method == "A" else (k.twin(node_inst[1]).attr | node_inst[2].attr | attr)
    attr3 = (k.twin(node_inst[2]).attr | node_inst[3].attr | attr) if method == "A" else (k.twin(node_inst[0]).attr | node_inst[3].attr | attr)

    k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten

    # TODO: attributes

    if len(kinks_) == 0:
        # there are no kinks

        # is there a circle component around an arc? (does not really depend on the resolution A or b)
        if node_inst[0].node == node_inst[2].node == c:
            k.set_endpoint(node_inst[1], node_inst[3], **(attr3 | (attr0 if method == "A" else attr2)))
            k.set_endpoint(node_inst[3], node_inst[1], **(attr1 | (attr2 if method == "A" else attr0)))
            #k.set_arc((node_inst[1], node_inst[3]))
        elif node_inst[1].node == node_inst[3].node == c:
            k.set_endpoint(node_inst[0], node_inst[2], **(attr2 | (attr1 if method == "A" else attr3)))
            k.set_endpoint(node_inst[2], node_inst[0], **(attr0 | (attr3 if method == "A" else attr1)))
            #k.set_arc((node_inst[0], node_inst[2]))
        else:
            if method == "A":
                # join 0 and 1
                k.set_endpoint(node_inst[0], node_inst[1], **attr1)  # we should join attributes of [1] and twin of [0]
                k.set_endpoint(node_inst[1], node_inst[0], **attr0)  # we should join attributes of [0] and twin of [1]
                # join 2 and 3
                k.set_endpoint(node_inst[2], node_inst[3], **attr3)  # we should join attributes of [3] and twin of [2]
                k.set_endpoint(node_inst[3], node_inst[2], **attr2)  # we should join attributes of [2] and twin of [3]
            elif method == "B":
                # join 0 and 3
                k.set_endpoint(node_inst[0], node_inst[3], **attr3)
                k.set_endpoint(node_inst[3], node_inst[0], **attr0)
                # join 1 and 2
                k.set_endpoint(node_inst[1], node_inst[2], **attr2)
                k.set_endpoint(node_inst[2], node_inst[1], **attr1)

    # single kink?
    elif len(kinks_) == 1:
        attr = [attr0, attr1, attr2, attr3]
        ep = kinks_.pop()

        if (method == "B") ^ ep.position % 2:
            # add unknot
            vertex = unique_new_node_name(k)
            k.add_vertex(vertex, degree=2)
            type1 = create_using=type(node_inst[(ep.position + 0) % 4])  # this is just a guess
            type0 = type1.reverse_type()

            #type0 = IngoingEndpoint if type(type1) is OutgoingEndpoint else OutgoingEndpoint
            # here I am not sure about the attributes, but we defined 0 to be the outer endpoint and 1 to be the inner endpoint of the unknot
            k.set_endpoint((vertex, 0), (vertex, 1), create_using=type1,**attr[(ep.position + 0) % 4])
            k.set_endpoint((vertex, 1), (vertex, 0), create_using=type0, **attr[(ep.position + 3) % 4])

            k.set_endpoint(node_inst[(ep.position + 1) % 4], node_inst[(ep.position + 2) % 4],
                           **attr[(ep.position + 2) % 4])  # just turns out to be so
            k.set_endpoint(node_inst[(ep.position + 2) % 4], node_inst[(ep.position + 1) % 4],
                           **attr[(ep.position + 1) % 4])  # just turns out to be so
        else:
            k.set_endpoint(node_inst[(ep.position + 1) % 4], node_inst[(ep.position + 2) % 4],
                           **(attr[(ep.position + 0) % 4] | attr[(ep.position + 2) % 4]))  # just turns out to be so
            k.set_endpoint(node_inst[(ep.position + 2) % 4], node_inst[(ep.position + 1) % 4],
                           **(attr[(ep.position + 3) % 4] | attr[(ep.position + 1) % 4]))  # just turns out to be so

    # double kink
    else:
        # do kink positions match the join positions
        # TODO: write better
        #ep0, ep1 = kinks_
        # add_unknot(k, number_of_unknots=1 if (ep0.position % 2) ^ (method == "A") else 2)

        ep = kinks_.pop()
        type1 = type(node_inst[(ep.position + 0) % 4])  # this is just a guess
        type0 = type1.reverse_type() #IngoingEndpoint if type(type1) is OutgoingEndpoint else OutgoingEndpoint

        if node_inst[0].position == 1:


            if method == "A":

                k.add_vertex(u := unique_new_node_name(k), degree=2)
                k.add_vertex(v := unique_new_node_name(k), degree=2)
                # not sure about attr
                k.set_endpoint((u, 0), (u, 1), create_using=type1, **attr0)
                k.set_endpoint((u, 1), (u, 0), create_using=type0, **attr1)
                k.set_endpoint((v, 0), (v, 1), create_using=type1, **attr2)
                k.set_endpoint((v, 1), (v, 0), create_using=type0, **attr3)
            else:
                k.add_vertex(u := unique_new_node_name(k), degree=2)
                k.set_endpoint((u, 0), (u, 1), create_using=type1, **(attr0 | attr2))
                k.set_endpoint((u, 1), (u, 0), create_using=type0, **(attr1 | attr3))
        else:
            if method == "A":
                k.add_vertex(u := unique_new_node_name(k), degree=2)
                k.set_endpoint((u, 0), (u, 1), create_using=type1, **(attr1 | attr3))
                k.set_endpoint((u, 1), (u, 0), create_using=type0, **(attr0 | attr2))
            else:
                k.add_vertex(u := unique_new_node_name(k), degree=2)
                k.add_vertex(v := unique_new_node_name(k), degree=2)
                k.set_endpoint((u, 0), (u, 1), create_using=type1, **attr3)
                k.set_endpoint((u, 1), (u, 0), create_using=type0, **attr0)
                k.set_endpoint((v, 0), (v, 1), create_using=type1, **attr1)
                k.set_endpoint((v, 1), (v, 0), create_using=type0, **attr2)


    return k


if __name__ == "__main__":
    pass
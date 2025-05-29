from knotpy import to_knotpy_notation
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Vertex
from knotpy.manipulation.rewire import pull_and_plug_endpoint

def contract_arc(k: PlanarDiagram, arc_for_contracting, inplace=True) -> PlanarDiagram:
    """
    Contracts a specific arc in a PlanarDiagram by merging its endpoints into one vertex.

    Args:
        k (PlanarDiagram): The planar diagram in which the arc contraction will be performed.
        arc_for_contracting (Tuple[Tuple[int, int], Tuple[int, int]]): The arc to be contracted,
            represented as a tuple of two endpoints, where each endpoint is a tuple consisting
            of a node identifier and a position index. The first tuple is the 'contracted'
            endpoint that remains after contraction, and the second tuple is the endpoint to
            be removed.
        inplace (bool, optional): If True, the operation is performed directly on the input
            PlanarDiagram object. If False, a copy of the input diagram will be modified, and
            the original remains unchanged. Defaults to True.

    Returns:
        PlanarDiagram: The modified planar diagram after the arc contraction if `inplace` is
        False, or the same (mutated) diagram if `inplace` is True.

    Raises:
        TypeError: If either of the endpoints specified in `arc_for_contracting` does not
        belong to a vertex in the planar diagram.
        ValueError: If the arc specified forms a loop (i.e., the endpoints are on the same
        vertex) and cannot be contracted.
    """
    if not inplace:
        k = k.copy()


    # print("++++ CONTRACTING ****")
    # print(to_knotpy_notation(k), arc_for_contracting)

    #k.name = None
    if "name" in k.attr:
        del k.attr["name"]

    c_ep, del_ep = arc_for_contracting  # "contracted" endpoint c_ep (remains) and deleted endpoint d_ep (removed)

    c_node, c_pos = c_ep = k.endpoint_from_pair(c_ep)  # will be kept
    del_node, del_pos = del_ep = k.endpoint_from_pair(del_ep)  # will be removed

    del_node_inst = k.nodes[del_node]

    if not isinstance(k.nodes[c_node], Vertex) or not isinstance(k.nodes[del_node], Vertex):
        raise TypeError(f"Cannot contract arc since either '{c_node}' or '{del_node}' is not a Vertex.")

    if c_node == del_node:
        raise ValueError("Cannot contract a loop")

    k.remove_arc(arc_for_contracting)

    index = del_pos
    while del_node_inst:

        # print(">", k)
        # print(" src", (del_node, max(index, -2) % len(del_node_inst)))
        # print(" dst", (c_node, c_pos))
        # print("***", to_knotpy_notation(k))
        # if (del_node, max(index, -1) % len(del_node_inst)) == ("a",0 ):
        #     pass


        index -= 1
        pull_and_plug_endpoint(k,
                               source_endpoint=(del_node, max(index, -1) % len(del_node_inst)),
                               destination_endpoint=(c_node, c_pos))

        # print("=", k)

        #assert len({ep for ep in k.endpoints if "color" in ep}) == 2, f"{k}"

    # Finally, remove the "other" endpoint
    k.remove_node(del_node, remove_incident_endpoints=False)

    return k


if __name__ == "__main__":

    # contracting an endpoint from a graph with a loop in the vertex that is removed
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1x2,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    r.set_arcs_from("y0e0,y1f0,y2d0,y3a0,y4y5,y6g0,y7h0")
    contract_arc(k, (("y", 2), ("x", 3)))
    if k != r:
        print(k, "(wrong)")
        print(r)
    else:
        print("ok")


    # contracting an endpoint from a nice graph
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1f0,y3g0,y4h0")
    r.set_arcs_from("y0e0,y1f0,y2d0,y3a0,y4b0,y5c0,y6g0,y7h0")
    contract_arc(k, (("y",2),("x",3)))
    if k != r:
        print(k, "(wrong")
    else:
        print("ok")


    #contracting an endpoint from a graph with a loop in the point that remains
    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0y1,y3g0,y4h0")
    r.set_arcs_from("y0y1,y2d0,y3a0,y4b0,y5c0,y6g0,y7h0")
    contract_arc(k, (("y",2),("x",3)))
    if k != r:
        print(k, "(wrong)")
    else:
        print("ok")

    k, r = PlanarDiagram(), PlanarDiagram()
    k.set_arcs_from("x0a0,x1b0,x2c0,x4d0,x3y2,y0e0,y1y4,y3g0")
    r.set_arcs_from("y0e0,y1y7,y2d0,y3a0,y4b0,y5c0,y6g0")
    contract_arc(k, (("y",2),("x",3)))
    if k != r:
        print(k, "(wrong)")
        print(r)
    else:
        print("ok")



"""
Skein operations:
 - smoothing crossings by A/B smoothening
"""

from knotpy.algorithms.components_disjoint import add_unknot
from knotpy.algorithms.structure import kinks
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint

def smoothen_crossing(k: PlanarDiagram, crossing_for_smoothing, method: str, in_place=False):
    """Smoothen the crossing with "type A" or "type B" smoothing. Connect endpoints of crossings with positions given by
    join_positions. For example, for the crossing [1,3,4,6] and type "A" smoothing, we join the positions (0,1) and
    (2,3). The function will return a knot/link, where we join nodes 1 & 3 and 4 & 6. For type "B", we join positions
    (1, 2) and (3, 0).
    :param k:  planar diagram,
    :param crossing_for_smoothing:
    :param method: "A" for type-A smoothing or "B" for type-B smoothing or "O" for oriented smoothing.
    :return: planar diagram with one less crossing than k.
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

    if not in_place:
        k = k.copy()
    node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
    kinks_ = kinks(k, of_crossing=c)
    k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten

    #print(method, kinks_)


    if len(kinks_) == 0:
        # there are no kinks

        # is there a circle component around an arc? (does not really depend on the resolution A or b)
        if node_inst[0].node == node_inst[2].node == c:
            #print("circ",1,3)
            k.set_arc((node_inst[1], node_inst[3]))
        elif node_inst[1].node == node_inst[3].node == c:
            #print("circ", 0, 2)
            k.set_arc((node_inst[0], node_inst[2]))
        else:
            if method == "A":
                #print("a")
                # join 0 and 1
                k.set_endpoint(node_inst[0], node_inst[1])  # we should join attributes of [1] and twin of [0]
                k.set_endpoint(node_inst[1], node_inst[0])  # we should join attributes of [0] and twin of [1]
                # join 2 and 3
                k.set_endpoint(node_inst[2], node_inst[3])  # we should join attributes of [3] and twin of [2]
                k.set_endpoint(node_inst[3], node_inst[2])  # we should join attributes of [2] and twin of [3]
            elif method == "B":
                #print("b")
                # join 0 and 3
                k.set_endpoint(node_inst[0], node_inst[3])
                k.set_endpoint(node_inst[3], node_inst[0])
                # join 1 and 2
                k.set_endpoint(node_inst[1], node_inst[2])
                k.set_endpoint(node_inst[2], node_inst[1])

    # single kink?
    elif len(kinks_) == 1:
        #print("kink")
        ep = kinks_.pop()
        if (method == "B") ^ ep.position % 2:
            #print("a")
            add_unknot(k)
        #print("else")
        k.set_endpoint(node_inst[(ep.position + 1) % 4], node_inst[(ep.position + 2) % 4], **node_inst[(ep.position + 2) % 4].attr)  # just turns out to be so
        k.set_endpoint(node_inst[(ep.position + 2) % 4], node_inst[(ep.position + 1) % 4], **node_inst[(ep.position + 1) % 4].attr)  # just turns out to be so

    # double kink
    else:
        # do kink positions match the join positions
        # TODO: write better
        #print("double")
        ep0, ep1 = kinks_
        add_unknot(k, number_of_unknots=1 if (ep0.position % 2) ^ (method == "A") else 2)

    #print("result", k)


    return k


if __name__ == "__main__":

    from knotpy.classes import PlanarDiagram




    k = PlanarDiagram()
    k.add_crossing("a")
    k.set_arcs_from([[("a", 0), ("a", 1)], [("a", 2), ("a", 3)]])



    print(k)

    print("A")

    print(smoothing_type_A(k, "a"))

    print("B")

    print(smoothing_type_B(k, "a"))

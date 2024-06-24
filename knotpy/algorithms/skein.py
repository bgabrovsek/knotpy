"""
Skein operations:
 - smoothing crossings by A/B smoothening
"""

from knotpy.algorithms.components_disjoint import add_unknot_in_place
from knotpy.algorithms.structure import kinks
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing


# _skein_aliases = {"0": ["0", "l0", "l_0", "zero", "a", "type a"],
#                   "∞": ["inf", "l_inf", "l∞", "l_∞", "∞", "b", "type b"]}
# _reversed_skein_aliases = {val: key for key in _skein_aliases for val in _skein_aliases[key]}
#
#
# def _smoothing(k, crossing_for_smoothing, join_positions: tuple):
#     """
#     :param k: knotted planar diagram instance
#     :param crossing_for_smoothing: crossing for smoothing
#     :param join_positions: tuple of tuples, the tuple ((0, 1), (2, 3) joins endpoints 0 & 1 and 2 & 3
#     :return: smoothened knot/link
#     """
#     # TODO: attributes
#     # TODO: make faster version, where we ignore kinks in the case we know the knot is simplified
#
#     _debug = False
#
#     c = crossing_for_smoothing
#     j = join_positions
#
#     if _debug:
#         print("Skein on", k)
#         print("  on positions", j, "on crossing", c)
#
#     if k.degree(c) != 4:
#         raise ValueError(f"Cannot perform a skein smoothing on a {k.degree(c)} degree node.")
#
#     k = k.copy()
#     node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
#     kinks_ = tuple(kinks(k, of_node=c))
#     k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten
#
#     if _debug:
#         print("  kinks:", kinks_)
#
#     # single or double kink?
#     if len(kinks_) == 0:
#         k.set_arc((node_inst[j[0][0]], node_inst[j[0][1]]))
#         k.set_arc((node_inst[j[1][0]], node_inst[j[1][1]]))
#
#
#     # single kink?
#     elif len(kinks_) == 1:
#         position = kinks_[0][0].position
#         # do kink positions match any of the join positions?
#         if frozenset((position, (position + 3) & 3)) in set(frozenset(_) for _ in j):
#             add_unknot_in_place(k)
#         k.set_arc((node_inst[(position + 1) & 3], node_inst[(position + 2) & 3]))
#
#     # double kink
#     else:
#         # a double kink resolves to one or two unknots
#         add_unknot_in_place(k)
#         # do kink positions match the join positions?
#         if set(frozenset(_) for _ in j) == set(frozenset((kinks_[i][0].position, (kinks_[i][0].position + 3) & 3))
#                                                for i in (0, 1)):
#             add_unknot_in_place(k)
#
#     if _debug:
#         print("  result:", k)
#
#     return k

    #
    #
    # # double kink?
    # if c_inst[0].node == c_inst[1].node == c_inst[2].node == c_inst[3].node == c:
    #     pass
    #
    # elif c_inst[join_positions[0][0]].node
    #
    #
    #
    #
    # for pos_a, pos_b in join_positions:
    #     if c_inst[pos_a].node == c_inst[pos_a].node == c:  # is a kink?
    #         k.add_bivalent_node(node := name_for_new_node(k))
    #         k.set_arc(((node, 0), (node, 1)), **(c_inst[pos_b] | c_inst[pos_a]))  # add trivial component, "circle"
    #     else:
    #         #!!!!!
    #         print(c_inst, pos_a, pos_b)
    #         k.set_arc((c_inst[pos_a], c_inst[pos_b]))  # join the arcs, but do not copy the attributes (?)
    #
    # return k
    #

def smoothen_crossing(k: PlanarDiagram, crossing_for_smoothing, method: str):
    """Smoothen the crossing with "type A" or "type B" smoothing. Connect endpoints of crossings with positions given by
    join_positions. For example, for the crossing [1,3,4,6] and type "A" smoothing, we join the positions (0,1) and
    (2,3). The function will return a knot/link, where we join nodes 1 & 3 and 4 & 6. For type "B", we join positions
    (1, 2) and (3, 0).
    :param k:  planar diagram,
    :param crossing_for_smoothing:
    :param method: "A" for type-A smoothing or "B" for type-B smoothing.
    :return: planar diagram with one less crossing than k.
    """
    method = method.upper()
    if method == "A":
        j0, j1 = (0, 1), (2, 3)  # join positions
    elif method == "B":
        j0, j1 = (1, 2), (3, 0)  # join positions
    else:
        raise ValueError(f"Type {method} is an unknown smoothening type (should be 'A' or 'B')")

    c = crossing_for_smoothing

    if not isinstance(k.nodes[c], Crossing):
        raise TypeError(f"Cannot smoothen a crossing of type {type(k.nodes[c])}")

    #print(k, "for crossing", c)


    k = k.copy()
    node_inst = k.nodes[c]  # keep the node/crossing instance for arc information
    kinks_ = kinks(k, of_crossing=c)
    k.remove_node(c, remove_incident_endpoints=False)  # the adjacent arcs will be overwritten

    #print(method, kinks_)

    # single or double kink?
    if len(kinks_) == 0:

        # is there a circle component? (does not really depend on the resolution A or b)
        if node_inst[0].node == node_inst[2].node == c:
            k.set_arc((node_inst[1], node_inst[3]))
        elif node_inst[1].node == node_inst[3].node == c:
            k.set_arc((node_inst[0], node_inst[2]))
        else:
            k.set_arc((node_inst[j0[0]], node_inst[j0[1]]))
            k.set_arc((node_inst[j1[0]], node_inst[j1[1]]))

    # single kink?
    elif len(kinks_) == 1:
        # TODO: could be written better
        ep = kinks_.pop()
        kink_pos = {ep.position, (ep.position - 1) % 4}  #{position, (position + 3) % 4}  # why -1 mod 4?
        if kink_pos == set(j0) or kink_pos == set(j1):
            add_unknot_in_place(k)
        cp1, cp2 = {0, 1, 2, 3} - kink_pos  # complementary positions
        k.set_arc((node_inst[cp1], node_inst[cp2]))  # join

    # double kink
    else:
        # do kink positions match the join positions
        # TODO: write better
        ep0, ep1 = kinks_
        kink0_pos = {ep0.position, (ep0.position - 1) % 4}  #{kinks_[0][0].position, (kinks_[0][0].position + 3) % 4}
        kink1_pos = {ep1.position, (ep1.position - 1) % 4}  #{kinks_[1][0].position, (kinks_[1][0].position + 3) % 4}

        # a double kink resolves to one or two unknots
        if kink0_pos == set(j0) and kink1_pos == set(j1) or kink0_pos == set(j1) and kink1_pos == set(j0):  # can check less things
            add_unknot_in_place(k, number_of_unknots=2)
        else:
            add_unknot_in_place(k, number_of_unknots=1)

    #print("result", k)


    return k
#
#
# def smoothing_type_A(k, crossing_for_smoothing):
#     """Smoothen the crossing with "type A" (L_0) smoothing.
#     :param k: knot
#     :param crossing_for_smoothing:
#     :return: smoothened knot
#     """
#     return _smoothing(k, crossing_for_smoothing, join_positions=((0, 1), (2, 3)))
#
#
# def smoothing_type_B(k, crossing_for_smoothing):
#     """Smoothen the crossing with "type A" (L_infinity) smoothing .
#     :param k: knot
#     :param crossing_for_smoothing:
#     :return: smoothened knot
#     """
#     return _smoothing(k, crossing_for_smoothing, join_positions=((1, 2), (3, 0)))


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

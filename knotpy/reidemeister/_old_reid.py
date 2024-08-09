from itertools import chain
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.algorithms.components_disjoint import add_unknot
from knotpy.sanity import sanity_check

__all__ = ["reidemeister_1_remove_kink",
           "reidemeister_1_add_kink",
           "reidemeister_2_unpoke",
           "reidemeister_2_poke",
           "reidemeister_3"
           ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

_DEBUG_REID = False

_CHECK_SANITY = True

def reidemeister_1_add_kink(k: PlanarDiagram, endpoint, sign=None, inplace=False):
    """Add a new kink at endpoint of sign inside the region endpoint belongs to.
    :param k:
    :param endpoint:
    :param sign:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return:
    """



    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot add kink in instance of type {type(k)}")

    if not isinstance(endpoint, Endpoint):
        raise TypeError(f"Cannot add kink in endpoint of type {type(endpoint)}")

    if not isinstance(sign, int):
        raise TypeError(f"Cannot add kink of sign of type {type(sign)}")

    if not inplace:
        k = k.copy()

    DEBUG = _DEBUG_REID or False
    if DEBUG: print("R1 add kink at", endpoint, "with sign", sign, k)

    if sign != 1 and sign != -1:
        raise TypeError(f"Cannot add kink of sign {sign}")



    if sign is None:
        endpoint, sign = endpoint

    twin_endpoint = k.twin(endpoint)
    #adj_endpoint = #k.arcs[endpoint][0]
    node = name_for_new_node(k)
    k.add_crossing(node)
    # TODO: ORIENTATION
    if sign > 0:
        k.set_arc(((node, 0), (node, 1)))
        k.set_arc(((node, 2), twin_endpoint))
        k.set_arc(((node, 3), endpoint))
    elif sign < 0:
        k.set_arc(((node, 1), (node, 2)))
        k.set_arc(((node, 3), twin_endpoint))
        k.set_arc(((node, 0), endpoint))
    else:
        raise ValueError(f"Unsupported crossing sign {sign}.")

    k.framing -= sign


    if DEBUG:
        print("R1 result", k)

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after add kink:", k)
            sanity_check(k)

    return k


def reidemeister_2_unpoke(k: PlanarDiagram, face: list, inplace=False) -> None:
    """Perform a unpoke (Reidemeister type II move) on the endpoints that define a bigon poke region.
        :param k: knotted planar diagram object
        :param face: a list of the two endpoints of the poke region
        :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.

        :return: knot k with two fewer crossings
        """

    if not inplace:
        k = k.copy()

    ep_a, ep_b = face
    twin_a, twin_b = k.twin(ep_a), k.twin(ep_b)


    DEBUG = _DEBUG_REID or False
    if DEBUG: print("R2 unpoke", k, face)


    # were instances or tuples provided?
    if not isinstance(ep_a, Endpoint) or not isinstance(ep_b, Endpoint):
        ep_a, ep_b = k.twin(twin_a), k.twin(twin_b)

    # a "jump" is the endpoint on the other side of the crossing (on the same edge/strand)
    jump_a = k.endpoint_from_pair((ep_a.node, (ep_a.position + 2) % 4))
    jump_b = k.endpoint_from_pair((ep_b.node, (ep_b.position + 2) % 4))
    jump_twin_a = k.endpoint_from_pair((twin_a.node, (twin_a.position + 2) % 4))
    jump_twin_b = k.endpoint_from_pair((twin_b.node, (twin_b.position + 2) % 4))

    twin_jump_a = k.twin(jump_a)  # twin jump a
    twin_jump_b = k.twin(jump_b)  # twin jump b
    twin_jump_twin_a = k.twin(jump_twin_a)  # twin jump twin a
    twin_jump_twin_b = k.twin(jump_twin_b)  # twin jump twin b

    k.remove_node(ep_a.node, remove_incident_endpoints=False)
    k.remove_node(ep_b.node, remove_incident_endpoints=False)

    if DEBUG:
        print("a", ep_a, "b", ep_b, "ta", twin_a, "tb",twin_b, "ja", jump_a, "jb", jump_b,  "tja",twin_jump_a, "tjb", twin_jump_b, "jta", jump_twin_a, "jtb", jump_twin_b, "tjta", twin_jump_twin_a, "tjtb", twin_jump_twin_b)


    def _set_arc(a:Endpoint, b:Endpoint):
        """ set endpoint with copied type and attributes"""
        k.set_endpoint(endpoint_for_setting=a, adjacent_endpoint=(b.node, b.position), create_using=type(b), **b.attr)
        k.set_endpoint(endpoint_for_setting=b, adjacent_endpoint=(a.node, a.position), create_using=type(a), **a.attr)

    if twin_jump_twin_a is jump_b and twin_jump_twin_b is jump_a:  # double kink?
        add_unknot(k)

    elif twin_jump_twin_a is jump_b:  # single kink at ep_a
        _set_arc(twin_jump_a, twin_jump_twin_b)

    elif twin_jump_twin_b is jump_a:  # single kink at ep_b
        _set_arc(twin_jump_b, twin_jump_twin_a)

    elif twin_jump_a is jump_twin_a and twin_jump_b is jump_twin_b:  # two unknots overlapping
        add_unknot(k, number_of_unknots=2)

    elif jump_a is twin_jump_b:  # "x"-type connected
        _set_arc(twin_jump_twin_a, twin_jump_twin_b)

    elif jump_twin_a is twin_jump_twin_b:  # "x"-type connected
        _set_arc(twin_jump_a, twin_jump_b)

    elif twin_jump_a is jump_twin_a:  # one unknot overlapping on strand a
        _set_arc(twin_jump_twin_b, twin_jump_b)
        add_unknot(k)

    elif twin_jump_b is jump_twin_b:  # one unknot overlapping on strand b
        _set_arc(twin_jump_twin_a, twin_jump_a)
        add_unknot(k)

    else:  # "normal" R2 move, all four external endpoints are distinct
        _set_arc(twin_jump_twin_a, twin_jump_a)
        _set_arc(twin_jump_twin_b, twin_jump_b)

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after poke:", k)
            sanity_check(k)

    return k

def _reversed_endpoint_type(ep):
    if type(ep) is Endpoint or ep is Endpoint:
        return Endpoint
    if type(ep) is OutgoingEndpoint or ep is OutgoingEndpoint:
        return IngoingEndpoint
    if type(ep) is IngoingEndpoint or ep is IngoingEndpoint:
        return OutgoingEndpoint
    raise TypeError()


def reidemeister_2_poke(k: PlanarDiagram, endpoint_over, endpoint_under=None, inplace=False):
    """
    :param k:
    :param endpoint_over:
    :param endpoint_under:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.

    :return:
    """

    DEBUG = _DEBUG_REID or False

    if not inplace:
        k = k.copy()

    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot add poke in instance of type {type(k)}")

    if not isinstance(endpoint_over, Endpoint) or not isinstance(endpoint_under, Endpoint):
        raise TypeError(f"Cannot add poke in endpoints of type {type(endpoint_over)} and {type(endpoint_under)}.")


    if DEBUG: print("R2 poke kink", k, endpoint_over, endpoint_under)

    if endpoint_under is None:
        endpoint_over, endpoint_under = endpoint_over

    # get endpoint instances and their twins
    twin_o_node, twin_o_pos = twin_o = k.twin(endpoint_over)
    twin_u_node, twin_u_pos = twin_u = k.twin(endpoint_under)
    ep_o_node, ep_o_pos = ep_o = k.twin(twin_o)  # get instance of endpoint_over
    ep_u_node, ep_u_pos = ep_u = k.twin(twin_u)  # get instance of endpoint_under

    if DEBUG:
        print("Over", endpoint_over, "twin", twin_o, "under", endpoint_under, "twin", twin_u)

    # get types (endpoint or ingoing/outgoing endpoint)
    type_o, rev_o = type(ep_o), _reversed_endpoint_type(ep_o)
    type_u, rev_u = type(ep_u), _reversed_endpoint_type(ep_u)

    # create two new crossings
    node_e = name_for_new_node(k)
    k.add_crossing(node_e)
    node_f = name_for_new_node(k)
    k.add_crossing(node_f)


    if DEBUG:
        print("Over", endpoint_over, "twin", twin_o, "under", endpoint_under, "twin", twin_u, "new nodes", node_e, node_f)


    # a poke on one arc
    same_arc = (twin_u == ep_o and twin_o == ep_u)


    # set endpoints for node "e"
    if not same_arc:
        k.set_endpoint(endpoint_for_setting=(node_e, 0), adjacent_endpoint=(twin_u_node, twin_u_pos), create_using=rev_u, **twin_u.attr)
    k.set_endpoint(endpoint_for_setting=(node_e, 1), adjacent_endpoint=(node_f, 1), create_using=rev_o)
    k.set_endpoint(endpoint_for_setting=(node_e, 2), adjacent_endpoint=(node_f, 0), create_using=type_u)
    k.set_endpoint(endpoint_for_setting=(node_e, 3), adjacent_endpoint=(ep_o_node, ep_o_pos), create_using=type_o, **ep_o.attr)

    # set endpoints for node "f"
    k.set_endpoint(endpoint_for_setting=(node_f, 0), adjacent_endpoint=(node_e, 2), create_using=rev_u)
    k.set_endpoint(endpoint_for_setting=(node_f, 1), adjacent_endpoint=(node_e, 1), create_using=type_o)
    k.set_endpoint(endpoint_for_setting=(node_f, 2), adjacent_endpoint=(ep_u_node, ep_u_pos), create_using=type_u, **ep_u.attr)
    if not same_arc:
        k.set_endpoint(endpoint_for_setting=(node_f, 3), adjacent_endpoint=(twin_o_node, twin_o_pos), create_using=rev_o, **twin_o.attr)

    # set endpoints for outside nodes
    k.set_endpoint(endpoint_for_setting=(ep_o_node, ep_o_pos), adjacent_endpoint=(node_e, 3), create_using=rev_o)
    k.set_endpoint(endpoint_for_setting=(ep_u_node, ep_u_pos), adjacent_endpoint=(node_f, 2), create_using=rev_u)
    if not same_arc:
        k.set_endpoint(endpoint_for_setting=(twin_o_node, twin_o_pos), adjacent_endpoint=(node_f, 3), create_using=type_o)
        k.set_endpoint(endpoint_for_setting=(twin_u_node, twin_u_pos), adjacent_endpoint=(node_e, 0), create_using=type_u)
    else:
        k.set_endpoint(endpoint_for_setting=(node_e, 0), adjacent_endpoint=(node_f, 3), create_using=rev_u)
        k.set_endpoint(endpoint_for_setting=(node_f, 3), adjacent_endpoint=(node_e, 0), create_using=rev_o)


    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after poke:", k)
            sanity_check(k)


    return k


def reidemeister_3(k, face, inplace=False):
    """Perform a Reidemeister III move on a non-alternating triangular region.
    :param k:
    :param face:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return:
    """

    DEBUG = _DEBUG_REID or False

    if DEBUG: print("R3", k, face)


    if k.is_oriented():
        raise ValueError("Oriented not yet supported")

    if not inplace:
        k = k.copy()

    # if len(region) != 3:
    #     raise ValueError(f"Cannot perform an Reidemeister III move on a region of length {len(region)}.")

    #triangle_nodes = {ep.node for ep in region}
    node_a, pos_a = face[0]
    node_b, pos_b = face[1]
    node_c, pos_c = face[2]

    area_nodes = {node_a, node_b, node_c}

    # redirect endpoints on arcs inside the area
    new_inner_endpoints = {
        (node_a, (pos_a + 1) % 4): (node_b, (pos_b + 2) % 4),  # (node, position + 1) -> (next node, next position + 2)
        (node_a, (pos_a + 2) % 4): (node_c, (pos_c + 1) % 4),  # (node, position + 2) -> (previous node, previous position + 1)
        (node_b, (pos_b + 1) % 4): (node_c, (pos_c + 2) % 4),
        (node_b, (pos_b + 2) % 4): (node_a, (pos_a + 1) % 4),
        (node_c, (pos_c + 1) % 4): (node_a, (pos_a + 2) % 4),
        (node_c, (pos_c + 2) % 4): (node_b, (pos_b + 1) % 4),
    }
    #print("new inner", new_inner_endpoints)

    # redirect the endpoints of the crossings on to the triangle face, directed outside (away from the triangle)
    new_outer_endpoints = {
        (node_a, pos_a): tuple(k.nodes[node_c][(pos_c + 1) % 4]),  # (node, position) -> k.nodes[previous node][previous position - 1]
        (node_a, (pos_a - 1) % 4): tuple(k.nodes[node_b][(pos_b + 2) % 4]),  # (node, position - 1) -> k.nodes[next node][next position + 2]
        (node_b, pos_b): tuple(k.nodes[node_a][(pos_a + 1) % 4]),
        (node_b, (pos_b - 1) % 4): tuple(k.nodes[node_c][(pos_c + 2) % 4]),
        (node_c, pos_c): tuple(k.nodes[node_b][(pos_b + 1) % 4]),
        (node_c, (pos_c - 1) % 4): tuple(k.nodes[node_a][(pos_a + 2) % 4]),
    }

    #print("new outer", new_outer_endpoints)


    # "outer" endpoints change if they point to a crossing of the triangle face
    new_outer_endpoints.update(
        {src_ep: (new_inner_endpoints[dst_ep][0], (new_inner_endpoints[dst_ep][1] + 2) % 4)
         for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] in area_nodes}
    )

    #print("new outer", new_outer_endpoints)


    # redirect endpoints that do not lie on the triangle (are incident to it)
    new_external_endpoints = {
        dst_ep: src_ep for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] not in area_nodes
    }

    #print("new external", new_external_endpoints)


    # new_external_endpoints = {
    #     dest_ep: src_ep if dest_ep[0] not in area_nodes else
    #     for src_ep, dest_ep in new_outer_endpoints.items() if
    # }

    for src_ep, dst_ep in chain(new_inner_endpoints.items(), new_outer_endpoints.items(), new_external_endpoints.items()):
        #print("setting", src_ep, "->", dst_ep)
        k.set_endpoint(
            endpoint_for_setting=src_ep,
            adjacent_endpoint=dst_ep,
            create_using=type(k.nodes[dst_ep[0]][dst_ep[1]]),  # use old type of endpoint
            **k.nodes[dst_ep[0]][dst_ep[1]].attr  # use old type of attributes
        )

    #sprint("After R3", k)

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after R3:", k)
            sanity_check(k)

    return k

    #print(k)
    #print()
    #
    # #if DEBUG: print(f"R3 nodes: {triangle_nodes}")
    #
    # #inst = {node: list(k.nodes[node]) for node in triangle_nodes}  # make a copy of the nodes
    # #adj_region = [k.nodes[ep] for ep in region]
    # new_outer_endpoints = dict()  # endpoints to replace outside the area
    # new_inner_endpoints = dict()  # endpoints to replace inside the area
    # for index in range(3):
    #     node, pos = face[index]
    #     prev_node, prev_pos = face[(index - 1) % 3]
    #     next_node, next_pos = face[(index + 1) % 3]
    #
    #     new_outer_endpoints[(node, pos)] = tuple(k.nodes[prev_node][(prev_pos + 1) % 4])  #(prev_node, (prev_pos + 1) % 4)
    #     new_outer_endpoints[(node, (pos - 1) % 4)] = tuple(k.nodes[next_node][(next_pos + 2) % 4]) #(next_node, (next_pos + 2) % 4)
    #     new_inner_endpoints[(node, (pos + 1) % 4)] = (next_node, (next_pos + 2) % 4)
    #     new_inner_endpoints[(node, (pos + 2) % 4)] = (prev_node, (prev_pos + 1) % 4)
    #
    # for ep, adj_ep in chain(zip(region, adj_region), zip(adj_region, region)):
    #     # reroute the internal triangle endpoint
    #     k.nodes[adj_ep.node][(adj_ep.position + 2) & 3] = Endpoint(ep.node, (ep.position + 2) & 3)  # no loop
    #
    #     if DEBUG: print("EP", ep, "ADJ", adj_ep, "EP+2", inst[ep.node][(ep.position + 2) & 3])
    #
    #     # reroute the external triangle endpoint
    #     if inst[ep.node][(ep.position + 2) & 3].node in triangle_nodes:
    #         adj_j_ep = inst[ep.node][(ep.position + 2) & 3]
    #
    #         if DEBUG: print("  J", adj_j_ep)
    #
    #         k.nodes[adj_ep] = inst[adj_j_ep.node][(adj_j_ep.position + 2) & 3]
    #     else:
    #         k.nodes[adj_ep] = inst[ep.node][(ep.position + 2) & 3]


if __name__ == "__main__":

    from knotpy.classes.planardiagram import PlanarDiagram

    k = PlanarDiagram()
    k.add_crossings_from("ABC")
    k.set_arcs_from([(("A", 3), ("B", 1)),
                     (("A", 2), ("C", 0)),
                     (("B", 2), ("C", 3)),
                     (("A", 0), ("B", 0)),
                     (("B", 3), ("A", 1)),
                     (("C", 1), ("C", 2))
                     ])

    print(k)
    reidemeister_3(k, [k["B"][1], k["A"][2], k["C"][3]])

    print(k)

    exit()
    k = PlanarDiagram()
    k.add_crossings_from("ABCDEFGHI")
    k.set_arcs_from([(("A",0), ("B",2)),
                    (("A",1), ("C",1)),
                    (("B",1), ("C",2)),
                    (("A",2), ("D",0)),
                     (("A", 3), ("B", 3)),
                     #(("B", 3), ("F", 0)),
                    (("B", 0), ("G", 0)),
                    (("C", 3), ("H", 0)),
                    (("C", 0), ("I", 0))
                     ])

    print(k)
    reidemeister_3(k, [k["C"][1], k["A"][0], k["B"][1]])

    print(k)
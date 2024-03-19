from itertools import chain
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.node_algorithms import name_for_new_node
from knotpy.algorithms.components import add_unknot_in_place


__all__ = ['remove_kink']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

_debug_reidemeister = False


def remove_kink(k: PlanarDiagram, region: list):
    """Perform a Reidemeister type I move (unkink) on the singleton region and adjust the framing.
    :param k: knotted planar diagram object
    :param region: the singleton list containing the arc for removal
    :return: knot k with one fewer crossing
    """

    if _debug_reidemeister:
        print("Remove kink from", k, "on endpoint", region[0])


    if len(region) != 1:
        raise ValueError(f"Cannot perform an unkink on a region of length {len(region)}.")


    # sanity checks
    # if arc[0].node != arc[1].node:
    #     raise ValueError("Cannot remove a kink on an arc that does not form a loop.")
    #
    # node = arc[0].node
    # crossing_inst = k.nodes[node]
    # if not crossing_inst.is_crossing:
    #     raise ValueError(f"Cannot remove a kink on a node of type {type(crossing_inst).__name__}.")

    node, position = region[0]

    crossing_inst = k.nodes[node]  # save the crossing instance
    k.remove_node(node, remove_incident_endpoints=False)

    # we attach the endpoints at positions (endpoint.position + 1) and (endpoint.position + 2)

    # double kink?
    if crossing_inst[(position + 1) & 3].node == crossing_inst[(position + 2) & 3].node == node:
        add_unknot_in_place(k)
    # single kink?
    else:
        k.set_arc((crossing_inst[(position + 1) & 3], crossing_inst[(position + 2) & 3]))

    k.framing = k.framing + (1 if position & 1 else -1)

    if _debug_reidemeister:
        print("      After R1", k)

def add_kink(k, endpoint, sign):
    """Add a new kink at endpoint of sign inside the region endpoint belongs to."""
    adj_endpoint = k.arcs[endpoint][0]
    node = name_for_new_node(k)
    k.add_crossing(node)
    if sign > 0:
        k.add_arcs(((node, 0), (node, 1)))
        k.add_arcs(((node, 2), adj_endpoint))
        k.add_arcs(((node, 3), endpoint))
    elif sign < 0:
        k.add_arcs(((node, 1), (node, 2)))
        k.add_arcs(((node, 3), adj_endpoint))
        k.add_arcs(((node, 0), endpoint))
    else:
        raise ValueError(f"Unsupported crossing sign {sign}.")



def remove_poke(k: PlanarDiagram, region: list) -> None:
    """Perform a unpoke (Reidemeister type II move) on the endpoints that define a bigon poke region.
    :param k: knotted planar diagram object
    :param region: a list of the two endpoints of the poke region
    :return: knot k with two fewer crossings
    """
    if _debug_reidemeister:
        print("Remove poke from", k, "on region", region)

    if len(region) != 2:
        raise ValueError(f"Cannot perform an unpoke on a region of length {len(region)}.")

    r = list(faces(k))

    # no sanity checks

    ep_a, ep_b = region
    node_a, node_b = ep_a.node, ep_b.node
    a_inst_, b_inst_ = k.nodes[node_a], k.nodes[node_b]  # crossing instances

    k.remove_node(node_a, remove_incident_endpoints=False)
    k.remove_node(node_b, remove_incident_endpoints=False)

    if _debug_reidemeister:
        print("  Crossings", a_inst_, b_inst_, "ep", ep_a, ep_b)

    # is there a kink at crossings a or b?
    kink_a = a_inst_[(ep_a.position + 1) & 3].node == a_inst_[(ep_a.position + 2) & 3].node == node_a
    kink_b = b_inst_[(ep_b.position + 1) & 3].node == b_inst_[(ep_a.position + 2) & 3].node == node_b

    # double kink?
    if kink_a and kink_b:
        add_unknot_in_place(k)
    # one kink?
    elif kink_b:
        k.set_arc((a_inst_[(ep_a.position + 1) & 3], a_inst_[(ep_a.position + 2) & 3]))  # attach the non-kink endpoints
    elif kink_a:
        k.set_arc((b_inst_[(ep_b.position + 1) & 3], b_inst_[(ep_b.position + 2) & 3]))  # attach the non-kink endpoints
    # no kink?
    else:

        arc_a = (a_inst_[(ep_a.position + 2) & 3], b_inst_[(ep_b.position + 1) & 3])
        arc_b = (b_inst_[(ep_b.position + 2) & 3], a_inst_[(ep_a.position + 1) & 3])

        # is the 1st new arc connected (forms an unknot after the unpoke)? The second "and" term is unnecessary.
        if arc_a[0].node == node_b and arc_a[1].node == node_a:
            add_unknot_in_place(k)
        else:
            k.set_arc(arc_a)

        if arc_b[0].node == node_a and arc_b[1].node == node_b:
            add_unknot_in_place(k)
        else:
            k.set_arc(arc_b)


    if _debug_reidemeister:
        print("  After RII", k)


def reidemeister_3(k, region):
    """Perform a Reidemeister III move on a non-alternating triangular region."""

    if len(region) != 3:
        raise ValueError(f"Cannot perform an Reidemeister III move on a region of length {len(region)}.")

    triangle_nodes = {ep.node for ep in region}
    print(triangle_nodes)
    inst = {node: list(k.nodes[node]) for node in triangle_nodes}  # make a copy of the nodes
    adj_region = [k.nodes[ep] for ep in region]
    for ep, adj_ep in chain(zip(region, adj_region), zip(adj_region, region)):
        # reroute the internal triangle endpoint
        k.nodes[adj_ep.node][(adj_ep.position + 2) & 3] = Endpoint(ep.node, (ep.position + 2) & 3)  # no loop

        print("EP", ep, "ADJ", adj_ep, "EP+2", inst[ep.node][(ep.position + 2) & 3])

        # reroute the external triangle endpoint
        if inst[ep.node][(ep.position + 2) & 3].node in triangle_nodes:
            adj_j_ep = inst[ep.node][(ep.position + 2) & 3]

            print("  J", adj_j_ep)

            k.nodes[adj_ep] = inst[adj_j_ep.node][(adj_j_ep.position + 2) & 3]
        else:
            k.nodes[adj_ep] = inst[ep.node][(ep.position + 2) & 3]


if __name__ == "__main__":

    from knotpy.classes.knot import Knot

    k = Knot()
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
    k = Knot()
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
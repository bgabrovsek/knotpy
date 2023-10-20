from copy import deepcopy
from itertools import product
from knotpy.convert import to_knotted
from knotpy.algorithms.node_algorithms import name_for_next_node_generator
from knotpy.algorithms.components import disjoint_sum, add_unknot_in_place
from knotpy.classes.spatialgraph import SpatialGraph

__all__ = ['insert_tangle', 'insert_tangles_from']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def insert_tangle(k, node, tangle, compass=None, create_using=None):
    """Insert the tangle into the knotted stricture at the 4-valent node.
    :param k: knotted structure to insert the tangle
    :param node: the node which we will replace with a tangle
    :param tangle: the tangle we will insert
    :param compass: a dictionary or list specifying which endpoints are connected to which endpoints. For example, a
    dictionary {0: "NE", 1: "NW", 2: "SW", 3: "SE"} will connect the NE endpoint with the node node of k at position 0,
    etc.
    :return:
    """

    raise NotImplementedError()

    #
    # new_knot, (k_relabel_dict, t_relabel_dict) = disjoint_sum(k, tangle,
    #                                                           return_relabel_dicts=True,
    #                                                           create_using=create_using)
    # compass = compass or {0: "NE", 1: "NW", 2: "SW", 3: "SE"}
    # for position, ord_dir in compass.items():
    #
    #     # redirect the arcs
    #     new_node = k_relabel_dict[node]
    #     new_tangle_node = t_relabel_dict[ord_dir]
    #
    #     new_knot.set_arc(
    #         (new_knot.nodes[new_node][position],
    #          new_knot.nodes[new_tangle_node][0])
    #     )
    #
    # new_knot.remove_node(k_relabel_dict[node], remove_incident_endpoints=False)
    #
    # for old_node in  ("NE", "NW", "SW", "SE"):
    #     new_knot.remove_node(t_relabel_dict[old_node], remove_incident_endpoints=False)
    #
    #
    # return new_knot
    #

def insert_tangles_from(k, tangles_dict: dict, create_using=None):
    """
    Insert tangles from tangles_dict. Uses default compass {0: "NE", 1: "NW", 2: "SW", 3: "SE"}.
    :param k: knotted graph-like structure
    :param tangles_dict: a dictionary mapping a node to a tangle {node 1: tangle 1, ...}
    :return: list of knotted structures
    """

    _debug = False

    compass = {0: "NE", 1: "NW", 2: "SW", 3: "SE"}  # TODO: enable custom compass

    new_knot, relabel_dicts = disjoint_sum(k, *tangles_dict.values(),
                                           return_relabel_dicts=True,
                                           create_using=SpatialGraph)

    if _debug:
        for ky, v in tangles_dict.items():
            print(ky, '->', v)
        print("N", new_knot)
        print('R', relabel_dicts)

    relabel_k = relabel_dicts[0]  # new labels for knot nodes
    relabel_t = relabel_dicts[1:]  # list of new labels for tangle nodes

    if len(tangles_dict) != len(relabel_t):
        raise ValueError()

    for node, tangle, relabel in zip(tangles_dict.keys(), tangles_dict.values(), relabel_t):
        if _debug: print("NODE", node,"tan",tangle,"rel", relabel_t)

        new_node = relabel_k[node]  # old knot node

        """Loop through endpoints (ordinal directions) of the tangle. We have the 4-valent node (new_node) and 
        the tangle endpoint node (new_tangle_node) and we connect the endpoints adjacent to these.
        In the special case when the tangle nodes are connected (horizontal/vertical tangle), the reconnection fixed 
        itself when a double reconnection is applied form both ends (...).
        In the case when a tangle insertion creates an unknot (e.g. horizontal tangle inserted at a loop), an existing
        arc is added, we capture this and add the unknot. 
        """
        for position, ord_dir in compass.items():
            if _debug: print(position, ord_dir)
            # redirect the arcs
            new_tangle_node = relabel[ord_dir]  # ordinal tangle node

            if _debug: print("  arc", (new_knot.nodes[new_node][position], new_knot.nodes[new_tangle_node][0]))

            # connect adjacent tangle/graph endpoints
            new_arc = (new_knot.nodes[new_node][position], new_knot.nodes[new_tangle_node][0])

            if new_knot.nodes[new_arc[0]] == new_arc[1] and new_knot.nodes[new_arc[1]] == new_arc[0]:  # self-loop?
                add_unknot_in_place(new_knot)
            else:
                new_knot.set_arc(new_arc)

        new_knot.remove_node(new_node, remove_incident_endpoints=False)  # remove the node that wes replaced by a tangle

        for old_node in ("NE", "NW", "SW", "SE"):  # remove tangle endpoints, since they are now connected
            new_knot.remove_node(relabel[old_node], remove_incident_endpoints=False)

    return new_knot


if __name__ == "__main__":
    import knotpy as kp
    # g = kp.from_plantri_notation("cbbc,aca,aab")
    # print(g)
    # t = kp.integer_tangle(1)
    # print(t)
    # k = kp.insert_tangles_from(g, {"a": t}, create_using=kp.SpatialGraph)
    # print("Result\n",k)

    tangles = [kp.horizontal_tangle(), kp.vertical_tangle(), kp.integer_tangle(1)]
    strs = ["Horizontal", "Vertical", "Integer"]
    ts = list(zip(tangles, strs))


    for (t0, s0), (t1, s1) in product(ts, ts):
        print("\n###", s0, s1,  "###")

        g = kp.from_plantri_notation("bccb,daad,ada,bbc")
        print(g)
        print(t0)
        print(t1)
        k = kp.insert_tangles_from(g, {"a": t0, "b":t1}, create_using=kp.SpatialGraph)
        print("Result")
        print(k)

    exit()


    # from knotpy.generate.simple_tangles import integer_tangle
    # from knotpy.notation.plantri import from_plantri_notation
    # t = integer_tangle(2)
    # print(t)
    #
    # g = from_plantri_notation("bcde,aedc,abd,acbe,adb")
    # print(g)
    #
    # k = insert_tangle(g, "b", t, create_using=SpatialGraph)
    # print(k)
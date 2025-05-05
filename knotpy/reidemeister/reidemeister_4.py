from knotpy import from_knotpy_notation
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.manipulation.subdivide import subdivide_endpoint_by_crossing, subdivide_endpoint
from knotpy.manipulation.rewire import pull_and_plug_endpoint
from knotpy.utils.dict_utils import common_dict

def _expand_over_under_adjacent_positions(k:PlanarDiagram, v:Vertex, start_position:int):
    """
    For a vertex and position, it checks next positions, CCW and CW, for the vertex, so that all of them form a
    non-alternating triangle, which means there is an over- or under-strand between them.
    Basically, it returns the positions of a vertex v that are incident to crossings such that a R4 slide can be
    performed, meaning, we can slide the strand from return positions to new on the "other side" of the vertex.
    it finds only such positions, where "start position" is included.

    """

    v_inst = k.nodes[v]  # instance of the vertex

    if not isinstance(v_inst, Vertex):
        raise TypeError("Variable v must be of a vertex")

    deg = k.degree(v)
    good_positions = [start_position]  # here we store "good" positions of v, where R4 move can be made

    # There should be a crossing adjacent to v at the position.
    start_ep = v_inst[start_position]
    if not isinstance(k.nodes[start_ep.node], Crossing):
        return []

    good_neighbour_crossings = [start_ep.node]  # get the crossing adjacent to v
    good_parity = start_ep.position % 2  # all other positions should be of the same parity (all over or all under)

    # expand the positions CCW
    for _ in range(deg - 1):
        position = good_positions[-1]
        next_position = (position + 1) % deg  # move one position CCW
        adj_ep = k.nodes[v][position]
        next_adj_ep = k.nodes[v][next_position]
        adj_crossing_inst = k.nodes[adj_ep.node]
        next_adj_crossing_inst = k.nodes[next_adj_ep.node]

        # check if next position meets all requirements so it forms a strand continuing from position to the next
        if not isinstance(next_adj_crossing_inst, Crossing):  # is not a crossing
            break
        if next_adj_ep.node in good_neighbour_crossings:  # the crossing is not already used
            break
        if next_adj_ep.position % 2 != good_parity:  # over/under is wrong
            break

        turn_ep = adj_crossing_inst[(adj_ep.position - 1) % 4]
        next_turn_ep = next_adj_crossing_inst[(next_adj_ep.position + 1) % 4]

        if k.twin(turn_ep) != next_turn_ep or k.twin(next_turn_ep) != turn_ep:  # strand continues from position to the nexy (cna only check one)
            break

        # all conditions are met, so we can continue extending
        good_positions.append(next_position)
        good_neighbour_crossings.append(next_adj_ep.node)

        #print("ccw", next_position, next_adj_ep.node, adj_ep.node, good_neighbour_crossings)

    # expand the positions CW
    for _ in range(deg - 1):
        position = good_positions[0]
        next_position = (position - 1) % deg  # move one position CW
        adj_ep = k.nodes[v][position]
        next_adj_ep = k.nodes[v][next_position]
        adj_crossing_inst = k.nodes[adj_ep.node]
        next_adj_crossing_inst = k.nodes[next_adj_ep.node]

        # check if next position meets all requirements so it forms a strand continuing from position to the next
        if not isinstance(next_adj_crossing_inst, Crossing):  # is not a crossing
            break
        if next_adj_ep.node in good_neighbour_crossings:  # the crossing is not already used
            break
        if next_adj_ep.position % 2 != good_parity:  # over/under is wrong
            break

        turn_ep = adj_crossing_inst[(adj_ep.position + 1) % 4]
        next_turn_ep = next_adj_crossing_inst[(next_adj_ep.position - 1) % 4]

        if k.twin(turn_ep) != next_turn_ep or k.twin(next_turn_ep) != turn_ep:  # strand continues from position to the nexy (cna only check one)
            break

        # all conditions are met, so we can continue extending
        good_positions.insert(0, next_position)
        good_neighbour_crossings.insert(0, next_adj_ep.node)

        #print(" cw", next_position, next_adj_ep.node, good_neighbour_crossings)


    return good_positions


def find_reidemeister_4_slides(k:PlanarDiagram):

    for v in k.vertices:
        unused_positions = set(range(k.degree(v)))

        while unused_positions:
            position = unused_positions.pop()

            good_positions = _expand_over_under_adjacent_positions(k, v, position)
            if good_positions:
                yield v, good_positions
            unused_positions.difference_update(set(good_positions))



def reidemeister_4_slide(k:PlanarDiagram, node_positions_pair, inplace=False):

    if not inplace:
        k = k.copy()

    v, positions = node_positions_pair
    deg = k.degree(v)
    parity = k.nodes[v][positions[0]].position % 2

    # get common attributes of old crossings
    crossings = [k.nodes[v][pos].node for pos in positions]
    common_node_attr = common_dict( *(k.nodes[c].attr for c in crossings )  )

    # Get endpoint type (in the case we have an orientation)
    ep_first = k.nodes[v][positions[0]]
    ep_last = k.nodes[v][positions[-1]]

    # first & last from ccw order
    ep_side_first = k.endpoint_from_pair((ep_first.node, (ep_first.position + 1) % 4))
    ep_side_last = k.endpoint_from_pair((ep_last.node, (ep_last.position - 1) % 4))
    common_ep_side_attr = common_dict(ep_first.attr, ep_last.attr)
    ep_side_first_type = type(ep_side_first)
    ep_side_last_type = type(ep_side_last)

    # subdivide side endpoints
    temp_node_first = subdivide_endpoint(k, ep_side_first, _temp=True)
    temp_node_last = subdivide_endpoint(k, ep_side_last, _temp=True)


    # Get positions on the other side of the vertex in CCW order.
    new_positions = [(_ + positions[-1] + 1) % deg for _ in range(deg - len(positions))]

    # put crossings to the other side
    new_crossings = [subdivide_endpoint_by_crossing(k, endpoint=(v, pos), crossing_position=parity) for pos in new_positions]
    for c in new_crossings:
        k.nodes[c].attr = common_node_attr

    # put arcs between crossings
    for index in range(len(new_positions) - 1):
        # position = new_positions[index]
        # next_position = new_positions[index + 1]
        crossing = new_crossings[index]
        next_crossing = new_crossings[index + 1]

        # set arc
        k.set_endpoint(endpoint_for_setting=(crossing, (parity - 1) % 4), adjacent_endpoint=(next_crossing, (parity + 1) % 4), create_using=ep_side_first_type, **common_ep_side_attr)
        k.set_endpoint(endpoint_for_setting=(next_crossing, (parity + 1) % 4), adjacent_endpoint=(crossing, (parity - 1) % 4), create_using=ep_side_last_type, **common_ep_side_attr)

    k.set_endpoint((new_crossings[0], (parity + 1) % 4), ep_side)
    # redirect endpoints # TODO: orientation
    #pull_and_plug_endpoint(k, source_endpoint=ep_side_last, destination_endpoint=(new_crossings[0], (parity + 1) % 4))
    #pull_and_plug_endpoint(k, source_endpoint=ep_side_first, destination_endpoint=(new_crossings[-1], (parity - 1) % 4))
    k.set_endpoint(endpoint_for_setting=())

    return k

if __name__ == "__main__":
    s = "a=V(c0 b0 d2) b=V(a1 c3 d3) c=X(a0 d1 d0 b1) d=X(c2 c1 a2 b2)"
    t = "a=V(c3 b0 e3 d3) b=X(a1 c2 c1 e0) c=X(d2 b2 b1 a0) d=X(e2 e1 c0 a3) e=X(b3 d1 d0 a2)"
    k = from_knotpy_notation(s)
    print(k, sanity_check(k))
    for v, good_positions in find_reidemeister_4_slides(k):
        print(v, good_positions)
        k_ = reidemeister_4_slide(k, (v, good_positions), inplace=False)
        print(k_, sanity_check(k_))


    k = from_knotpy_notation(t)
    print(k, sanity_check(k))
    for v, good_positions in find_reidemeister_4_slides(k):
        print(v, good_positions)

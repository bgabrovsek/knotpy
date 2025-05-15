from random import choice

from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.manipulation.subdivide import subdivide_endpoint_by_crossing, subdivide_endpoint
from knotpy.manipulation.rewire import pull_and_plug_endpoint
from knotpy.utils.dict_utils import common_dict
from knotpy.manipulation.remove import remove_bivalent_vertex
from knotpy.algorithms.disjoint_sum import add_unknot
from knotpy._settings import settings

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


def find_reidemeister_4_slide(k:PlanarDiagram, change: str = "any"):
    """
        Find and yield all possible Reidemeister 4 "slide" moves on a given PlanarDiagram.
        A slide move is given by a vertex and the set of incident positions of the vertex's arcs.

        Parameters
        ----------
        k : PlanarDiagram
            The input planar diagram on which potential Reidemeister 4 slide moves are to be found.
        change : str, optional
            Specifies the type of crossing change to consider. Valid values include:
            - "any": No specific condition for the crossing change.
            - "decrease": Considers only moves that result in a decrease in crossings.
            - "constant": Considers only moves that keep crossings constant.
            - "increase": Considers only moves that result in an increase in crossings.
            - "nonincreasing": Considers moves allowing non-increasing crossings.
            - "nondecreasing": Considers moves allowing non-decreasing crossings.
            Defaults to "any".

        Yields
        ------
        tuple
            Each yielded value is a tuple containing:
            - A vertex from the PlanarDiagram where the move is found.
            - A set of positions representing valid Reidemeister 4 slide adjustments.

    """

    def _satisfied(loc):
        if change == "any": return True
        ci = _crossing_increase_reidemeister_4_slide(k, loc)
        if change == "decrease" or change == "reduce": return ci < 0
        if change == "constant": return ci == 0
        if change == "increase": return ci > 0
        if change == "nonincreasing": return ci <= 0
        if change == "nondecreasing": return ci >= 0

    change = change.lower().strip()
    if change.endswith("ing"):
        change = change[:-3] + "e"
    if change not in ["any", "decrease", "reduce", "constant", "increase", "nonincrease", "nondecrease"]:
        raise ValueError(f"change parameter is '{change}', but it must be one of the following: "
                         f"any, decrease, constant, increase, nonincrease, or nondecrease")


    for v in k.vertices:
        unused_positions = set(range(k.degree(v)))

        while unused_positions:
            position = unused_positions.pop()

            good_positions = _expand_over_under_adjacent_positions(k, v, position)

            if good_positions and _satisfied((v, good_positions)):
                yield v, good_positions
            unused_positions.difference_update(set(good_positions))

def _crossing_increase_reidemeister_4_slide(k:PlanarDiagram, node_positions_pair: tuple):
    """ Number of additional crossings after performing a R4 slide (can be negative if the number decreases or zero
    if the number stays the same)."""
    v, positions = node_positions_pair
    return k.degree(v) - 2 * len(positions)

def choose_reidemeister_4_slide(k: PlanarDiagram, change: str = "any", random=False):
    """
    Selects a Reidemeister 4 slide move on a planar diagram.

    This function identifies and selects a Reidemeister 4 slide move based on the
    specified filtering criteria, allowing optional randomization. The `change`
    parameter specifies the form of filtering to apply with respect to the number
    of crossings in the diagram. Users can choose moves that increase, decrease,
    remain constant, or have no specific constraint on the number of crossings. If
    randomization is enabled, the function selects any move that satisfies the
    criteria at random. If no valid moves are found, or the criteria cannot be met,
    the function returns `None`.

    Parameters:
        k (PlanarDiagram): The planar diagram on which a Reidemeister 4 slide move
            will be performed.
        change (str): A string specifying the filtering criteria for the move.
            Possible values are:
              - "any": Return any valid move.
              - "increase": Only moves that increase the number of crossings.
              - "decrease": Only moves that decrease the number of crossings.
              - "constant": Only moves that leave the number unchanged.
              - "nonincreasing": Moves that do not increase (constant or decrease).
              - "nondecreasing": Moves that do not decrease (constant or increase).
            Default is "any".
        random (bool): A boolean flag. If True, a valid move satisfying the criteria
            is randomly selected. If False, the first valid move is selected.
            Default is False.

    Returns:
        Optional[Any]: The selected location representing a Reidemeister 4 slide
            move if a valid move is found; otherwise, returns `None`.

    Raises:
        ValueError: If the `change` parameter value is not one of the accepted
            strings: "any", "decrease", "constant", "increase", "nonincreasing",
            or "nondecreasing".
    """

    if not change or change is None:
        change = "any"

    if random:
        locations = list(find_reidemeister_4_slide(k, change))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_4_slide(k, change), None)


def _crossing_to_arc(k: PlanarDiagram, crossing, parity):
    """
    Remove a crossing and join two of its arcs into one (remove it and connect the adjacent endpoints).
    This ignores the non-parity endpoints and connect the parity endpoints.
    """

    if not isinstance(k.nodes[crossing], Crossing):
        raise TypeError("Variable crossing must be of a crossing")
    parity %= 2

    # connect two arcs of a knot
    ep_a = k.nodes[crossing][parity]
    ep_b = k.nodes[crossing][parity + 2]
    k.set_endpoint(ep_a, ep_b)
    k.set_endpoint(ep_b, ep_a)

    # remove the crossing
    k.remove_node(crossing, remove_incident_endpoints=False)


def reidemeister_4_slide(k:PlanarDiagram, vertex_positions_pair, inplace=False):

    if not inplace:
        k = k.copy()

    # assert sanity_check(k)

    v, positions = vertex_positions_pair
    deg = k.degree(v)
    parity = k.nodes[v][positions[0]].position % 2


    # get common attributes of old crossings
    crossings = [k.nodes[v][pos].node for pos in positions]
    common_node_attr = common_dict( *(k.nodes[c].attr for c in crossings )  )

    # # is there a full circle (disjoint unknot) around the vertex?
    # if len(positions) == deg:
    #     # remove the unknot
    #     for c in crossings:
    #         _crossing_to_arc(k, c, parity)
    #     add_unknot(k, 1, inplace=True)  # TODO: attributes
    #     # backtrack Reidemeister moves
    #     if settings.trace_moves:
    #         k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R4"
    #
    #     return k

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

    # get destination side arcs
    ep_side_first_twin = k.twin(ep_side_first)
    ep_side_last_twin = k.twin(ep_side_last)

    # are there new crossings (there was not a full slide-off)
    if new_crossings:
        k.set_endpoint((new_crossings[0], (parity + 1) % 4), ep_side_last_twin) # TODO: attributes
        k.set_endpoint(ep_side_last_twin, (new_crossings[0], (parity + 1) % 4)) # TODO: attributes
        k.set_endpoint((new_crossings[-1], (parity - 1) % 4), ep_side_first_twin)  # TODO: attributes
        k.set_endpoint(ep_side_first_twin, (new_crossings[-1], (parity - 1) % 4))  # TODO: attributes
    else:
        k.set_endpoint(ep_side_last_twin, ep_side_first_twin)  # TODO: attributes
        k.set_endpoint(ep_side_first_twin, ep_side_last_twin)


    remove_bivalent_vertex(k, temp_node_first, keep_if_unknot=True)
    remove_bivalent_vertex(k, temp_node_last, keep_if_unknot=True)

    for c in crossings:
        _crossing_to_arc(k, c, parity)

    # remove bivalent vertices

    #k.set_endpoint((new_crossings[0], (parity + 1) % 4), ep_side)
    # redirect endpoints # TODO: orientation
    #pull_and_plug_endpoint(k, source_endpoint=ep_side_last, destination_endpoint=(new_crossings[0], (parity + 1) % 4))
    #pull_and_plug_endpoint(k, source_endpoint=ep_side_first, destination_endpoint=(new_crossings[-1], (parity - 1) % 4))

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R4"

    # assert sanity_check(k), "oh no"
    # print("R4", k)

    return k

if __name__ == "__main__":

    """
    MRRM 0 Diagram named +t3_1 a → V(b0 c0 d3), b → V(a0 e0 f3), c → X(a1 f0 e3 d0), d → X(c3 e2 e1 a2), e → X(b1 d2 d1 c2), f → X(c1 f2 f1 b2) (_sequence=R1)    A**11 + A**10 + A**9 - A**8 - 2*A**7 - 4*A**6 - 3*A**5 - 2*A**4 + A**2 + A + 1 ['R1kink', 'R2poke', 'R4increase', 'R5twist']
R4 ('a', [1])
MRRM 1 Diagram named +t3_1 a → V(j0 e3 i0), b → V(j2 e0 f3), d → X(i1 e2 e1 i2), e → X(b1 d2 d1 a1), f → X(j3 f2 f1 b2), i → X(a2 d0 d3 j1), j → X(a0 i3 b0 f0) (_sequence=R1R4)    -A**10 - 2*A**9 - 4*A**8 - 3*A**7 - 3*A**6 + A**4 + 2*A**3 + 2*A**2 + A + 1
    
    """


    from knotpy import from_knotpy_notation, yamada_polynomial
    t1 = "a → V(b0 c0 d3), b → V(a0 e0 f3), c → X(a1 f0 e3 d0), d → X(c3 e2 e1 a2), e → X(b1 d2 d1 c2), f → X(c1 f2 f1 b2)"
    t1 = from_knotpy_notation(t1)
    print(t1, sanity_check(t1), yamada_polynomial(t1))
    t2 = reidemeister_4_slide(t1, ('a', [1]), inplace=False)
    print(t2, sanity_check(t2), yamada_polynomial(t2))
    print("       a → V(j0 e3 i0), b → V(j2 e0 f3), d → X(i1 e2 e1 i2), e → X(b1 d2 d1 a1), f → X(j3 f2 f1 b2), i → X(a2 d0 d3 j1), j → X(a0 i3 b0 f0)")
    exit()
    #R4 ('b', [1])"
    """
    
    Diagram a → V(i0 e1 h0), b → V(i2 d2 e3), d → X(h1 e0 b1 h2), e → X(d1 a1 i3 b2), h → X(a2 d0 d3 i1), i → X(a0 h3 b0 e2) (_sequence=R4) True -A**12 - A**11 - A**10 - A**9 - A**8 - A**6 - A**4 + 1
            a → V(i0 e1 h0), b → V(i2 d2 e3), d → X(h1 e0 b1 h2), e → X(d1 a1 i3 b2), h → X(a2 d0 d3 i1), i → X(a0 h3 b0 e2)
    """


    # from R4 examples
    h1 = "a=V(b1 e0 f0) b=V(e1 a0 f3) c=V(e2 d0) d=V(c1 f2) e=X(a1 b0 c0 f1) f=X(a2 e3 d1 b2)"
    h1 = from_knotpy_notation(h1)
    print(h1, sanity_check(h1))

    r4 = ("a", [1, 2])

    k1 = reidemeister_4_slide(h1, r4)
    print(k1, sanity_check(k1))

    print(yamada_polynomial(h1))
    print(yamada_polynomial(k1))

    from knotpy.catalog.knot_tables import get_theta_curves

    for t in get_theta_curves():
        locations = list(find_reidemeister_4_slide(t))
        if locations:
            location = choice(locations)
            tt = reidemeister_4_slide(t, location)
            s = sanity_check(tt)
            if not s:
                print(t, "->", tt)

            y1 = yamada_polynomial(t)
            y2 = yamada_polynomial(tt)

            if y1 != y2:
                print(t, "->", tt, "(yamada)")

    # for v, good_pos in find_reidemeister_4_slides(h1):
    #     print(v, good_pos)

    # s = "a=V(c0 b0 d2) b=V(a1 c3 d3) c=X(a0 d1 d0 b1) d=X(c2 c1 a2 b2)"
    # t = "a=V(c3 b0 e3 d3) b=X(a1 c2 c1 e0) c=X(d2 b2 b1 a0) d=X(e2 e1 c0 a3) e=X(b3 d1 d0 a2)"
    # k = from_knotpy_notation(s)
    # print(k, sanity_check(k))
    # for v, good_positions in find_reidemeister_4_slides(k):
    #     print(v, good_positions)
    #     k_ = reidemeister_4_slide(k, (v, good_positions), inplace=False)
    #     print(k_, sanity_check(k_))
    #
    # k = from_knotpy_notation(t)
    # print(k, sanity_check(k))
    # for v, good_positions in find_reidemeister_4_slides(k):
    #     print(v, good_positions)

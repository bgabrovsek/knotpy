# knotpy/reidemeister/reidemeister_4.py
from __future__ import annotations

from typing import Iterable, Iterator, Optional, Sequence, Tuple, List, Hashable

from random import choice
import warnings

from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.classes.node import Crossing, Vertex
from knotpy.algorithms.subdivide import (
    subdivide_endpoint_by_crossing,
    subdivide_endpoint,
)
from knotpy.utils.dict_utils import common_dict
from knotpy.algorithms.remove import remove_bivalent_vertex
from knotpy._settings import settings


def _expand_over_under_adjacent_positions(
    k: Diagram, v: Hashable, start_position: int
) -> list[int]:
    """
    For a vertex and position, it checks next positions, CCW and CW, for the vertex, so that all of them form a
    non-alternating triangle, which means there is an over- or under-strand between them.
    Basically, it returns the positions of a vertex v that are incident to crossings such that a R4 slide can be
    performed, meaning, we can slide the strand from return positions to new on the "other side" of the vertex.
    it finds only such positions, where "start position" is included.

    Args:
        k (Diagram): The (oriented or unoriented) diagram.
        v (Hashable): The vertex node identifier.
        start_position (int): Index of the incident endpoint at which to start.

    Return:
        list[int]: A CCW-to-CW list of valid incident positions (including `start_position`)
        along which a single over/under strand continues.
    """
    v_inst = k.nodes[v]  # instance of the vertex

    if not isinstance(v_inst, Vertex):
        raise TypeError("Variable v must be of a vertex")

    deg = k.degree(v)
    good_positions: list[int] = [start_position]  # positions at v where an R4 can be made

    # There should be a crossing adjacent to v at the position.
    start_ep = v_inst[start_position]
    if not isinstance(k.nodes[start_ep.node], Crossing):
        return []

    good_neighbour_crossings = [start_ep.node]  # crossing adjacent to v
    good_parity = start_ep.position % 2  # all other positions should match this parity

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
        if next_adj_ep.node in good_neighbour_crossings:  # the crossing is already used
            break
        if next_adj_ep.position % 2 != good_parity:  # over/under is wrong
            break

        turn_ep = adj_crossing_inst[(adj_ep.position - 1) % 4]
        next_turn_ep = next_adj_crossing_inst[(next_adj_ep.position + 1) % 4]

        # strand continues from position to the next (can only check one)
        if k.twin(turn_ep) != next_turn_ep or k.twin(next_turn_ep) != turn_ep:
            break

        # all conditions are met, so we can continue extending
        good_positions.append(next_position)
        good_neighbour_crossings.append(next_adj_ep.node)

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
        if next_adj_ep.node in good_neighbour_crossings:  # the crossing is already used
            break
        if next_adj_ep.position % 2 != good_parity:  # over/under is wrong
            break

        turn_ep = adj_crossing_inst[(adj_ep.position + 1) % 4]
        next_turn_ep = next_adj_crossing_inst[(next_adj_ep.position - 1) % 4]

        # strand continues from position to the next (can only check one)
        if k.twin(turn_ep) != next_turn_ep or k.twin(next_turn_ep) != turn_ep:
            break

        # all conditions are met, so we can continue extending
        good_positions.insert(0, next_position)
        good_neighbour_crossings.insert(0, next_adj_ep.node)

    return good_positions


def find_reidemeister_4_slide(
    k: Diagram, change: str = "any"
) -> Iterator[tuple[Hashable, list[int]]]:
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
    if "R4" not in settings.allowed_moves:
        return

    def _satisfied(loc: tuple[Hashable, list[int]]) -> bool:
        if change == "any":
            return True
        ci = _crossing_increase_reidemeister_4_slide(k, loc)
        if change == "decrease" or change == "reduce":
            return ci < 0
        if change == "constant":
            return ci == 0
        if change == "preserve" or change == "preserve":
            return ci == 0
        if change == "nonincreasing":
            return ci <= 0
        if change == "nondecreasing":
            return ci >= 0
        return False

    # normalize and validate change flag
    change = (change or "any").lower().strip()
    if change.endswith("ing"):
        change = change[:-3] + "e"
    if change not in [
        "any",
        "decrease",
        "reduce",
        "preserve",
        "increase",
        "nonincrease",
        "nondecrease",
        "constant",
    ]:
        raise ValueError(
            f"change parameter is '{change}', but it must be one of the following: "
            f"any, decrease, preserve, increase, nonincrease, or nondecrease"
        )

    for v in k.vertices:
        unused_positions = set(range(k.degree(v)))

        while unused_positions:
            position = unused_positions.pop()

            good_positions = _expand_over_under_adjacent_positions(k, v, position)

            if good_positions and _satisfied((v, good_positions)):
                yield v, good_positions
            unused_positions.difference_update(set(good_positions))


def _crossing_increase_reidemeister_4_slide(
    k: Diagram, node_positions_pair: tuple[Hashable, list[int]]
) -> int:
    """ Number of additional crossings after performing a R4 slide (can be negative if the number decreases or zero
    if the number stays the same)."""
    v, positions = node_positions_pair
    return k.degree(v) - 2 * len(positions)


def choose_reidemeister_4_slide(
    k: Diagram, change: str = "any", random: bool = False
) -> Optional[tuple[Hashable, list[int]]]:
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

    Return:
        Optional[tuple[Hashable, list[int]]]: The selected (vertex, positions) location
        for an R4 slide if available; otherwise `None`.

    Raises:
        ValueError: If the `change` parameter value is not one of the accepted
            strings: "any", "decrease", "constant", "increase", "nonincreasing",
            or "nondecreasing".
    """
    if "R4" not in settings.allowed_moves:
        return None

    if not change or change is None:
        change = "any"

    if random:
        locations = list(find_reidemeister_4_slide(k, change))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_4_slide(k, change), None)


def _crossing_to_arc(k: Diagram, crossing: Hashable, parity: int) -> None:
    """
    Remove a crossing and join two of its arcs into one (remove it and connect the adjacent endpoints).
    This ignores the non-parity endpoints and connect the parity endpoints.

    Args:
        k (Diagram): Diagram to modify.
        crossing (Hashable): Crossing node identifier.
        parity (int): Use 0 (even) or 1 (odd) side to connect.
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


def reidemeister_4_slide(
    k: Diagram, vertex_positions_pair: tuple[Hashable, list[int]], inplace: bool = False
) -> Diagram:
    """
    Perform a Reidemeister IV "slide" move.

    The move slides a contiguous bundle of same-parity strands incident to a vertex
    across that vertex to the opposite side, introducing a chain of new crossings
    (or none, in the full slide-off case) and reconnecting the outside strands.

    Args:
        k (Diagram): The diagram to operate on.
        vertex_positions_pair (tuple[Hashable, list[int]]): A pair (v, positions),
            where `v` is a vertex node id and `positions` is a contiguous list of
            incident positions at `v` all meeting the over/under continuation test.
        inplace (bool): If True modify `k` in place, otherwise return a modified copy.

    Return:
        Diagram: The diagram with the slide applied.
    """
    # TODO: there is a _temp parameter on

    if "R4" not in settings.allowed_moves:
        warnings.warn(
            "An R4 move is being performed, although it is disabled in the global KnotPy settings."
        )

    if not inplace:
        k = k.copy()

    v, positions = vertex_positions_pair
    deg = k.degree(v)
    parity = k.nodes[v][positions[0]].position % 2

    # get common attributes of old crossings
    crossings = [k.nodes[v][pos].node for pos in positions]
    common_node_attr = common_dict(*(k.nodes[c].attr for c in crossings))

    # Get endpoint type (in the case we have an orientation)
    ep_first = k.nodes[v][positions[0]]
    ep_last = k.nodes[v][positions[-1]]

    # first & last from ccw order
    ep_side_first = k.endpoint_from_pair((ep_first.node, (ep_first.position + 1) % 4))
    ep_side_last = k.endpoint_from_pair((ep_last.node, (ep_last.position - 1) % 4))
    common_ep_side_attr = common_dict(ep_first.attr, ep_last.attr)
    ep_side_first_type = type(ep_side_first)
    ep_side_last_type = type(ep_side_last)

    # subdivide side endpoints (temporary bi-vertices)
    temp_node_first = subdivide_endpoint(k, ep_side_first, _temp=True)
    temp_node_last = subdivide_endpoint(k, ep_side_last, _temp=True)

    # Get positions on the other side of the vertex in CCW order.
    new_positions = [(_ + positions[-1] + 1) % deg for _ in range(deg - len(positions))]

    # put crossings to the other side
    new_crossings = [
        subdivide_endpoint_by_crossing(
            k, endpoint=(v, pos), crossing_position=parity
        )
        for pos in new_positions
    ]
    for c in new_crossings:
        k.nodes[c].attr = common_node_attr

    # put arcs between crossings
    for index in range(len(new_positions) - 1):
        crossing = new_crossings[index]
        next_crossing = new_crossings[index + 1]

        # set arc
        k.set_endpoint(
            endpoint_for_setting=(crossing, (parity - 1) % 4),
            adjacent_endpoint=(next_crossing, (parity + 1) % 4),
            create_using=ep_side_first_type,
            **common_ep_side_attr,
        )
        k.set_endpoint(
            endpoint_for_setting=(next_crossing, (parity + 1) % 4),
            adjacent_endpoint=(crossing, (parity - 1) % 4),
            create_using=ep_side_last_type,
            **common_ep_side_attr,
        )

    # get destination side arcs
    ep_side_first_twin = k.twin(ep_side_first)
    ep_side_last_twin = k.twin(ep_side_last)

    # are there new crossings (there was not a full slide-off)
    if new_crossings:
        k.set_endpoint((new_crossings[0], (parity + 1) % 4), ep_side_last_twin)  # TODO: attributes
        k.set_endpoint(ep_side_last_twin, (new_crossings[0], (parity + 1) % 4))  # TODO: attributes
        k.set_endpoint((new_crossings[-1], (parity - 1) % 4), ep_side_first_twin)  # TODO: attributes
        k.set_endpoint(ep_side_first_twin, (new_crossings[-1], (parity - 1) % 4))  # TODO: attributes
    else:
        k.set_endpoint(ep_side_last_twin, ep_side_first_twin)  # TODO: attributes
        k.set_endpoint(ep_side_first_twin, ep_side_last_twin)

    remove_bivalent_vertex(k, temp_node_first, keep_if_unknot=True)
    remove_bivalent_vertex(k, temp_node_last, keep_if_unknot=True)

    for c in crossings:
        _crossing_to_arc(k, c, parity)

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R4 "

    return k


if __name__ == "__main__":
    pass
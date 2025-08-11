# knotpy/reidemeister/reidemeister_2.py
"""
Reidemeister move II (R2): poke / unpoke.

Provides functions for detecting and performing R2 moves on diagrams.
Supports both unoriented and oriented diagrams via the Diagram alias.
"""
from itertools import combinations
from random import choice
import warnings

from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.naming import unique_new_node_name
from knotpy._settings import settings


def find_reidemeister_2_unpoke(k: Diagram):
    """
    Yield bigon faces (2-gons) where an R2 *unpoke* can be applied.

    A valid bigon here is two endpoints from two crossings with opposite parity
    (positions differ mod 2). These are the locations that reduce crossings by 2.

    Args:
        k (Diagram): Diagram to scan.

    Yields:
        tuple[Endpoint, Endpoint]: The 2-face (as endpoints) forming a removable bigon.

    Notes:
        Respects ``settings.allowed_moves``; yields nothing if "R2" is disabled.
    """
    if "R2" not in settings.allowed_moves:
        return

    # Loop through faces; keep 2-gons formed by two crossings with opposite parity.
    for face in k.faces:
        if (
            len(face) == 2
            and isinstance(k.nodes[face[0].node], Crossing)
            and isinstance(k.nodes[face[1].node], Crossing)
            and (face[0].position % 2) != (face[1].position % 2)
        ):
            yield face


def find_reidemeister_2_poke(k: Diagram):
    """
    Yield all possible R2 *poke* positions as ordered pairs (under, over)
    from endpoints in a common face.

    Args:
        k (Diagram): Diagram to scan.

    Yields:
        tuple[Endpoint, Endpoint]: ``(ep_under, ep_over)``. Both orders are yielded.
    """
    if "R2" not in settings.allowed_moves:
        return

    for face in k.faces:
        for ep_under, ep_over in combinations(face, 2):
            yield ep_under, ep_over
            yield ep_over, ep_under  # also the swapped order


def choose_reidemeister_2_unpoke(k: Diagram, random: bool = False):
    """
    Choose one R2 *unpoke* location (a 2-gon face).

    Args:
        k (Diagram): Diagram to analyze.
        random (bool): If True, pick randomly; otherwise return the first.

    Returns:
        tuple[Endpoint, Endpoint] | None: The chosen bigon as a pair of endpoints, or None.
    """
    if "R2" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_reidemeister_2_unpoke(k))
        return choice(locations) if locations else None
    return next(find_reidemeister_2_unpoke(k), None)


def choose_reidemeister_2_poke(k: Diagram, random: bool = False):
    """
    Choose one R2 *poke* pair (under, over) from a common face.

    Args:
        k (Diagram): Diagram to analyze.
        random (bool): If True, pick randomly; otherwise return the first.

    Returns:
        tuple[Endpoint, Endpoint] | None: The chosen (under, over) pair, or None.
    """
    if "R2" not in settings.allowed_moves:
        return None

    if random:
        choices = tuple(find_reidemeister_2_poke(k))
        if not choices:
            # Keeping your diagnostic; raising keeps behavior explicit.
            print("aa", k)
            raise ValueError("Can't find Reidemeister 2 poke")
        return choice(choices)
    return next(find_reidemeister_2_poke(k), None)  # select 1st item


def reidemeister_2_unpoke(k: Diagram, face, inplace: bool = False) -> Diagram:
    """
    Perform an R2 *unpoke* on a removable bigon (2-face).

    Reduces crossings by 2 by removing the two crossings bordering the bigon,
    then reconnecting external endpoints. Special cases (double kinks / unknots)
    are handled as in your original logic.

    Args:
        k (Diagram): Diagram to modify (or copy if ``inplace=False``).
        face (tuple[Endpoint, Endpoint]): The 2-gon endpoints.
        inplace (bool): Modify in place if True; otherwise return a modified copy.

    Returns:
        Diagram: The diagram after applying the move.

    Notes:
        If move tracing is enabled, appends ``"R2-"`` to ``k.attr["_sequence"]``.
    """
    # TODO: the code below is cumbersome; consider phantom temporary bi-vertices.
    if "R2" not in settings.allowed_moves:
        warnings.warn(
            "An R2 move is being performed, although it is disabled in the global KnotPy settings."
        )

    if not inplace:
        k = k.copy()

    ep_a, ep_b = face
    twin_a, twin_b = k.twin(ep_a), k.twin(ep_b)

    # If tuple pairs were passed, normalize to instances.
    if not isinstance(ep_a, Endpoint) or not isinstance(ep_b, Endpoint):
        ep_a, ep_b = k.twin(twin_a), k.twin(twin_b)

    # "Jump" is the opposite endpoint across the crossing (same strand).
    jump_a = k.endpoint_from_pair((ep_a.node, (ep_a.position + 2) % 4))
    jump_b = k.endpoint_from_pair((ep_b.node, (ep_b.position + 2) % 4))
    jump_twin_a = k.endpoint_from_pair((twin_a.node, (twin_a.position + 2) % 4))
    jump_twin_b = k.endpoint_from_pair((twin_b.node, (twin_b.position + 2) % 4))

    twin_jump_a = k.twin(jump_a)
    twin_jump_b = k.twin(jump_b)
    twin_jump_twin_a = k.twin(jump_twin_a)
    twin_jump_twin_b = k.twin(jump_twin_b)

    # Remove the two crossings that bound the bigon.
    k.remove_node(ep_a.node, remove_incident_endpoints=False)
    k.remove_node(ep_b.node, remove_incident_endpoints=False)

    def _set_arc(a: Endpoint, b: Endpoint):
        """Wire endpoints (a <-> b) with copied types/attrs preserved."""
        k.set_endpoint(
            endpoint_for_setting=a,
            adjacent_endpoint=(b.node, b.position),
            create_using=type(b),
            **b.attr,
        )
        k.set_endpoint(
            endpoint_for_setting=b,
            adjacent_endpoint=(a.node, a.position),
            create_using=type(a),
            **a.attr,
        )

    # Match original case analysis exactly.
    if twin_jump_twin_a is jump_b and twin_jump_twin_b is jump_a:  # double kink
        add_unknot(k)

    elif twin_jump_twin_a is jump_b:  # single kink at ep_a
        _set_arc(twin_jump_a, twin_jump_twin_b)

    elif twin_jump_twin_b is jump_a:  # single kink at ep_b
        _set_arc(twin_jump_b, twin_jump_twin_a)

    elif twin_jump_a is jump_twin_a and twin_jump_b is jump_twin_b:  # two overlapping unknots
        add_unknot(k, number_of_unknots=2)

    elif twin_jump_b is jump_a:  # “x”-type connected
        _set_arc(twin_jump_twin_a, twin_jump_twin_b)

    elif twin_jump_twin_b is jump_twin_a:  # “x”-type connected
        _set_arc(twin_jump_a, twin_jump_b)

    elif twin_jump_a is jump_twin_a:  # one unknot overlapping on strand a
        _set_arc(twin_jump_twin_b, twin_jump_b)
        add_unknot(k)

    elif twin_jump_b is jump_twin_b:  # one unknot overlapping on strand b
        _set_arc(twin_jump_twin_a, twin_jump_a)
        add_unknot(k)

    else:  # normal R2: all four external endpoints distinct
        _set_arc(twin_jump_twin_a, twin_jump_a)
        _set_arc(twin_jump_twin_b, twin_jump_b)

    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R2-"

    return k


def _reversed_endpoint_type(ep):
    """Return the opposite endpoint class (Endpoint <-> itself; Outgoing <-> Ingoing)."""
    if type(ep) is Endpoint or ep is Endpoint:
        return Endpoint
    if type(ep) is OutgoingEndpoint or ep is OutgoingEndpoint:
        return IngoingEndpoint
    if type(ep) is IngoingEndpoint or ep is IngoingEndpoint:
        return OutgoingEndpoint
    raise TypeError()


def reidemeister_2_poke(k: Diagram, under_over_endpoints, inplace: bool = False) -> Diagram:
    """
    Perform an R2 *poke* at a given ordered pair (under, over).

    Creates two new crossings and reconnects endpoints to realize the local
    “poke” configuration. Handles the same-arc edge case as in your original.

    Args:
        k (Diagram): Diagram to modify (or copy if ``inplace=False``).
        under_over_endpoints (tuple[Endpoint, Endpoint]): ``(under, over)``.
        inplace (bool): Modify in place if True; otherwise return a modified copy.

    Returns:
        Diagram: The diagram after applying the move.
    """
    endpoint_under, endpoint_over = under_over_endpoints

    if not inplace:
        k = k.copy()

    if not isinstance(endpoint_over, Endpoint) or not isinstance(endpoint_under, Endpoint):
        raise TypeError(
            f"Cannot add poke in endpoints of type {type(endpoint_over)} and {type(endpoint_under)}."
        )

    # Endpoint instances and their twins.
    twin_o_node, twin_o_pos = twin_o = k.twin(endpoint_over)
    twin_u_node, twin_u_pos = twin_u = k.twin(endpoint_under)
    ep_o_node, ep_o_pos = ep_o = k.twin(twin_o)  # instance of endpoint_over
    ep_u_node, ep_u_pos = ep_u = k.twin(twin_u)  # instance of endpoint_under

    # Endpoint classes (plain vs. oriented).
    type_o, rev_o = type(ep_o), _reversed_endpoint_type(ep_o)
    type_u, rev_u = type(ep_u), _reversed_endpoint_type(ep_u)

    # Create two new crossings.
    node_e = unique_new_node_name(k)
    k.add_crossing(node_e)
    node_f = unique_new_node_name(k)
    k.add_crossing(node_f)

    # Poke on a single arc?
    same_arc = (twin_u == ep_o and twin_o == ep_u)

    # Wiring for node "e"
    if not same_arc:
        k.set_endpoint(
            endpoint_for_setting=(node_e, 0),
            adjacent_endpoint=(twin_u_node, twin_u_pos),
            create_using=rev_u,
            **twin_u.attr,
        )
    k.set_endpoint(endpoint_for_setting=(node_e, 1), adjacent_endpoint=(node_f, 1), create_using=rev_o)
    k.set_endpoint(endpoint_for_setting=(node_e, 2), adjacent_endpoint=(node_f, 0), create_using=type_u)
    k.set_endpoint(
        endpoint_for_setting=(node_e, 3),
        adjacent_endpoint=(ep_o_node, ep_o_pos),
        create_using=type_o,
        **ep_o.attr,
    )

    # Wiring for node "f"
    k.set_endpoint(endpoint_for_setting=(node_f, 0), adjacent_endpoint=(node_e, 2), create_using=rev_u)
    k.set_endpoint(endpoint_for_setting=(node_f, 1), adjacent_endpoint=(node_e, 1), create_using=type_o)
    k.set_endpoint(
        endpoint_for_setting=(node_f, 2),
        adjacent_endpoint=(ep_u_node, ep_u_pos),
        create_using=type_u,
        **ep_u.attr,
    )
    if not same_arc:
        k.set_endpoint(
            endpoint_for_setting=(node_f, 3),
            adjacent_endpoint=(twin_o_node, twin_o_pos),
            create_using=rev_o,
            **twin_o.attr,
        )

    # Outside nodes
    k.set_endpoint(endpoint_for_setting=(ep_o_node, ep_o_pos), adjacent_endpoint=(node_e, 3), create_using=rev_o)
    k.set_endpoint(endpoint_for_setting=(ep_u_node, ep_u_pos), adjacent_endpoint=(node_f, 2), create_using=rev_u)
    if not same_arc:
        k.set_endpoint(
            endpoint_for_setting=(twin_o_node, twin_o_pos),
            adjacent_endpoint=(node_f, 3),
            create_using=type_o,
        )
        k.set_endpoint(
            endpoint_for_setting=(twin_u_node, twin_u_pos),
            adjacent_endpoint=(node_e, 0),
            create_using=type_u,
        )
    else:
        k.set_endpoint(endpoint_for_setting=(node_e, 0), adjacent_endpoint=(node_f, 3), create_using=rev_u)
        k.set_endpoint(endpoint_for_setting=(node_f, 3), adjacent_endpoint=(node_e, 0), create_using=rev_o)

    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R2+"

    return k
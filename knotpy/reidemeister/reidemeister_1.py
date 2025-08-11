# knotpy/reidemeister/reidemeister_1.py
"""
Reidemeister move I (R1): add or remove a kink.

This module finds and performs Reidemeister I moves on a diagram. It works for
both unoriented and oriented diagrams (your `Diagram` alias), respects the
global settings (e.g., allowed moves, tracing), and preserves endpoint
attributes where appropriate.

Key ideas:
- Removing a kink: identify a 1-gon (“kink”) via its defining endpoint and
  reconnect the adjacent endpoints; if a *double* kink is present at a node,
  that node vanishes and an unknot is added.
- Adding a kink: insert a new crossing next to a chosen endpoint with a given
  sign (+1 or −1), wiring endpoints to realize the desired local twist.
"""

from itertools import product
from random import choice
import warnings

from knotpy.classes.planardiagram import Diagram  # PlanarDiagram | OrientedPlanarDiagram
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.topology import kinks
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.utils.dict_utils import common_dict
from knotpy._settings import settings


def find_reidemeister_1_remove_kink(k: Diagram):
    """
    Yield locations where a Reidemeister I *removal* (unkink) can be performed.

    A location is represented by the endpoint that defines the 1-face of the kink.

    Args:
        k (Diagram): The diagram to scan.

    Yields:
        Endpoint: The endpoint that determines a removable kink.

    Notes:
        Respects ``settings.allowed_moves``; yields nothing if "R1" is disabled.
    """
    if "R1" not in settings.allowed_moves:
        return
    for ep in kinks(k):
        yield ep


def find_reidemeister_1_add_kink(k: Diagram):
    """
    Yield all possible places to *add* a kink (endpoint, sign).

    Args:
        k (Diagram): The diagram to scan.

    Yields:
        tuple[Endpoint, int]: Pairs ``(endpoint, sign)``, where ``sign`` is ``+1`` or ``-1``.
    """
    if "R1" not in settings.allowed_moves:
        return
    # Could return product directly; keep generator for clarity and symmetry with *_remove_*.
    for ep_sign in product(k.endpoints, (1, -1)):
        yield ep_sign


def choose_reidemeister_1_add_kink(k: Diagram, random: bool = False) -> tuple[Endpoint, int] | None:
    """
    Choose one R1 *add kink* move (endpoint, sign).

    Args:
        k (Diagram): Diagram to analyze.
        random (bool): If True, choose a random candidate; otherwise the first.

    Returns:
        tuple[Endpoint, int] | None: The chosen ``(endpoint, sign)`` or ``None`` if unavailable.
    """
    if "R1" not in settings.allowed_moves:
        return None
    return choice(tuple(find_reidemeister_1_add_kink(k))) if random else next(find_reidemeister_1_add_kink(k), None)


def choose_reidemeister_1_remove_kink(k: Diagram, random: bool = False) -> Endpoint | None:
    """
    Choose one R1 *remove kink* location.

    Args:
        k (Diagram): Diagram to analyze.
        random (bool): If True, choose a random candidate; otherwise the first.

    Returns:
        Endpoint | None: The chosen kink endpoint or ``None`` if unavailable.
    """
    if "R1" not in settings.allowed_moves:
        return None
    if random:
        locations = tuple(find_reidemeister_1_remove_kink(k))
        return choice(locations) if locations else None
    return next(find_reidemeister_1_remove_kink(k), None)


def reidemeister_1_remove_kink(k: Diagram, endpoint: Endpoint, inplace: bool = False) -> Diagram:
    """
    Perform an R1 *unkink* at the given kink-defining endpoint.

    If a *double* kink occurs at the crossing (two loops), the crossing is
    removed and an unknot is added. Otherwise we reconnect the two neighboring
    endpoints around the crossing and delete the crossing.

    Args:
        k (Diagram): Diagram to modify (or copy if ``inplace=False``).
        endpoint (Endpoint): Endpoint that defines the 1-gon (kink) face.
        inplace (bool): Modify in place if True; otherwise return a modified copy.

    Returns:
        Diagram: The diagram after applying the move.

    Notes:
        - If framed, framing changes by ``-1`` on removing a positive kink and by
          ``+1`` on removing a negative kink (determined by endpoint parity).
        - If move tracing is enabled, appends ``"R1-"`` to ``k.attr["_sequence"]``.
    """
    if "R1" not in settings.allowed_moves:
        warnings.warn(
            "An R1 move is being performed, although it is disabled in the global KnotPy settings."
        )

    if not inplace:
        k = k.copy()

    node, position = endpoint

    # Double kink check: both CCW-neighbors point back to the same crossing node.
    if k.nodes[node][(position + 1) % 4].node == k.nodes[node][(position + 2) % 4].node == node:
        k.remove_node(node, remove_incident_endpoints=False)
        add_unknot(k)  # TODO: copy endpoint attributes to new unknot; oriented case as needed.
    else:
        # Single kink: attach endpoints at (pos+1) and (pos+2) and delete the crossing.
        ep_a, ep_b = k.nodes[node][(position + 1) & 3], k.nodes[node][(position + 2) & 3]
        k.set_endpoint(
            endpoint_for_setting=(ep_a.node, ep_a.position),
            adjacent_endpoint=(ep_b.node, ep_b.position),
            create_using=type(ep_b),
            **ep_b.attr,
        )
        k.set_endpoint(
            endpoint_for_setting=(ep_b.node, ep_b.position),
            adjacent_endpoint=(ep_a.node, ep_a.position),
            create_using=type(ep_a),
            **ep_a.attr,
        )
        k.remove_node(node, remove_incident_endpoints=False)

    # Framing update: positive kink removal decreases framing by 1, negative increases by 1.
    if k.is_framed():
        k.framing = k.framing + (-1 if position % 2 else 1)

    # Backtrack Reidemeister moves.
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R1-"

    return k


def reidemeister_1_add_kink(k: Diagram, endpoint_sign_pair: tuple[Endpoint, int], inplace: bool = False) -> Diagram:
    """
    Add an R1 kink at ``endpoint`` with given ``sign`` (``+1`` or ``-1``).

    The kink is created inside the face containing the given endpoint; that face
    gains one extra edge. Attributes of the endpoint and its twin are reconciled
    (intersection via ``common_dict``) and applied consistently when wiring.

    Args:
        k (Diagram): Diagram to modify (or copy if ``inplace=False``).
        endpoint_sign_pair (tuple[Endpoint, int]): ``(endpoint, sign)`` with ``sign in {+1, -1}``.
        inplace (bool): Modify in place if True; otherwise return a modified copy.

    Returns:
        Diagram: The diagram after applying the move.

    Raises:
        TypeError: If ``sign`` is not ``+1`` or ``-1``.

    Notes:
        - If framed, framing increases by ``sign``.
        - If move tracing is enabled, appends ``"R1+"`` to ``k.attr["_sequence"]``.
    """
    if "R1" not in settings.allowed_moves:
        warnings.warn(
            "An R1 move is being performed, although it is disabled in the global KnotPy settings."
        )

    if not inplace:
        k = k.copy()

    endpoint, sign = endpoint_sign_pair
    if sign not in (1, -1):
        raise TypeError(f"Cannot add kink of sign {sign}")

    twin_endpoint = k.twin(endpoint)
    common_attr = common_dict(endpoint.attr, twin_endpoint.attr)

    e_type = type(endpoint)
    t_type = type(twin_endpoint)

    k.add_crossing(crossing := unique_new_node_name(k))

    if sign > 0:
        # Positive kink wiring pattern.
        k.set_endpoint((crossing, 0), (crossing, 1), create_using=e_type, **common_attr)
        k.set_endpoint((crossing, 1), (crossing, 0), create_using=t_type, **endpoint.attr)

        k.set_endpoint((crossing, 2), twin_endpoint)  # attributes copied from twin
        k.set_endpoint(twin_endpoint, (crossing, 2), create_using=e_type, **endpoint.attr)

        k.set_endpoint((crossing, 3), endpoint)  # attributes copied from endpoint
        k.set_endpoint(endpoint, (crossing, 3), create_using=t_type, **twin_endpoint.attr)
    else:
        # Negative kink wiring pattern.
        k.set_endpoint((crossing, 1), (crossing, 2), create_using=e_type, **common_attr)
        k.set_endpoint((crossing, 2), (crossing, 1), create_using=t_type, **endpoint.attr)

        k.set_endpoint((crossing, 3), twin_endpoint)
        k.set_endpoint(twin_endpoint, (crossing, 3), create_using=e_type, **endpoint.attr)

        k.set_endpoint((crossing, 0), endpoint)
        k.set_endpoint(endpoint, (crossing, 0), create_using=t_type, **twin_endpoint.attr)

    if k.is_framed():
        k.framing += sign  # add +1 for positive, -1 for negative

    # Backtrack Reidemeister moves.
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R1+"

    return k


if __name__ == "__main__":
    pass
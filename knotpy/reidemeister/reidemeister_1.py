from itertools import product
from random import choice

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.topology import kinks
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.algorithms.sanity import sanity_check
from knotpy.algorithms.naming import unique_new_node_name
from knotpy._settings import settings
from knotpy.utils.dict_utils import common_dict


def find_reidemeister_1_remove_kink(k: PlanarDiagram):
    """
    Return the location where a Reidemeister type 1 unkink in a planar diagram can be performed.
    Such a location is given by the endpoint defining the 1-face of the kink.

    Args:
        k: The planar diagram where kinks are to be identified and removed,
           represented as an instance of PlanarDiagram.

    Yields:
        The endpoint of each identified kink in the planar diagram as the
        removal point.
    """
    for ep in kinks(k):
        yield ep

def find_reidemeister_1_add_kink(k: PlanarDiagram):
    """
    Find locations (endpoint and sign) of where all possible kinks in the planar diagram can be added.

    Args:
        k (PlanarDiagram): A planar diagram for which possible kink positions are found.

    Returns:
        Generator[tuple]: A generator yielding pairs of
            endpoints and signs representing possible kink positions.
    """

    for ep_sign in product(k.endpoints, (1, -1)):  # could we just return the product?
        yield ep_sign


def choose_reidemeister_1_add_kink(k: PlanarDiagram, random=False):
    """
    Selects a Reidemeister 1 "add kink" move location from the given planar diagram.
    A Reidemeister 1 move adds a small loop to a planar knot or link diagram while preserving its topological
    equivalence.

    If the `random` parameter is set to True, the function selects a random "Add Kink"
    move from all possible moves. If set to False, the function determines and returns the
    first move it identifies. If no valid move exists, the function returns None.

    Args:
        k: The planar knot or link diagram where a Reidemeister 1 "Add Kink" move is to
            be applied.
        random: Controls the selection of the move. If True, a random "Add Kink" move
            is selected. If False, the function returns the first identified move. Defaults
            to False.

    Returns:
        Optional[ReidemeisterMove]: Returns a ReidemeisterMove object representing a valid
        "Add Kink" move if one is found. If no moves are available, returns None.
    """

    if random:
        return choice(tuple(find_reidemeister_1_add_kink(k)))
    else:
        return next(find_reidemeister_1_add_kink(k), None)


def choose_reidemeister_1_remove_kink(k: PlanarDiagram, random=False):
    """
    Selects a kink to remove from a planar diagram using the Reidemeister type I move.

    This function chooses a valid kink for removal from the given planar diagram
    using a Reidemeister type I move. If the random flag is set to True, a random
    kink will be selected from the available options. Otherwise, the first
    available kink will be chosen. If no kink is available, it returns None.

    Args:
        k (PlanarDiagram): The input planar diagram to operate on.
        random (bool): Flag to determine whether to select a kink randomly or
            deterministically. Defaults to False.

    Returns:
        Optional[PlanarDiagram]: The selected kink for removal if available;
            otherwise, None.
    """
    if random:
        locations = tuple(find_reidemeister_1_remove_kink(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_1_remove_kink(k), None)


def reidemeister_1_remove_kink(k: PlanarDiagram, endpoint:Endpoint, inplace=False):
    """
    Perform a Reidemeister type I move (unkink) on a singleton face in a knotted planar diagram and
    adjust the framing if required. This operation simplifies the knot by removing a single crossing.

    Args:
        k (PlanarDiagram): The knotted planar diagram object to modify or clone for modification.
        endpoint (Endpoint): The endpoint of the knot specifying the location of the arc for removal.
        inplace (bool, optional): If True, the operation modifies the provided planar diagram instance
            directly. If False, a new modified instance of the diagram is returned. Defaults to False.

    Returns:
        PlanarDiagram: The planar diagram with one fewer crossing after the operation.
    """

    if not inplace:
        k = k.copy()

    node, position = endpoint

    # Check if there is a double kink at the node
    if k.nodes[node][(position + 1) % 4].node == k.nodes[node][(position + 2) % 4].node == node:
        k.remove_node(node, remove_incident_endpoints=False)
        add_unknot(k)  # TODO: copy endpoint attributes to new unknot, let it be oriented if oriented

    # We only have a single kink
    else:
        # we attach the endpoints at positions (endpoint.position + 1) and (endpoint.position + 2)
        ep_a, ep_b = k.nodes[node][(position + 1) & 3], k.nodes[node][(position + 2) & 3]
        k.set_endpoint(endpoint_for_setting=(ep_a.node, ep_a.position),
                       adjacent_endpoint=(ep_b.node, ep_b.position),
                       create_using=type(ep_b), **ep_b.attr)
        k.set_endpoint(endpoint_for_setting=(ep_b.node, ep_b.position),
                       adjacent_endpoint=(ep_a.node, ep_a.position),
                       create_using=type(ep_a), **ep_a.attr)
        k.remove_node(node, remove_incident_endpoints=False)

    if k.is_framed():
        k.framing = k.framing + (-1 if position % 2 else 1)  # if we remove positive kink, the framing decreases by 1

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R1-"

    return k



def reidemeister_1_add_kink(k: PlanarDiagram, endpoint_sign_pair: tuple, inplace=False):
    """
    Add a Reidemeister 1 kink to a planar diagram. Add the kink in such a way, that the kink is inside the face that
    contains the endpoint (the number of endpoints on the face is increased by 1).

    Args:
        k (PlanarDiagram): The planar diagram to which the kink will be added.
        endpoint_sign_pair (tuple): A tuple containing the specific endpoint and
            the sign of the kink to be added. The sign must either be 1 for a positive
            kink or -1 for a negative kink.
        inplace (bool): A boolean flag. If `True`, modifies the provided `k` diagram
            in place. If `False`, operates on and returns a copy of the diagram.

    Raises:
        TypeError: If the sign provided in `endpoint_sign_pair` is not 1 or -1.

    Returns:
        PlanarDiagram: The updated diagram with the added kink. If `inplace` is set to
        `False`, a new diagram containing the kink is returned, otherwise the original
        modified diagram.
    """

    if not inplace:
        k = k.copy()

    endpoint, sign = endpoint_sign_pair
    if sign != 1 and sign != -1:
        raise TypeError(f"Cannot add kink of sign {sign}")

    twin_endpoint = k.twin(endpoint)
    common_attr = common_dict(endpoint.attr, twin_endpoint.attr)

    e_type = type(endpoint)
    t_type = type(twin_endpoint)

    k.add_crossing(crossing := unique_new_node_name(k))

    if sign > 0:
        k.set_endpoint((crossing, 0), (crossing, 1), create_using=e_type, **common_attr)
        k.set_endpoint((crossing, 1), (crossing, 0), create_using=t_type, **endpoint.attr)

        k.set_endpoint((crossing, 2), twin_endpoint)  # attributes are copied
        k.set_endpoint(twin_endpoint, (crossing, 2), create_using=e_type, **endpoint.attr)

        k.set_endpoint((crossing, 3), endpoint)  # attributes are copied
        k.set_endpoint(endpoint, (crossing, 3), create_using=t_type, **twin_endpoint.attr)
    else:
        k.set_endpoint((crossing, 1), (crossing, 2), create_using=e_type, **common_attr)
        k.set_endpoint((crossing, 2), (crossing, 1), create_using=t_type, **endpoint.attr)

        k.set_endpoint((crossing, 3), twin_endpoint)  # attributes are copied
        k.set_endpoint(twin_endpoint, (crossing, 3), create_using=e_type, **endpoint.attr)

        k.set_endpoint((crossing, 0), endpoint)  # attributes are copied
        k.set_endpoint(endpoint, (crossing, 0), create_using=t_type, **twin_endpoint.attr)

    if k.is_framed():
        k.framing += sign  # if we add a positive kink, the framing increases by 1

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R1+"

    return k



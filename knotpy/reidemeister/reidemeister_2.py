from itertools import combinations
from random import choice
import warnings

from knotpy.classes import PlanarDiagram
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.naming import unique_new_node_name
from knotpy._settings import settings

def find_reidemeister_2_unpoke(k: PlanarDiagram):
    """
    Iterates through the planar diagram to identify bigon regions that allow unpoking via a
    Reidemeister II move, reducing the number of crossings by two.

    Args:
        k (PlanarDiagram): The planar diagram to evaluate for Reidemeister II faces to unpoke.

    Yields:
        ReidemeisterLocationUnpoke: An object representing the location of a
            Reidemeister II unpoke in the planar diagram.
    """

    if "R2" not in settings.allowed_moves:
        return

    # Loop through all faces and yield 2-faces (bigons) with same position parity.
    for face in k.faces:
        if (len(face) == 2 and
                isinstance(k.nodes[face[0].node], Crossing) and
                isinstance(k.nodes[face[1].node], Crossing) and
                face[0].position % 2 != face[1].position % 2):
            yield face


def find_reidemeister_2_poke(k: PlanarDiagram):
    """
    Identifies and generates all possible Reidemeister 2 poke positions within a given planar diagram. A Reidemeister
    poke position denotes a distinct pair of endpoints (over endpoint, under endpoint), both of which reside in the
    same face of the planar diagram. These poke positions are used for Reidemeister 2 transformations.

    Args:
        k (PlanarDiagram): A planar diagram object representing the knot or link.

    Returns:
        Generator[Tuple[Any, Any], None, None]: A generator yielding tuples, where each tuple represents a pair
        of endpoints (over endpoint, under endpoint) for Reidemeister 2 poke positions.
    """

    if "R2" not in settings.allowed_moves:
        return

    for face in k.faces:
        for ep_under, ep_over in combinations(face, 2):
            yield ep_under, ep_over
            yield ep_over, ep_under   # switch over/under



def choose_reidemeister_2_unpoke(k: PlanarDiagram, random=False):
    """
    Chooses a Reidemeister 2 unpoke move that can be applied to a planar diagram. The function searches
    for possible moves and either selects a random one if specified or returns the first move it
    finds. If no moves are applicable, the function returns None.

    Args:
        k (PlanarDiagram): The planar diagram on which the Reidemeister 2 unpoke move is to be
            applied.
        random (bool): If True, selects a random valid move from the available options. If False,
            returns the first move found.

    Returns:
        Optional[ReidemeisterMove]: A valid Reidemeister 2 unpoke move if available, otherwise None.
    """

    if "R2" not in settings.allowed_moves:
        return None

    if random:
        locations = tuple(find_reidemeister_2_unpoke(k))
        return choice(locations) if locations else None
    else:
        return next(find_reidemeister_2_unpoke(k), None)



def choose_reidemeister_2_poke(k: PlanarDiagram, random=False):
    """
    Selects a Reidemeister 2 poke from a given planar diagram, either the first
    available or a random one based on the specified parameter.

    Args:
        k (PlanarDiagram): The planar diagram to be analyzed for possible
            Reidemeister 2 pokes.
        random (bool): If True, the function will return a random Reidemeister 2
            poke. If False, the function will return the first Reidemeister 2 poke
            found. Defaults to False.

    Returns:
        Optional[Any]: Returns the selected Reidemeister 2 poke, either random or
        the first available one. Returns None if no Reidemeister 2 poke is found.
    """

    if "R2" not in settings.allowed_moves:
        return None

    if random:
        return choice(tuple(find_reidemeister_2_poke(k)))
    else:
        return next(find_reidemeister_2_poke(k), None)  # select 1st item


def reidemeister_2_unpoke(k: PlanarDiagram, face, inplace=False):
    """
    Perform a Reidemeister type II "unpoke" operation on a planar diagram.

    This function modifies a planar diagram by unpoking the endpoints that form
    a bigon poke region. The operation reduces the number of crossings in the
    diagram by two and adjusts the corresponding endpoints and arcs. This function
    can either modify the diagram in place or return a modified copy of the diagram,
    depending on the arguments provided.

    Args:
        k (PlanarDiagram): The planar diagram object representing the knot to be
            modified.
        face: The face of the planar diagram where the unpoke operation is to be
            performed.
        inplace (bool, optional): If True, the operation modifies the original diagram.
            If False, a new diagram is returned with the unpoke applied.

    Returns:
        PlanarDiagram: The planar diagram after applying the Reidemeister type II
            unpoke operation.
    """

    # TODO: the code below is cumbersome, replace by inserting phantom temporary bi-vertices

    if "R2" not in settings.allowed_moves:
        warnings.warn("An R2 move is being performed, although it is disabled in the global KnotPy settings.")

    if not inplace:
        k = k.copy()

    ep_a, ep_b = face
    twin_a, twin_b = k.twin(ep_a), k.twin(ep_b)


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

    # print("a", ep_a, "b", ep_b, "ta", twin_a, "tb",twin_b, "ja", jump_a, "jb", jump_b,  "tja",twin_jump_a, "tjb", twin_jump_b, "jta", jump_twin_a, "jtb", jump_twin_b, "tjta", twin_jump_twin_a, "tjtb", twin_jump_twin_b)


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

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R2-"

    return k

def _reversed_endpoint_type(ep):
    if type(ep) is Endpoint or ep is Endpoint:
        return Endpoint
    if type(ep) is OutgoingEndpoint or ep is OutgoingEndpoint:
        return IngoingEndpoint
    if type(ep) is IngoingEndpoint or ep is IngoingEndpoint:
        return OutgoingEndpoint
    raise TypeError()


def reidemeister_2_poke(k: PlanarDiagram, under_over_endpoints, inplace=False):
    """
    Performs a Reidemeister type II poke operation on a given planar diagram, updating the
    diagram with new crossings and endpoints according to the operation.

    This function modifies a planar diagram by introducing two crossings and reconnecting
    endpoints as specified by the over-under relationship of the endpoints provided.
    The `inplace` flag determines whether the operation modifies the original diagram object
    or works on a copied version.

    Args:
        k (PlanarDiagram): The planar diagram on which the poke operation will be performed.
        under_over_endpoints (tuple): A tuple containing two endpoints (one "under" and one "over"),
            which determine the nature of the Reidemeister II poke.
        inplace (bool, optional): If True, the operation modifies the original diagram `k`. If
            False, a modified copy of `k` is returned. Defaults to False.

    Returns:
        PlanarDiagram: The modified planar diagram after performing the Reidemeister II poke.

    Raises:
        TypeError: If `k` is not an instance of `PlanarDiagram`.
        TypeError: If `over_under_endpoints` does not contain valid `Endpoint` instances.
    """

    endpoint_under, endpoint_over = under_over_endpoints


    if not inplace:
        k = k.copy()

    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot add poke in instance of type {type(k)}")

    if not isinstance(endpoint_over, Endpoint) or not isinstance(endpoint_under, Endpoint):
        raise TypeError(f"Cannot add poke in endpoints of type {type(endpoint_over)} and {type(endpoint_under)}.")



    # get endpoint instances and their twins
    twin_o_node, twin_o_pos = twin_o = k.twin(endpoint_over)
    twin_u_node, twin_u_pos = twin_u = k.twin(endpoint_under)
    ep_o_node, ep_o_pos = ep_o = k.twin(twin_o)  # get instance of endpoint_over
    ep_u_node, ep_u_pos = ep_u = k.twin(twin_u)  # get instance of endpoint_under

    # get types (endpoint or ingoing/outgoing endpoint)
    type_o, rev_o = type(ep_o), _reversed_endpoint_type(ep_o)
    type_u, rev_u = type(ep_u), _reversed_endpoint_type(ep_u)

    # create two new crossings
    node_e = unique_new_node_name(k)
    k.add_crossing(node_e)
    node_f = unique_new_node_name(k)
    k.add_crossing(node_f)


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

    # backtrack Reidemeister moves
    if settings.trace_moves:
        k.attr["_sequence"] = k.attr.setdefault("_sequence", "") + "R2+"

    return k
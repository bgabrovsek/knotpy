from itertools import product, combinations
from random import choice

from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.classes import PlanarDiagram
from knotpy.algorithms.structure import kinks
from knotpy.algorithms.disjoint_sum import add_unknot
from knotpy.sanity import sanity_check
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.node_operations import name_for_new_node

_DEBUG_REID = False
_CHECK_SANITY = False


class ReidemeisterLocationUnpoke(ReidemeisterLocation):
    def __init__(self, face):
        if face[0].position % 2 == 0 and face[0].position % 2 == 1:
            self.endpoint_under, self.endpoint_over = face
        else:
            self.endpoint_over, self.endpoint_under = face

        self.color = None  # if color is given, then the arcs involved in the moves will be colored

    def __str__(self):
        return "Unpoke " + str(self.endpoint_under) + str(self.endpoint_over)


class ReidemeisterLocationPoke(ReidemeisterLocation):
    def __init__(self, endpoint_under, endpoint_over):
        self.endpoint_under = endpoint_under
        self.endpoint_over = endpoint_over
        self.color = None  # if color is given, then the arcs involved in the moves will be colored

    def __str__(self):
        return "Poke " + str(self.endpoint_under) + str(self.endpoint_over)


def find_reidemeister_2_unpoke(k: PlanarDiagram):
    """An iterator (generator) over bigon areas/regions that enable us to unpoke (Reidemeister II move). (to reduce the
    number of crossings by 2)
    The areas contain the two endpoints that define it.
    :param k: planar diagram
    :return: an iterator (generator) over poke faces
    """
    # loop through all faces and yield bigons with same position parity
    for face in k.faces:
        if (len(face) == 2 and
                all(isinstance(k.nodes[ep.node], Crossing) for ep in face) and
                face[0].position % 2 != face[1].position % 2):
            yield ReidemeisterLocationUnpoke(face)


def find_reidemeister_2_poke(k: PlanarDiagram):
    """A reidemeister poke position is the pair (over endpoint, under endpoint), where both endpoints lie in the same face.
    :param k:
    :return: generator over pairs of endpoints
    """
    for face in k.faces:
        for ep_over, ep_under in combinations(face, 2):
            yield ReidemeisterLocationPoke(ep_over, ep_under)
            yield ReidemeisterLocationPoke(ep_under, ep_over)  # switch over/under



def choose_reidemeister_2_unpoke(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    if random:
        return choice(tuple(find_reidemeister_2_unpoke(k)))
    else:
        return next(find_reidemeister_2_unpoke(k), None)



def choose_reidemeister_2_poke(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    if random:
        return choice(tuple(find_reidemeister_2_poke(k)))
    else:
        return next(find_reidemeister_2_poke(k), None)  # select 1st item


def reidemeister_2_unpoke(k: PlanarDiagram, location: ReidemeisterLocationUnpoke, inplace=False):
    """Perform a unpoke (Reidemeister type II move) on the endpoints that define a bigon poke region.
        :param k: knotted planar diagram object
        :param location: a list of the two endpoints of the poke region
        :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.

        :return: knot k with two fewer crossings
        """

    if not inplace:
        k = k.copy()

    ep_a, ep_b = location.endpoint_under, location.endpoint_over
    twin_a, twin_b = k.twin(ep_a), k.twin(ep_b)


    DEBUG = _DEBUG_REID or False
    if DEBUG: print("R2 unpoke", k, ep_a, ep_b)


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


def reidemeister_2_poke(k: PlanarDiagram, location: ReidemeisterLocationPoke, inplace=False):
    """
    :param k:
    :param location:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.

    :return:
    """

    DEBUG = _DEBUG_REID or False


    if not inplace:
        k = k.copy()

    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot add poke in instance of type {type(k)}")

    if not isinstance(location.endpoint_over, Endpoint) or not isinstance(location.endpoint_under, Endpoint):
        raise TypeError(f"Cannot add poke in endpoints of type {type(location.endpoint_over)} and {type(location.endpoint_under)}.")


    if DEBUG: print("R2 poke kink", k, location.endpoint_over, location.endpoint_under)


    # get endpoint instances and their twins
    twin_o_node, twin_o_pos = twin_o = k.twin(location.endpoint_over)
    twin_u_node, twin_u_pos = twin_u = k.twin(location.endpoint_under)
    ep_o_node, ep_o_pos = ep_o = k.twin(twin_o)  # get instance of endpoint_over
    ep_u_node, ep_u_pos = ep_u = k.twin(twin_u)  # get instance of endpoint_under

    if DEBUG:
        print("Over", location.endpoint_over, "twin", twin_o, "under", location.endpoint_under, "twin", twin_u)

    # get types (endpoint or ingoing/outgoing endpoint)
    type_o, rev_o = type(ep_o), _reversed_endpoint_type(ep_o)
    type_u, rev_u = type(ep_u), _reversed_endpoint_type(ep_u)

    # create two new crossings
    node_e = name_for_new_node(k)
    k.add_crossing(node_e)
    node_f = name_for_new_node(k)
    k.add_crossing(node_f)


    if DEBUG:
        print("Over", location.endpoint_over, "twin", twin_o, "under", location.endpoint_under, "twin", twin_u, "new nodes", node_e, node_f)


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

    # color newly created poke
    if location.color is not None:
        for face in k.faces:
            if len(face) == 2 and {face[0].node, face[1].node} == {node_e, node_f}:
                face[0].attr["color"] = location.color
                face[1].attr["color"] = location.color
                k.twin(face[0]).attr["color"] = location.color
                k.twin(face[1]).attr["color"] = location.color
    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after poke:", k)
            sanity_check(k)


    return k
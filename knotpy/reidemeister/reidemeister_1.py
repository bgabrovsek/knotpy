from itertools import product
from random import choice

from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.classes import PlanarDiagram
from knotpy.algorithms.structure import kinks
from knotpy.algorithms.components_disjoint import add_unknot
from knotpy.sanity import sanity_check
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.node_operations import name_for_new_node

_DEBUG_REID = False
_CHECK_SANITY = True

class ReidemeisterLocationRemoveKink(ReidemeisterLocation):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.color = None  # if color is given, then the arcs involved in the moves will be colored

    def __str__(self):
        return "Remove kink " + str(self.endpoint)


class ReidemeisterLocationAddKink(ReidemeisterLocation):
    def __init__(self, endpoint, sign):
        self.endpoint = endpoint
        self.sign = sign
        self.color = None  # if color is given, then the arcs involved in the moves will be colored

    def __str__(self):
        return "Add kink " + str(self.endpoint) + {1: "+", -1: "-"}[self.sign]


def find_reidemeister_1_remove_kink(k: PlanarDiagram):
    """An "unkink" position is en endpoint defining the 1-face of the diagram
    :param k:
    :return: set of endpoints
    """
    for ep in kinks(k):
        yield ReidemeisterLocationRemoveKink(ep)


def find_reidemeister_1_add_kink(k: PlanarDiagram):
    """Get positions of possible kinks. Such a position is defined as a pair (endpoint, sign), where sign is 1 or -1.
    :param k:
    :return: generator over elements of the form (endpoint, sign)
    """
    for ep, sign in product(k.endpoints, (1, -1)):  # could we just return the product?
        yield ReidemeisterLocationAddKink(ep, sign)


def choose_reidemeister_1_add_kink(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    if random:
        return choice(tuple(find_reidemeister_1_add_kink(k)))
    else:
        return next(find_reidemeister_1_add_kink(k), None)


def choose_reidemeister_1_remove_kink(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    if random:
        return choice(tuple(find_reidemeister_1_remove_kink(k)))
    else:
        return next(find_reidemeister_1_remove_kink(k), None)


def reidemeister_1_remove_kink(k: PlanarDiagram, location: ReidemeisterLocationRemoveKink, inplace=False):
    """Perform a Reidemeister type I move (unkink) on the singleton region and adjust the framing.
    :param k: knotted planar diagram object
    :param location: the singleton list containing the arc for removal
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return: knot k with one fewer crossing
    """

    DEBUG = _DEBUG_REID or False

    if not inplace:
        k = k.copy()

    # if len(face) != 1:
    #     raise ValueError(f"Cannot perform an unkink on a region of length {len(face)}.")

    if DEBUG: print("R1 remove kink", k, location.endpoint)

    node, position = location.endpoint
    # double kink?
    if k.nodes[node][(position + 1) % 4].node == k.nodes[node][(position + 2) % 4].node == node:
        k.remove_node(node, remove_incident_endpoints=False)
        add_unknot(k)  # TODO: copy endpoint attributes to new unknot, let it be oriented of oriented
    # single kink?
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

    k.framing = k.framing + (-1 if position % 2 else 1)  # if we remove positive kink, the framing decreases by 1

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after remove kink:", k)
            sanity_check(k)

    return k



def reidemeister_1_add_kink(k: PlanarDiagram, location: ReidemeisterLocationAddKink, inplace=False):
    """Add a new kink at endpoint of sign inside the region endpoint belongs to.
    :param k:
    :param location:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return:
    """

    # if not isinstance(k, PlanarDiagram):
    #     raise TypeError(f"Cannot add kink in instance of type {type(k)}")

    # if not isinstance(endpoint, Endpoint):
    #     raise TypeError(f"Cannot add kink in endpoint of type {type(endpoint)}")

    # if not isinstance(sign, int):
    #     raise TypeError(f"Cannot add kink of sign of type {type(sign)}")

    if not inplace:
        k = k.copy()

    DEBUG = _DEBUG_REID or False
    if DEBUG: print("R1 add kink at", location.endpoint, "with sign", location.sign, k)

    if location.sign != 1 and location.sign != -1:
        raise TypeError(f"Cannot add kink of sign {location.sign}")


    twin_endpoint = k.twin(location.endpoint)
    #adj_endpoint = #k.arcs[endpoint][0]
    node = name_for_new_node(k)
    k.add_crossing(node)
    # TODO: ORIENTATION
    if location.sign > 0:
        k.set_arc(((node, 0), (node, 1)))
        k.set_arc(((node, 2), twin_endpoint))
        k.set_arc(((node, 3), location.endpoint))
    elif location.sign < 0:
        k.set_arc(((node, 1), (node, 2)))
        k.set_arc(((node, 3), twin_endpoint))
        k.set_arc(((node, 0), location.endpoint))
    else:
        raise ValueError(f"Unsupported crossing sign {location.sign}.")

    k.framing += location.sign  # if we add a positive kink, the framing increases by 1

    # color newly created poke
    if location.color is not None:
        for face in k.faces:
            if len(face) == 1 and face[0].node == node:
                face[0].attr["color"] = location.color
                k.twin(face[0]).attr["color"] = location.color


    if DEBUG:
        print("R1 result", k)

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after add kink:", k)
            sanity_check(k)

    return k



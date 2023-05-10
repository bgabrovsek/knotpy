import string
import re
from copy import deepcopy

import knotpy as kp
from knotpy.algorithms.node_algorithms import name_for_new_node

_skein_aliases = {"0": ["0", "l0", "l_0", "zero", "a", "type a"],
                  "∞": ["inf", "l_inf", "l∞", "l_∞", "∞", "b", "type b"]}
_reversed_skein_aliases = {val: key for key in _skein_aliases for val in _skein_aliases[key]}


def _smoothing(k, crossing_for_smoothing, join_positions):
    """Connect endpoints of crossings with positions given by join_positions.
    :param k: knot
    :param crossing_for_smoothing:
    :param join_positions: tuple of tuples, if we want to join endpoints 0 & 1 and 2 & 3 of the crossings, a tuple
    ((0, 1), (2, 3) should be given.
    :return: smoothened knot/link
    """
    # TODO: attributes
    c = crossing_for_smoothing

    if k.degree(c) != 4:
        raise ValueError(f"Node {c} is not a 4-valent crossing.")

    k = deepcopy(k)
    c_inst = k.nodes[c]
    k.remove_node(c, remove_incident_arcs=False)

    ep_attr = {pos: k._endpoint_attr[cr, pos] for pos in range(4)}
    for pos in range(4):
        del k._endpoint_attr[(cr, pos)]
    # connect arcs 0 & 1 and 2 & 3
    for pos_a, pos_b in ((0, 1), (2, 3)):
       if adj[pos_a] != adj[pos_b]:  # not a kink?
            k._adj[adj[pos_a]] = adj[pos_b]
            k._adj[adj[pos_b]] = adj[pos_a]
            k._endpoint_attr[adj[pos_a]] = ep_attr[pos_a] | K._endpoint_attr[adj[pos_a]]
            k._endpoint_attr[adj[pos_b]] = ep_attr[pos_b] | K._endpoint_attr[adj[pos_b]]
       else:
            node = name_for_new_node
            k._add_node(node, degree=2)
            k._set_endpoint(endpoint_for_setting=(node, pos_a), adjacent_endpoint=(node, pos_b), **ep_attr[pos_a])
            k._set_endpoint(endpoint_for_setting=(node, pos_b), adjacent_endpoint=(node, pos_a), **ep_attr[pos_b])

    return k


def smoothing_type_A(k, crossing_for_smoothing):
    """ Smoothens the crossing with "type A" smoothing, also known as L_0 smoothing.
    :param k: knot
    :param crossing_for_smoothing:
    :return: smoothened knot
    """
    return _smoothing(k, crossing_for_smoothing, join_positions=((0, 1), (2, 3)))



def smoothing_type_B(k, crossing_for_smoothing):
    """ Smoothens the crossing with "type A" smoothing, also known as L_infinity smoothing.
    :param k: knot
    :param crossing_for_smoothing:
    :return: smoothened knot
    """
    return _smoothing(k, crossing_for_smoothing, join_positions=((2, 3), (3, 0)))



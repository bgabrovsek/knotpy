"""Simple algorithms/functions regarding nodes."""

import string
from collections import defaultdict

from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Vertex, Crossing
from knotpy.classes import PlanarDiagram
# from knotpy.generate.simple import house_graph

__all__ = ['degree_sequence', 'name_for_new_node', "add_node_to", "permute_node", "remove_bivalent_vertices", "mirror", "flip"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def add_node_to(k, node_for_adding, node_type, degree=None):
    """
    :param k: planar diagram instance for adding a node
    :param node_for_adding:
    :param node_type: type of node "X", "V", ...
    :param degree: degree of the node (optional)
    :return:
    """
    if node_type == "X" or node_type == "x":
        if (degree or 4) != 4:
            raise ValueError(f"Cannot add a crossing with degree {degree}")
        k.add_crossing(node_for_adding)
    else:
        raise ValueError(f"Unknown node type {repr(node_type)}")


def degree_sequence(g):
    return tuple(sorted([len(g.nodes[node]) for node in g.nodes]))  # TODO: use degree


# dictionary that stores True for all letters a-zA-Y and False for other hashable objects
_is_letter_but_not_Z = defaultdict(bool, {letter: True for letter in string.ascii_letters[:-1]})
_next_letter = defaultdict(bool, {string.ascii_letters[i]: string.ascii_letters[i + 1] for i in range(51)})


def name_for_new_node(k, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not k.number_of_nodes:
        return default

    if all(_is_letter_but_not_Z[node] for node in k.nodes):
        return _next_letter[max(k.nodes, key=str.swapcase)]

    return max((node for node in k.nodes if isinstance(node, int)), default=0)


def name_for_next_node_generator(k, count=None, default="a"):
    """Returns a natural next available node name for the graph/knot K. If all nodes are letters a-zA-Y, it returns the
    next available letter, otherwise returns the next available integer, or default if the knot is empty."""

    if not count:
        return

    new_node = name_for_new_node(k)

    for _ in range(count-1):
        yield new_node
        if isinstance(new_node, int):
            new_node += 1
        else:
            new_node = _next_letter[new_node] if _is_letter_but_not_Z[new_node] else 0


def permute_node(k, node, permutation):
    """Permute the endpoints of the node of knot k. For example, if p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,3,1]),
    and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
    :param k: knot diagram
    :param node: node of which we permute its endpoints
    :param permutation: permutation given as a dict or list/tuple
    :return: None
    TODO: are there problems regarding endpoint attributes?
    TODO: check if it works for loops (probably does not)
    TODO: make this faster, since it a frequently called operation in canonical() and consumes a lot of tottime and cumtime
    """

    adj_endpoints = [adj_ep for adj_ep in k.nodes[node]]  # save old endpoints, maybe enough just list(...)
    #print(k, "node", node, "perm", permutation)
    node_endpoint_inst = [k.twin(adj_ep) for adj_ep in adj_endpoints]
    for pos, adj_ep in enumerate(adj_endpoints):
        if adj_ep.node != node:  # no loop
            # set adjacent
            k.set_endpoint(endpoint_for_setting=(node, permutation[pos]),
                           adjacent_endpoint=(adj_ep.node, adj_ep.position),
                           create_using=type(adj_ep),
                           **adj_ep.attr)
            # set self
            k.set_endpoint(endpoint_for_setting=adj_ep,
                           adjacent_endpoint=(node, permutation[pos]),
                           create_using=type(node_endpoint_inst[pos]),
                           **node_endpoint_inst[pos].attr)
        else:
            # set adjacent
            k.set_endpoint(endpoint_for_setting=(node, permutation[pos]),
                           adjacent_endpoint=(adj_ep.node, permutation[adj_ep.position]),
                           create_using=type(adj_ep),
                           **adj_ep.attr)


    return

    # convert list/tuple permutation to dict
    if isinstance(p, list) or isinstance(p, tuple):
        p = dict(enumerate(p))

    #invp = inverse_dict(p)

    old_node_data = list(k.nodes[node])  # save old node ccw sequence since it can override
    for pos, ep in enumerate(old_node_data):
        #print("old_node_data[pos]", old_node_data[pos], type(old_node_data[pos]))
        # set endpoint from adjacent crossing
        #print(type(ep))
        if DEBUG: print("setting", ep, "to", (node, p[pos]))
        k.set_endpoint(
            endpoint_for_setting=ep,
            adjacent_endpoint=(node, p[pos]),
            create_using=type(old_node_data[pos]),  # copies the type and "old" attributes
            )
        # set endpoint from crossing
        if DEBUG: print("Setting", node,p[pos], "to", ep)
        k.nodes[node][p[pos]] = ep

    if DEBUG: print("result", k)

def replug_endpoint(k: PlanarDiagram, source_endpoint, destination_endpoint):
    """Unplugs the endpoint endpoint_source and plugs it into endpoint_destination. Takes care of removing the source
    endpoint (shifting bigger indices). Does not insert the destination endpoint, but overwrites it.

    :param k: planar diagram
    :param source_endpoint:
    :param destination_endpoint:
    :return:
    """
    src_node, src_pos = source_endpoint
    dst_node, dst_pos = destination_endpoint

    src_ep = k.endpoints[(src_node, src_pos)]
    adj_ep = k.nodes[src_node][src_pos]

    if isinstance(k.nodes[src_node], Crossing):
        raise ValueError("Cannot unplug endpoint from crossing (this would yield a 3-valent crossing).")

    k.set_endpoint(endpoint_for_setting=(dst_node, dst_pos),
                   adjacent_endpoint=adj_ep,
                   create_using=type(src_ep),
                   **src_ep.attr)
    k.set_endpoint(endpoint_for_setting=adj_ep,
                   adjacent_endpoint=(dst_node, dst_pos),
                   create_using=type(adj_ep),
                   **adj_ep.attr)

    k.remove_endpoint(src_ep)


def unplug(k: PlanarDiagram, node, unplug_endpoint_positions):
    """Unplug endpoints from the node.
    :param k: Planar diagram
    :param node: the node to unplug endpoints
    :param unplug_endpoint_positions: positions/indices to be unplugged
    :return:
    """

    unplug_endpoint_positions = sorted(unplug_endpoint_positions)
    while unplug_endpoint_positions:
        position = unplug_endpoint_positions.pop()  # remove (last) endpoint at index
        # create new leaf node
        new_node = name_for_new_node(k)
        k.add_node(node_for_adding=new_node, create_using=Vertex, degree=1)
        replug_endpoint(k, source_endpoint=(node, position), destination_endpoint=(new_node, 0))


def remove_bivalent_vertices(k:PlanarDiagram, match_attributes=False):
    """Remove bivalent vertices from knotted graph k
    :param k:
    :param match_attributes: if True, removes bivalent vertices only if all four adjacent/incident endpoints match,
    if False, it removes the bivalent vertices regardless
    :return: None
    """
    if not hasattr(k, "vertices"):
        raise TypeError(f"cannot remove bivalent vertices from an instance of type {type(k)}")

    bivalent_vertices = {node for node in k.vertices if len(k.nodes[node]) == 2}

    while bivalent_vertices:
        node = bivalent_vertices.pop()
        # get the incident endpoints b0 and b1 and the incident endpoints a0 and a1 (ai is the twin of bi for i=0,1)
        b0 = k.endpoint_from_pair((node, 0))
        a0 = k.twin(b0)
        b1 = k.endpoint_from_pair((node, 1))
        a1 = k.twin(b1)

        if match_attributes and (b0.attr == a0.attr == b1.attr == a1.attr):
            continue  # skip removing vertex

        if b0.node == a0.node or b1.node == a1.node:
            continue  # cannot remove loops

        if k.is_oriented() and (type(a0) is type(a1)):
            continue  # skip incoherently ordered endpoints

        k.nodes[a0.node][a0.position] = a1
        k.nodes[a1.node][a1.position] = a0
        k.remove_node(node_for_removing=node, remove_incident_endpoints=False)


def flip(k:PlanarDiagram, inplace=False):
    """Flip the diagram by 180 degrees
        :param k:
        :param crossings:
        :return:
        """
    if not inplace:
        k = k.copy()

    for c in list(k.crossings):
        permute_node(k, c, {0:3,1:2,2:1,3:0})
    return k

def mirror(k: PlanarDiagram, crossings=None, inplace=False):
    """Mirror a planar diagram in-place. If no crosssings are given, mirror the whole diagram
    :param k:
    :param crossings:
    :return:
    """

    if not inplace:
        k = k.copy()

    #print(crossings)
    if crossings is None:
        crossings = set(k.crossings)


    if k.is_oriented():
        raise NotImplementedError("Mirroring not implemented on oriented knots")
    else:
        for c in crossings:
            permute_node(k, c, (1, 2, 3, 0))

    return k
    # a → X(d0 b1 c1 c0), b → X(e0 a1 c3 c2), c → X(a3 a2 b3 b2), d → V(a0), e → V(b0) with framing 0


if __name__ == "__main__":
    pass
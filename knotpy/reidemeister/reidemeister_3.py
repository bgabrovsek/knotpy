from itertools import product, chain
from random import choice

from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.sanity import sanity_check
from knotpy.classes.node import Crossing

_CHECK_SANITY = False


class ReidemeisterLocationThree(ReidemeisterLocation):
    """ Class that stores a position where a  Reidemeister 3 move can be performed."""
    def __init__(self, face):
        self.face = face  # a face that contains three endpoints
        self.color = None  # if color is given, then the arcs involved in the moves will be colored

    def __str__(self):
        return "R3 " + str(self.face)


def find_reidemeister_3_triangle(k):
    """A generator that yields triangular faces where Reidemeister III moves can be performed.
    :param k: planar diagram
    :return: yields a non-alternating triangles
    """
    # TODO: make faster by not iterating over all regions
    for face in k.faces:
        if len(face) != 3 or len({ep.node for ep in face}) != 3:
            continue

        if all(type(k.nodes[ep.node]) is Crossing for ep in face) and \
                not (face[0].position % 2 == face[1].position % 2 == face[2].position % 2):
            yield ReidemeisterLocationThree(face)

def choose_reidemeister_3_triangle(k, random=False):
    """Returns a (random) face where a Reidemeister 3 move can be performed.
    :param k: planar diagram
    :param random: if True, the function returns a random face, otherwise it returns the first face is finds
    :return: a triangular face
    """
    if random:
        return choice(tuple(find_reidemeister_3_triangle(k)))
    else:
        return next(find_reidemeister_3_triangle(k), None)  # select 1st item


def reidemeister_3(k, location:ReidemeisterLocationThree, inplace=False):
    """Perform a Reidemeister III move on a non-alternating triangular region.
    :param k: planar diagram
    :param location: ReidemeisterLocationThree object
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return:
    """
    DEBUG = False

    if DEBUG: print("R3", k, location)

    if k.is_oriented():
        raise ValueError("Oriented not yet supported")

    if not inplace:
        k = k.copy()

    # if len(region) != 3:
    #     raise ValueError(f"Cannot perform an Reidemeister III move on a region of length {len(region)}.")

    node_a, pos_a = location.face[0]
    node_b, pos_b = location.face[1]
    node_c, pos_c = location.face[2]
    area_nodes = {node_a, node_b, node_c}

    # redirect endpoints on arcs inside the area
    new_inner_endpoints = {
        (node_a, (pos_a + 1) % 4): (node_b, (pos_b + 2) % 4),  # (node, position + 1) -> (next node, next position + 2)
        (node_a, (pos_a + 2) % 4): (node_c, (pos_c + 1) % 4),  # (node, position + 2) -> (previous node, previous position + 1)
        (node_b, (pos_b + 1) % 4): (node_c, (pos_c + 2) % 4),
        (node_b, (pos_b + 2) % 4): (node_a, (pos_a + 1) % 4),
        (node_c, (pos_c + 1) % 4): (node_a, (pos_a + 2) % 4),
        (node_c, (pos_c + 2) % 4): (node_b, (pos_b + 1) % 4),
    }
    #print("new inner", new_inner_endpoints)

    # redirect the endpoints of the crossings on to the triangle face, directed outside (away from the triangle)
    new_outer_endpoints = {
        (node_a, pos_a): tuple(k.nodes[node_c][(pos_c + 1) % 4]),  # (node, position) -> k.nodes[previous node][previous position - 1]
        (node_a, (pos_a - 1) % 4): tuple(k.nodes[node_b][(pos_b + 2) % 4]),  # (node, position - 1) -> k.nodes[next node][next position + 2]
        (node_b, pos_b): tuple(k.nodes[node_a][(pos_a + 1) % 4]),
        (node_b, (pos_b - 1) % 4): tuple(k.nodes[node_c][(pos_c + 2) % 4]),
        (node_c, pos_c): tuple(k.nodes[node_b][(pos_b + 1) % 4]),
        (node_c, (pos_c - 1) % 4): tuple(k.nodes[node_a][(pos_a + 2) % 4]),
    }
    #print("new outer", new_outer_endpoints)

    # "outer" endpoints change if they point to a crossing of the triangle face
    new_outer_endpoints.update(
        {src_ep: (new_inner_endpoints[dst_ep][0], (new_inner_endpoints[dst_ep][1] + 2) % 4)
         for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] in area_nodes}
    )

    # redirect endpoints that do not lie on the triangle (are incident to it)
    new_external_endpoints = {
        dst_ep: src_ep for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] not in area_nodes
    }

    # actually make the endpoint changes
    for src_ep, dst_ep in chain(new_inner_endpoints.items(), new_outer_endpoints.items(), new_external_endpoints.items()):
        k.set_endpoint(
            endpoint_for_setting=src_ep,
            adjacent_endpoint=dst_ep,
            create_using=type(k.nodes[dst_ep[0]][dst_ep[1]]),  # use old type of endpoint
            **k.nodes[dst_ep[0]][dst_ep[1]].attr  # use old type of attributes
        )

    # save the nodes where the R3 was made to the planar diagram (optional)
    # this is needed when performing multiple R3 moves, so we do not repeat (undo) the moves
    k.attr["_r3"] = area_nodes

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after R3:", k)
            sanity_check(k)

    return k

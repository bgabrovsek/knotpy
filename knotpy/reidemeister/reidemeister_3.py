from itertools import product, chain
from random import choice

from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.classes import PlanarDiagram
from knotpy.algorithms.structure import kinks
from knotpy.algorithms.components_disjoint import add_unknot_in_place
from knotpy.sanity import sanity_check
from knotpy.classes.node import Crossing

_DEBUG_REID = False
_CHECK_SANITY = True

class ReidemeisterLocationThree(ReidemeisterLocation):
    def __init__(self, face):
        self.face = face

    def __str__(self):
        return "R3 " + str(self.face)


def find_reidemeister_3_triangles(k):
    """An iterator (generator) over non-alternating triangular regions that enable us to perform an (Reidemeister III
    move). See also regions().
    :param k: planar diagram object
    :return: an iterator (generator) over non-alternating triangles
    """
    # TODO: make faster by not iterating over all regions
    for face in k.faces:
        if len(face) != 3 or len({ep.node for ep in face}) != 3:
            continue

        if all(type(k.nodes[ep.node]) is Crossing for ep in face) and \
                not (face[0].position % 2 == face[1].position % 2 == face[2].position % 2):
            yield ReidemeisterLocationThree(face)

def choose_reidemeister_3_triangle(k, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    if random:
        return choice(tuple(find_reidemeister_3_triangles(k)))
    else:
        return next(find_reidemeister_3_triangles(k), None)  # select 1st item


def reidemeister_3(k, location:ReidemeisterLocationThree, inplace=False):
    """Perform a Reidemeister III move on a non-alternating triangular region.
    :param k:
    :param face:
    :param inplace: If True, modify the current instance.
                    If False, return a new instance with the modified value.
    :return:
    """

    DEBUG = _DEBUG_REID or False

    if DEBUG: print("R3", k, location)


    if k.is_oriented():
        raise ValueError("Oriented not yet supported")

    if not inplace:
        k = k.copy()

    # if len(region) != 3:
    #     raise ValueError(f"Cannot perform an Reidemeister III move on a region of length {len(region)}.")

    #triangle_nodes = {ep.node for ep in region}
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

    #print("new outer", new_outer_endpoints)


    # redirect endpoints that do not lie on the triangle (are incident to it)
    new_external_endpoints = {
        dst_ep: src_ep for src_ep, dst_ep in new_outer_endpoints.items() if dst_ep[0] not in area_nodes
    }

    #print("new external", new_external_endpoints)


    # new_external_endpoints = {
    #     dest_ep: src_ep if dest_ep[0] not in area_nodes else
    #     for src_ep, dest_ep in new_outer_endpoints.items() if
    # }

    for src_ep, dst_ep in chain(new_inner_endpoints.items(), new_outer_endpoints.items(), new_external_endpoints.items()):
        #print("setting", src_ep, "->", dst_ep)
        k.set_endpoint(
            endpoint_for_setting=src_ep,
            adjacent_endpoint=dst_ep,
            create_using=type(k.nodes[dst_ep[0]][dst_ep[1]]),  # use old type of endpoint
            **k.nodes[dst_ep[0]][dst_ep[1]].attr  # use old type of attributes
        )

    #sprint("After R3", k)

    if _CHECK_SANITY:
        try:
            sanity_check(k)
        except:
            print("Not sane after R3:", k)
            sanity_check(k)

    return k

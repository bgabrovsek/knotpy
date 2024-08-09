"""
A detour move is a move, where a stran passes through multiple other strands


"""
from itertools import product, combinations, chain
from random import choice

from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.classes import PlanarDiagram
from knotpy.algorithms.structure import kinks
from knotpy.algorithms.components_disjoint import add_unknot
from knotpy.sanity import sanity_check
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint, OutgoingEndpoint, IngoingEndpoint
from knotpy.algorithms.node_operations import name_for_new_node



from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.reidemeister._abstract_reidemeister_location import ReidemeisterLocation
from knotpy.reidemeister.reidemeister_1 import (ReidemeisterLocationAddKink, ReidemeisterLocationRemoveKink,
                                                find_reidemeister_1_add_kink, find_reidemeister_1_remove_kink,
                                                reidemeister_1_remove_kink, reidemeister_1_add_kink,
                                                choose_reidemeister_1_remove_kink, choose_reidemeister_1_add_kink)
from knotpy.reidemeister.reidemeister_2 import (ReidemeisterLocationPoke, ReidemeisterLocationUnpoke,
                                                find_reidemeister_2_unpoke, find_reidemeister_2_poke,
                                                reidemeister_2_unpoke, reidemeister_2_poke, choose_reidemeister_2_unpoke,
                                                choose_reidemeister_2_poke)
from knotpy.reidemeister.reidemeister_3 import (ReidemeisterLocationThree, find_reidemeister_3_triangle, reidemeister_3,
                                                choose_reidemeister_3_triangle)
from knotpy.notation.pd import to_pd_notation



def detour_find_reidemeister_1_add_kinks_bigon(k):
    """Finds positions of R1 moves next to an alternating 2-region (bigon), where, after the R1 move, a non-alternating
    triangle (3-gon) is created, such that we can perform a R3 move.
    :param k:
    :return:
    """
    # TODO: could optimize, so that we only add a kink where we have two overstrands, so that there is a possibility
    #  that we are able to reduce it (we cannot reduce alternating diagrams

    # loop through all faces and create R1 moves where the bigons have same position parity
    for face in k.faces:
        if (len(face) == 2 and
                all(isinstance(k.nodes[ep.node], Crossing) for ep in face) and
                face[0].position % 2 == face[1].position % 2):
            yield ReidemeisterLocationAddKink(k.twin(face[0]), -1 if face[0].position % 2 else 1)
            yield ReidemeisterLocationAddKink(k.twin(face[1]), -1 if face[1].position % 2 else 1)


def detour_find_reidemeister_2_pokes_n_gon(k):
    """Finds positions of R2 moves inside a region, where, after the R2 move, a non-alternating
    triangle (3-gon) is created, such that we can perform a R3 move.
    :param k:
    :return:
    """

    # loop through all faces with length > 3 and create R3 moves
    for face in k.faces:
        if any(type(k.nodes[ep.node]) is not Crossing for ep in face):
            # TODO maybe the ones where we make R2 can only be crossings
            continue

        if ((len(face) == 3 and (face[0].position % 2 == face[1].position % 2 == face[2].position % 2))
                or len(face) >= 4):
            for i in range(len(face)):
                ep_a, ep_b, ep_c = face[i], face[(i+1) % len(face)], face[(i+2) % len(face)]

                if (ep_a.position % 2) != (ep_b.position % 2):
                    """we have a over/under strand between a and b, so any poke is ok"""
                    # both pokes
                    yield ReidemeisterLocationPoke(ep_a, ep_c)
                    yield ReidemeisterLocationPoke(ep_c, ep_a)
                elif ep_a.position % 2 == ep_b.position % 2 == 1:
                    yield ReidemeisterLocationPoke(endpoint_under=ep_c, endpoint_over=ep_a)
                elif ep_a.position % 2 == ep_b.position % 2 == 0:
                    yield ReidemeisterLocationPoke(endpoint_under=ep_a, endpoint_over=ep_b)



def find_detour_moves(k):
    """

    :param k:
    :return:
    """
    for rm in chain(detour_find_reidemeister_1_add_kinks_bigon(k), detour_find_reidemeister_2_pokes_n_gon(k)):
        yield rm



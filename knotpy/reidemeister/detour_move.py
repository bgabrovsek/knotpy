"""
A detour move is a move, where a stran passes through multiple other strands


"""
from itertools import chain

from knotpy.classes.node import Crossing
from knotpy.reidemeister.reidemeister_4 import find_reidemeister_4_slide
from knotpy.reidemeister.reidemeister_5 import find_reidemeister_5_twists
from knotpy._settings import settings

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
            yield k.twin(face[0]), -1 if face[0].position % 2 else 1
            yield k.twin(face[1]), -1 if face[1].position % 2 else 1


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
                    # TODO: check if over/under order is correct
                    yield ep_a, ep_c
                    yield ep_c, ep_a
                elif ep_a.position % 2 == ep_b.position % 2 == 1:
                    yield ep_c, ep_a  # c is under, a is over
                elif ep_a.position % 2 == ep_b.position % 2 == 0:
                    yield ep_a, ep_b  # a is under, b is over



def find_detour_moves(k):
    """Finds all detour moves for a knot."""
    # TODO: spefify what move it is, either as a tuple (move_type, location) or (Reidemeister function, location)

    # Add kinks
    if "R1" in settings.allowed_moves:
        for ep_sign in detour_find_reidemeister_1_add_kinks_bigon(k):
            yield ep_sign

    # Add R2 pokes
    if "R2" in settings.allowed_moves:
        for face in detour_find_reidemeister_2_pokes_n_gon(k):
            yield face

    if "R4" in settings.allowed_moves:
        for v_pos in find_reidemeister_4_slide(k, change="nondecreasing"):
            yield v_pos

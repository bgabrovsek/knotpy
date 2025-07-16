"""
A detour move is a move, where a stran passes through multiple other strands


"""

from knotpy._settings import settings
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint
from knotpy.reidemeister.reidemeister_2 import reidemeister_2_poke
from knotpy.reidemeister.reidemeister_4 import find_reidemeister_4_slide, reidemeister_4_slide


def detour_find_reidemeister_1_add_kinks_bigon(k):
    """Finds positions of R1 moves next to an alternating 2-region (bigon), where, after the R1 move, a non-alternating
    triangle (3-gon) is created, such that we can perform a R3 move.
    :param k:
    :return:
    """

    # TODO: could optimize, so that we only add a kink where we have two overstrands, so that there is a possibility
    #  that we are able to reduce it (we cannot reduce alternating diagrams

    if "R1" not in settings.allowed_moves:
        return None

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

    if "R2" not in settings.allowed_moves:
        return

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

    # Do not use R1 increasing moves for simplification
    # Add kinks
    # if "R1" in settings.allowed_moves and settings.r1_increase_simplification:
    #     for ep_sign in detour_find_reidemeister_1_add_kinks_bigon(k):
    #         yield ep_sign

    # Add R2 pokes
    if "R2" in settings.allowed_moves:
        for face in detour_find_reidemeister_2_pokes_n_gon(k):
            yield face

    if "R4" in settings.allowed_moves:
        for v_pos in find_reidemeister_4_slide(k, change="increasing"):
            yield v_pos

    # TODO: can twisting the knotted graph via R5 yield an essential configuration?

def detour_move(k, location, inplace=False):
    """Make the detour move at the given location."""

    # Is the move an R2 poke?
    if isinstance(location, tuple) and len(location) == 2 and isinstance(location[0], Endpoint) and isinstance(location[1], Endpoint):
        return reidemeister_2_poke(k, location, inplace=inplace)

    if isinstance(location, tuple) and len(location) == 2 and isinstance(location[1], list):
        return reidemeister_4_slide(k, location, inplace=inplace)


    #         return "R4"
    # Is the move a R4 slide?

    #         return "R2poke" if detailed else "R2"


    #     # A R2 unpoke is given by a face of length 2
    #     elif isinstance(location, set) and len(location) == 2:
    #         return "R2unpoke" if detailed else "R2"
    #
    #     # A R1 unkink is given by an Endpoint
    #     elif isinstance(location, Endpoint):
    #         return "R1unkink" if detailed else "R1"
    #
    #     # A R2 poke is given by an ordered tuple of Endpoints
    #     elif isinstance(location, tuple) and len(location) == 2 and isinstance(location[0], Endpoint) and isinstance(location[1], Endpoint):
    #         return "R2poke" if detailed else "R2"
    #
    #     # A R1 make kink is given by a tuple of (Endpoint, int)
    #     elif isinstance(location, tuple) and isinstance(location[0], Endpoint) and isinstance(location[1], int):
    #         return "R1kink" if detailed else "R1"

# # A R3 move is given by a face of length 3
#     if reidemeister_move_type == "R3":
#         return reidemeister_3(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R2unpoke":
#         return reidemeister_2_unpoke(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R1unkink":
#         return reidemeister_1_remove_kink(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R2poke":
#         return reidemeister_2_poke(k, location, inplace=inplace)
#     elif reidemeister_move_type == "R1kink":
#         return reidemeister_1_add_kink(k, location, inplace=inplace)
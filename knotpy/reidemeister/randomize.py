"""
Randomize the diagram by performing random Reidemeister moves.

"""

from random import choice

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy._settings import settings

def make_random_reidemeister_move(k: PlanarDiagram | OrientedPlanarDiagram):
    pass

def randomize_diagram(k, maximal_crossings_to_increase=2):
    """
    Perform random Reidemeister moves on a given diagram.

    This function modifies a diagram by applying random Reidemeister moves,
    which are transformations used in knot theory to simplify or alter the
    representation of a knot or link. The user can specify the type of moves
    to include and the number of crossing-increasing moves to perform.

    Parameters:
        k: The initial diagram to be transformed.
        crossing_increasing_moves (int): Optional; the number of crossing-increasing
            moves to perform. Default is 2.

    Raises:
        ValueError: If crossing_increasing_moves is set to a value greater than 0 but
            "R2" or "R1" moves are not included in settings.allowed_moves.

    Returns:
        The transformed diagram after applying the specified random Reidemeister moves.
    """

    from knotpy.reidemeister.space import reidemeister_3_space


    k = k.copy()

    if maximal_crossings_to_increase > 0:
        if maximal_crossings_to_increase == 1 and not "R1" not in settings.allowed_moves:
            raise ValueError("Cannot perform a crossing increasing moves without R1 move")
        elif "R2" not in settings.allowed_moves or "R1" not in settings.allowed_moves:
            raise ValueError("Cannot perform crossing increasing moves without R1 and R2 moves")

    # make random R3 moves
    k = choice(list(reidemeister_3_space(k)))

    # check if we can decrease a crossing or two
    decreasing_moves_allowed = []
    if "R1" in settings.allowed_moves: decreasing_moves_allowed.append("R1unkink")
    if "R2" in settings.allowed_moves: decreasing_moves_allowed.append("R2unpoke")
    if "R4" in settings.allowed_moves: decreasing_moves_allowed.append("R4nonincreasing")
    if "R5" in settings.allowed_moves: decreasing_moves_allowed.append("R5untwist")

    make_random_reidemeister_move(k, decreasing_moves_allowed, inplace=True)
    #sanity_check(k)

    if "R3" in settings.allowed_moves:
        k = choice(list(reidemeister_3_space(k)))

    # make increasing moves
    while (crossing_increasing_moves := crossing_increasing_moves - 1) >= 0:

        increasing_moves_allowed = []
        if "R1" in settings.allowed_moves: increasing_moves_allowed.append("R1kink")
        if "R2" in settings.allowed_moves: increasing_moves_allowed.append("R2poke")
        if "R4" in settings.allowed_moves: increasing_moves_allowed.append("R4increase")
        if "R5" in settings.allowed_moves: increasing_moves_allowed.append("R5twist")

        #print(increasing_moves_allowed)
        from knotpy import yamada_polynomial
        #print("MRRM 0", k, "  ", yamada_polynomial(k), increasing_moves_allowed)

        k = make_random_reidemeister_move(k, increasing_moves_allowed, inplace=False)
        #make_random_reidemeister_move(k, increasing_moves_allowed, inplace=True)

        #print("MRRM 1", k, "  ", yamada_polynomial(k))
        #sanity_check(k)


        if "R3" in settings.allowed_moves:
            k = choice(list(reidemeister_3_space(k)))
        #sanity_check(k)

    return k

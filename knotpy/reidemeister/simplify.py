from knotpy.notation.em import  to_condensed_em_notation, from_condensed_em_notation
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.utils.set_utils import LeveledSet
from knotpy.reidemeister.space import _simplify_greedy_decreasing, crossing_non_increasing_space
from knotpy.reidemeister.reidemeister import reidemeister_preserving_moves_generator, detour_generator, reidemeister_decreasing_moves_generator, flype_generator
from knotpy.algorithms.symmetry import flip
from knotpy._settings import settings

__all__ = ["simplify_decreasing", "simplify_smart", "simplify_non_increasing"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def simplify_decreasing(k: PlanarDiagram, inplace=False):
    """
    Simplify a planar diagram by applying a (non-random) sequence of crossing-decreasing Reidemeister moves
    (R1, R2, R4, R5), until there are no more such moves left. The algorithm is greedy, it performs the
    first crossing-reducing move it finds and continues to do so until there are no more such moves left.

    Args:
        k (PlanarDiagram): The planar diagram to be simplified.
        inplace (bool): Whether to simplify the given diagram in-place. If
            `True`, the input diagram `k` will be modified directly. If `False`,
            the function will create a copy of `k` and perform simplifications
            on it. Defaults to `False`.

    Returns:
        PlanarDiagram: The simplified planar diagram with possibly reduced crossings.
    """


    return _simplify_greedy_decreasing(k, to_canonical=False, inplace=inplace)



def simplify_non_increasing(k:PlanarDiagram, greediness:int = 1):
    """
    Simplifies a planar diagram through Reidemeister R3 moves and crossing-decreasing
    moves. The simplification process is influenced by the specified greediness level.

    Levels of Greediness:
        - Level 0: Iteratively applies all possible R3 moves, followed by crossing-
          decreasing moves until no further simplification is achievable. This is the
          slowest level.
        - Level 1: Similar to Level 0, but at each iteration step, the process only
          continues with diagrams having the lowest number of crossings.
        - Level 2: Focuses on rapid simplification by checking for and applying R3
          moves until a crossing-decreasing move becomes viable. Then takes this
          decreased diagram and repeats the steps.
          level.
        - Level 3: Similar to level 2, except that it returns a diagram immediately
          after it reduces it (does not rerun the loop to check additional R3 moves).

    The method does not perform crossing-increasing Reidemeister moves.

    Args:
        k (PlanarDiagram): The planar diagram to simplify.
        greediness (int): Specifies the level of aggressiveness for simplification.
            Default is 1.

    Returns:
        PlanarDiagram: The simplified planar diagram, or the original diagram if no
        simplifications were applied.
    """

    if isinstance(k, (set, tuple, list)):
        return type(k)(simplify_non_increasing(_) for _ in k)

    if greediness == 0 or greediness == 1:
        if "FLIP" in settings.allowed_moves:
            k = {k, flip(k, inplace=False)}

        return min(crossing_non_increasing_space(k, greediness=greediness, assume_canonical=False))

    elif greediness == 2:
        raise NotImplementedError("Not implemented yet.")

    elif greediness == 3:
        k = k.copy()
        number_of_nodes = len(k)

        # First, try to decrease crossing directly.
        simplify_decreasing(k, inplace=True)
        if len(k) < number_of_nodes:
            return k

        # Second, make crossing preserving moves until there are crossings to remove
        ls = LeveledSet(canonical(k))
        while not ls.is_level_empty(-1):
            ls.new_level()
            for _ in reidemeister_preserving_moves_generator(ls.iter_level(-2)):
                __ = simplify_decreasing(_, inplace=True)
                if len(__) < number_of_nodes:
                    return __
                else:
                    ls.add(canonical(__))

        return next(ls.iter_level(0))

    else:
        raise ValueError(f"Invalid greediness level {greediness}.")


def simplify_smart(k: PlanarDiagram, depth=1, flype=False):
    """
    Make "smart" Reidemeister moves to simplify a diagram. "Smart" moves are performed iteratively
    as follows:

    - Perform all non-increasing moves (R3, decreasing R1 and R2) repeatedly until no new diagrams
      are generated from these moves.
    - Perform crossing-increasing moves (increasing R1, R2, and possibly R5) in such a way that new
      R3 moves are enabled in the subsequent step.

    Args:
        k (PlanarDiagram, set, list, or tuple): Input diagram(s) to be simplified.
        depth (int): Number of iterations of crossing-increasing moves to be executed.
        greediness (int): Controls the extent of exploration during crossing-reducing moves.
            Higher greediness may increase processing time but ensure better reductions.


    Returns:
        PlanarDiagram or list[PlanarDiagram]: The minimal simplified diagram or a list of minimal
        simplified diagrams if multiple diagrams are given as input.
    """

    """
        memory_efficient (bool): If True, the algorithm uses less memory but at the cost of slower 
        computations. Defaults to False.
    """


    print("Simplifying", k)

    greediness = 1
    memory_efficient = True if k.number_of_crossings + 2 * depth < 26 * 2 - 2  else False # store searched knots as strings instead of planar diagram instances (True slightly slower, but more memory efficient)

    print(memory_efficient)

    settings_dump = settings.dump()
    if flype:
        settings.add_allowed_move("FLYPE")

    # if flype and "FLYPE" not in settings.allowed_moves:
    #     raise ValueError("Flyping is not allowed in the settings (check knotpy.settings.allowed_moves)")


    # If multiple diagrams are given, perform steps on each diagram.
    if isinstance(k, (set, list, tuple)):
        return [simplify_smart(_, depth) for _ in k]

    # We start the search with both k and simplified k (since sometimes much reduction is already done via decreasing).
    k = {canonical(k), canonical(simplify_decreasing(k, inplace=True))}  # we start with both k and simplified k

    # If we allow flipping the diagram, flip it.
    if "FLIP" in settings.allowed_moves:
        k |= {canonical(flip(_, inplace=False)) for _ in k}

    # if "FLYPE" in settings.allowed_moves:
    #     print("f")
    #     ls.new_level(canonical(flype_generator(ls.iter_level(-1))))
    # if "FLYPE" in settings.allowed_moves:
    #     print("f")
    #     k |= set(canonical(flype_generator(k)))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in k):
        return min(k)

    # Start off by making non-increasing moves (R3 and similar).
    # TODO: if we take greediness=0, then it takes much longer
    if memory_efficient:
        ls = LeveledSet(items=crossing_non_increasing_space(k, greediness=0, assume_canonical=True),
                        to_string=to_condensed_em_notation,
                        from_string=from_condensed_em_notation
                        )


    else:
        ls = LeveledSet(crossing_non_increasing_space(k, greediness=0, assume_canonical=True))

    # If there are no crossings to reduce, we are done.
    if any(_.number_of_crossings == 0 for _ in ls):
        return min(ls)

    print("0", ls.number_of_items())
    # Crossing-increasing loop
    start = ls.number_of_levels() #
    for depth_index in range(depth):

        print("a", ls.number_of_items())
        # increase crossings
        #ls.new_level(detour_space(ls.levels[-1], assume_canonical=True))
        ls.new_level()
        for lvl in (ls.iter_level(start-2), ls.iter_level(start-1)): #ls.levels[start-1:-1]:
            for k in lvl:
                for _ in detour_generator(k):
                    ls.add(canonical(_))

        print("b", ls.number_of_items())
        start = ls.number_of_levels()

        # if "FLYPE" in settings.allowed_moves:
        #     print("f")
        #     ls.new_level(canonical(flype_generator(ls.iter_level(-1))))

        # explore the new space and reduce the diagrams
        #ls.new_level(crossing_non_increasing_space(ls[-1], greediness=0, assume_canonical=True))
        from knotpy.reidemeister.space import crossing_preserving_space, crossing_decreasing_space
        ls.new_level()
        ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # TODO: if R3 not allowed, does preserving contain the input diagram?

        print("c", ls.number_of_items())
        while True:


            #ls.new_level(crossing_decreasing_space(ls[-1], assume_canonical=True))

            # TODO after adding the bottom three line, it works much faster (16x), but I do not know why
            if greediness == 0:
                ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))
            elif greediness == 1:
                while not ls.is_level_empty(-1):
                    ls.new_level()  # put reduced diagrams to the next level
                    ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))
            else:
                raise ValueError(f"Invalid greediness level {greediness}.")
            print("d", ls.number_of_items())


            if flype: #and "FLYPE" in settings.allowed_moves and depth_index == 0:
                ls.new_level(canonical(flype_generator(ls.iter_level(-1))))

                ls.new_level(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # TODO: if R3 not allowed, do we get ls[-1]?
                ls.extend(crossing_preserving_space(ls.iter_level(-2), assume_canonical=True))  # TODO: if R3 not allowed, do we get ls[-1]?
            else:
                ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))  # TODO: if R3 not allowed, do we get ls[-1]?

            print("e", ls.number_of_items())

            if ls.is_level_empty(-1):
                break




        # If there are no crossings to reduce, we are done.
        if any(_.number_of_crossings == 0 for _ in ls):
            return min(ls)


    settings.load(settings_dump)

    return min(ls)



# def _old_simplify_smart(k: PlanarDiagram, depth=1):
#     """ Make "smart" Reidemeister moves to simplify a diagram. "Smart" moves refer to this process at each step:
#
#     - perform all non-increasing moves (R3, decreasing R1 and R2,...) any number of times, until the set of obtained
#     diagrams stabalizes (no new diagrams are generated with R3, R1, R2, ... moves),
#     - perform all crossing-increasing moves once (increasing R1, R2, and possibly R5), in such a way that at the next
#     step a new R3 move can be performed.
#
#     :param k: Input diagram.
#     :param depth: How many times crossing increasing moves should be performed.
#     :return: The minimal diagram after the above process is applied.
#     """
#
#     # If multiple diagrams are given, perform steps on each diagram.
#     if isinstance(k, (set, list, tuple)):
#         return [simplify_smart(_, depth) for _ in k]
#
#     if not k:
#         return []
#
#     k = canonical(k)
#     # If we allow flipping the diagram, flip it.
#     if "FLIP" in settings.allowed_moves:
#         k = {k, canonical(flip(k, inplace=False))}
#
#     # Level 0: perform all R3 and crossing reducing R2, R1, R4, and R5 moves.
#     ls = LeveledSet(crossing_non_increasing_space(k, greediness=0, assume_canonical=False))
#
#     # If there are no crossings to reduce, we are done.
#     if any(_.number_of_crossings == 0 for _ in ls):
#         return min(ls)
#
#     """
#     For all next levels, increase the number of crossings by 1 or 2 (via R1 and R2 moves),
#     followed by all possible R3 moves and crossing-reducing R1 and R2 moves.
#     """
#     for depth_index in range(depth):
#
#         # increase crossings
#         ls.new_level(detour_space(ls[-1], assume_canonical=True))
#
#         # explore the new space and reduce the diagrams
#         ls.new_level(crossing_non_increasing_space(ls[-1], greediness=0, assume_canonical=True))
#
#         # If there are no crossings to reduce, we are done.
#         if any(_.number_of_crossings == 0 for _ in ls):
#             #print("levels!:", [len(c) for c in ls.levels])
#             return min(ls)
#
#     #print("levels :", [len(c) for c in ls.levels])
#     return min(ls)
#



"""
CORE DUMP at C:

Simplifying Diagram a → V(b3), b → X(c0 d3 c1 a0), c → X(b0 b2 d2 e0), d → X(e3 f0 c2 b1), e → X(c3 g0 f1 d0), f → X(d1 e2 h3 h2), g → X(e1 h1 i0 h0), h → X(g3 g1 f3 f2), i → V(g2
0 2
a 2
b 40
c 117
d 117
e 117
a 117
b 825
c 4970



"""
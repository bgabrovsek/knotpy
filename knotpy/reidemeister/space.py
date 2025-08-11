"""
A Reidemeister space of a specific type is the set of all diagrams reachable
by performing all sequences of the specified Reidemeister move types.

For example, the (crossing-preserving) R3 space of a diagram is the set of all
unique diagrams obtained by applying any number of R3 moves (in any order),
optionally interleaved with other crossing-preserving moves such as R4 slides.

This module provides utilities to explore several such “spaces”: purely
decreasing, purely preserving, non-increasing (preserve then reduce),
and “all moves up to a depth” spaces. Each function is careful to return
diagrams in canonical form where appropriate so equality and deduplication
are fast and reliable.
"""

from collections.abc import Iterable

from knotpy.classes.planardiagram import Diagram, PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.attributes import clear_node_attributes
from knotpy.utils.set_utils import LeveledSet

from knotpy.reidemeister.reidemeister import (
    reidemeister_preserving_moves_generator,
    reidemeister_decreasing_moves_generator,
    detour_generator,
    reidemeister_moves_generator,
)
from knotpy.reidemeister.reidemeister_1 import (
    choose_reidemeister_1_remove_kink,
    reidemeister_1_remove_kink,
)
from knotpy.reidemeister.reidemeister_2 import (
    choose_reidemeister_2_unpoke,
    reidemeister_2_unpoke,
)
from knotpy.reidemeister.reidemeister_4 import (
    choose_reidemeister_4_slide,
    reidemeister_4_slide,
)
from knotpy.reidemeister.reidemeister_5 import (
    choose_reidemeister_5_untwist,
    reidemeister_5_untwist,
)

__all__ = [
    "crossing_decreasing_space",
    "crossing_preserving_space",
    "detour_space",
    "crossing_non_increasing_space",
    "all_reidemeister_moves_space",
]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

# TODO: freezing (immutable diagrams for hashing across runs?)


def _set(
    k: Diagram | set | tuple | list | Iterable,
    to_canonical: bool,
) -> set[Diagram]:
    """Put the diagram(s) into a set, optionally canonicalizing.

    This helper normalizes various input collection types to a `set` of
    diagrams. If `to_canonical` is True, each diagram is mapped to its
    canonical representative before insertion.

    Args:
        k: A diagram or a collection of diagrams (set/tuple/list/Iterable).
        to_canonical: If True, convert each diagram to canonical form.

    Return:
        set[Diagram]: A set containing (possibly canonicalized) diagrams.

    Raises:
        TypeError: If `k` is not a diagram or a supported collection.
    """
    if isinstance(k, set):
        return {canonical(_) for _ in k} if to_canonical else k
    if isinstance(k, (tuple, list, Iterable)):
        return {canonical(_) for _ in k} if to_canonical else set(k)
    if isinstance(k, (PlanarDiagram, OrientedPlanarDiagram)):
        return {canonical(k)} if to_canonical else {k}

    raise TypeError("k must be a PlanarDiagram, OrientedPlanarDiagram, set, tuple or list")


def _filter_minimal_diagrams(diagrams: set[Diagram]) -> set[Diagram]:
    """From the set of diagrams, return only those with the minimal node count.

    This is often useful after exploring spaces: many sequences reach different
    representatives with the same minimal complexity; we typically keep only
    the diagrams with the fewest nodes for follow-up steps or output.

    Args:
        diagrams: A set of diagrams.

    Return:
        set[Diagram]: The subset with minimal |nodes|.
    """
    if not diagrams:
        return set()
    minimal_number_of_nodes = min(len(_) for _ in diagrams)
    return {_ for _ in diagrams if len(_) == minimal_number_of_nodes}


def _simplify_greedy_decreasing(
    k: Diagram | set | tuple | list,
    to_canonical: bool,
    inplace: bool = False,
) -> Diagram | set | tuple | list:
    """
    Simplify a diagram (or a collection of diagrams) by greedily applying a
    sequence of crossing-reducing Reidemeister moves (R2, R1, and—if enabled—
    also decreasing R4 and R5) until no such move remains.

    This is non-random: we always apply the first available decreasing move,
    then continue scanning from the beginning, repeating until fixed point.

    Args:
        k: Diagram or collection (set/list/tuple) of diagrams to simplify.
        to_canonical: If True, canonicalize the result(s) before returning.
        inplace: If True and `k` is a single diagram, modify it in place;
            otherwise operate on a copy.

    Return:
        Diagram | set | tuple | list: A possibly simplified diagram or a
        collection of simplified diagrams (matching the input container shape).
    """
    # Handle containers by mapping recursively.
    if isinstance(k, set):
        return {_simplify_greedy_decreasing(_, to_canonical=to_canonical, inplace=inplace) for _ in k}
    elif isinstance(k, list):
        return [_simplify_greedy_decreasing(_, to_canonical=to_canonical, inplace=inplace) for _ in k]
    elif isinstance(k, tuple):
        return tuple(_simplify_greedy_decreasing(_, to_canonical=to_canonical, inplace=inplace) for _ in k)

    # Single diagram:
    if not inplace:
        k = k.copy()

    while True:
        # Order matters: try R2 unpoke, then R1 unkink, then R5 untwist, then decreasing R4 slide.
        if face := choose_reidemeister_2_unpoke(k, random=False):
            reidemeister_2_unpoke(k, face, inplace=True)
            continue

        if ep := choose_reidemeister_1_remove_kink(k, random=False):
            reidemeister_1_remove_kink(k, ep, inplace=True)
            continue

        if face := choose_reidemeister_5_untwist(k, random=False):
            reidemeister_5_untwist(k, face, inplace=True)
            continue

        if vert_pos := choose_reidemeister_4_slide(k, change="decreasing", random=False):
            reidemeister_4_slide(k, vert_pos, inplace=True)
            continue

        break

    return canonical(k) if to_canonical else k


def crossing_decreasing_space(
    diagrams: Diagram | set | list,
    assume_canonical: bool,
) -> set[Diagram]:
    """
    Remove the crossings in a set of diagrams using Reidemeister I and II
    (and possibly decreasing variants of R4 and R5), returning *all* reduced
    diagrams encountered along the way.

    This explores the entire decreasing space, not only fully reduced endpoints.
    It is primarily useful when you want the full lattice of partial reductions,
    not just “the” simplified result.

    Args:
        diagrams: A diagram or a collection of diagrams to process.
        assume_canonical: If True, assume input diagrams are already canonical.
            If False, inputs are canonicalized before exploration.

    Return:
        set[Diagram]: All diagrams reachable via crossing-reducing sequences,
        in canonical form.
    """
    # Put input diagrams at level 0.
    ls = LeveledSet(_set(diagrams, to_canonical=not assume_canonical))
    while not ls.is_level_empty(-1):
        # Explore one decreasing “step.”
        ls.new_level()
        ls.extend(canonical(set(reidemeister_decreasing_moves_generator(ls.iter_level(-2)))))
    return set(ls)


def crossing_preserving_space(
    diagrams: Diagram | set[Diagram] | list[Diagram],
    assume_canonical: bool = False,
    depth: int | None = None,
) -> set[Diagram]:
    """
    Iteratively perform all possible crossing-preserving moves (R3 and
    crossing-preserving R4 slides) on a diagram or set of diagrams.

    The function does not force canonical form at the input, but it guarantees
    canonical outputs at each level so deduplication is robust.

    Args:
        diagrams: A diagram or set of diagrams on which to perform preserving moves.
        assume_canonical: If True, assume inputs are canonical; otherwise
            canonicalize them once at the start.
        depth: Optional maximum number of preserving “layers” to explore.
            If None, explore until the space closes (no new diagrams).

    Return:
        set[Diagram]: The set of diagrams reachable via preserving moves,
        canonicalized.
    """
    ls = LeveledSet(_set(diagrams, to_canonical=not assume_canonical))

    while not ls.is_level_empty(-1):
        if depth is not None and ls.number_of_levels() >= depth:
            break
        ls.new_level()
        ls.extend(canonical(reidemeister_preserving_moves_generator(ls.iter_level(-2))))

    results = set(ls)
    # Remove _r3 flags that are transient markers used to avoid immediate undo
    # when chaining multiple R3 moves across levels.
    clear_node_attributes(results, "_r3")  # TODO: confirm interactions with flypes/R1/...
    return results


def detour_space(
    diagrams: Diagram | set[Diagram] | list[Diagram],
    assume_canonical: bool,
) -> set[Diagram]:
    """
    Perform all “detour” crossing-increasing moves that are likely to enable
    an immediate R3 in the next step. Concretely, this includes R2 pokes that
    create non-alternating triangles, and R4 slides that increase crossings.

    Args:
        diagrams: A diagram or a set of diagrams.
        assume_canonical: If True, assume inputs are canonical.

    Return:
        set[Diagram]: A set of canonical diagrams after detour moves.
    """
    # Always work with a set of (possibly canonicalized) diagrams.
    diagrams = _set(diagrams, to_canonical=not assume_canonical)
    return {canonical(k) for k in detour_generator(diagrams)}


def crossing_non_increasing_space(
    diagrams: Diagram | set[Diagram] | list[Diagram],
    greediness: int,
    assume_canonical: bool,
) -> set[Diagram]:
    """
    Return the non-increasing “Reidemeister space” of the given diagrams.
    This interleaves preserving (R3/…) and decreasing (R1/R2/… decreasing) moves
    until closure.

    Two “greediness” strategies are supported:

      - Level 0: Iterate: preserve → decrease → preserve → decrease … until no
        further growth. This explores broadly and can be slower.
      - Level 1: At each iteration, keep only diagrams with the *minimal* number
        of nodes, then continue from those. This prunes aggressively.

    Args:
        diagrams: A diagram or collection of diagrams.
        greediness: 0 or 1 (see above).
        assume_canonical: If True, assume inputs are canonical; otherwise
            canonicalize them once at the start.

    Return:
        set[Diagram]: The union of all diagrams reached in the non-increasing space.

    Note:
        It may appear that greediness has little effect for certain inputs;
        this depends on structure—worth double-checking if results look identical.
    """
    diagrams = _set(diagrams, to_canonical=not assume_canonical)

    if greediness == 0:
        # Explore: preserve → decrease → preserve … until closure.
        ls = LeveledSet(crossing_preserving_space(diagrams, assume_canonical=assume_canonical))
        while True:
            ls.new_level(crossing_decreasing_space(ls.iter_level(-1), assume_canonical=True))
            if ls.is_level_empty(-1):
                break
            ls.new_level(crossing_preserving_space(ls.iter_level(-1), assume_canonical=True))
            if ls.is_level_empty(-1):
                break
        return set(ls)

    elif greediness == 1:
        # Always prune to minimal node count before expanding further.
        ls = LeveledSet(_filter_minimal_diagrams(diagrams))
        while not ls.is_level_empty(-1):
            diagrams = crossing_preserving_space(ls.iter_level(-1))
            diagrams = _simplify_greedy_decreasing(diagrams, to_canonical=True, inplace=True)
            diagrams = _filter_minimal_diagrams(diagrams)
            ls.new_level(diagrams)
        return _filter_minimal_diagrams(set(ls))

    else:
        raise ValueError("Greediness level must be 0 or 1.")


def all_reidemeister_moves_space(
    diagrams: Diagram | set[Diagram] | list[Diagram],
    depth: int = 1,
    assume_canonical: bool = False,
) -> set[Diagram]:
    """Make *all* allowed Reidemeister moves up to a given depth.

    This explores breadth-first by layers of single-move applications.
    At each layer, all one-move neighbors (of everything in the previous layer)
    are added, canonicalized, and deduplicated.

    Args:
        diagrams: A diagram or collection of diagrams.
        depth: Number of “single-move” layers to explore.
        assume_canonical: If True, assume inputs are canonical.

    Return:
        set[Diagram]: All diagrams reachable within `depth` layers of moves.
    """
    diagrams = _set(diagrams, to_canonical=not assume_canonical)
    ls = LeveledSet(diagrams)
    for _ in range(depth):
        ls.new_level([canonical(k) for k in reidemeister_moves_generator(ls.iter_level(-1))])
    return set(ls)
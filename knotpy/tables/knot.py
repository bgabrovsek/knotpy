"""
Module for accessing the (Rolfsen) knot table and precomputed invariants.

The knot table PD codes were obtained from:
[C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.org (e.g. August 4, 2025)]
"""

from __future__ import annotations

__all__ = ["knot", "knots", "identify", "knots_generator"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from pathlib import Path
from functools import partial

from knotpy.classes.planardiagram import Diagram
from knotpy.utils.dict_utils import LazyDict
from knotpy.tables.invariant_reader import load_invariant_table
from knotpy.classes.freezing import unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.symmetry import mirror as mirror_diagram
from knotpy.tables.invariant_reader import _eval_diagram_symmetry_dict, _eval_poly
from knotpy.algorithms.orientation import orient, reverse, unorient
from knotpy.tables.link import link
from knotpy.tables.theta import theta
from knotpy.tables.name import _named, safe_clean_and_parse_name
from knotpy._settings import settings
from knotpy.algorithms.topology import is_knot, is_link
from knotpy.reidemeister.simplify import simplify_decreasing
from knotpy.invariants.homflypt import homflypt, _homflypt_xyz_mirror

# Data store configuration
_DATA_DIR = Path(__file__).parent / "data"
_KNOT_TABLE_CROSSINGS = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Lazy dictionaries: indexed by crossing count
_knot_table: list[dict] = [{} for _ in range(max(_KNOT_TABLE_CROSSINGS) + 1)]
_knot_precomputed_homflypt: list[dict] = [{} for _ in range(max(_KNOT_TABLE_CROSSINGS) + 1)]
_knot_precomputed_kauffman: list[dict] = [{} for _ in range(max(_KNOT_TABLE_CROSSINGS) + 1)]

_loaded = False  # Tracks whether tables are already loaded

def _load_knot_table() -> None:
    """Populate lazy tables for diagrams and selected invariants."""
    global _loaded
    if _loaded:
        return  # Already loaded, skip

    for n in _KNOT_TABLE_CROSSINGS:
        _knot_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table,
                filename=_DATA_DIR / f"knots_{n}.csv.gz",
                evaluate=False,
            ),
            eval_function=_eval_diagram_symmetry_dict,
        )

        _knot_precomputed_homflypt[n] = LazyDict(
            load_function=partial(
                load_invariant_table,
                filename=_DATA_DIR / f"knots_homflypt_{n}.csv.gz",
                evaluate=False,
                only_field_name="homflypt"
            ),
            eval_function=_eval_poly,
        )

        _knot_precomputed_kauffman[n] = LazyDict(
            load_function=partial(
                load_invariant_table,
                filename=_DATA_DIR / f"knots_kauffman_{n}.csv.gz",
                evaluate=False,
                only_field_name="kauffman"
            ),
            eval_function=_eval_poly,
        )

    _loaded = True




"""
Oriented
chiral K, K*, -K, -K*
fully amphicheiral K = K* = -K = -K*
negative amphicheiral K = -K*, K* = -K
positive amphicheiral K = K*, -K = -K*
reversible K = -K. *K = -*K


Non-oriented
chiral K, K*
fully amphicheiral, K = K*
negative amphicheiral, K = K*
positive amphicheiral, K = K*
reversible K, K*
"""

def knot(name: str) -> Diagram:
    """
    Return the (unfrozen) diagram for a knot by name.
    """
    _load_knot_table()  # Lazy load

    if (res := safe_clean_and_parse_name(name)) is None:
        raise ValueError(f"Invalid knot name: {name}")

    type_name, number_of_crossings, alt_type, index, mirror, orientation = res

    # checks
    if type_name == "link":
        return link(name)
    if type_name in {"theta", "handcuff"}:
        return theta(name)
    if type_name != "knot":
        raise ValueError(f"Invalid knot type: {name}")
    if number_of_crossings > max(_KNOT_TABLE_CROSSINGS):
        raise ValueError(f"Only knots with up to {max(_KNOT_TABLE_CROSSINGS)} crossings are supported (got: {name})")

    # reconstruct the knot name and retrieve the knot
    base_name = f"{number_of_crossings}{'' if not alt_type else alt_type}_{index}"
    if base_name not in _knot_table[number_of_crossings]:
        raise ValueError(f"Knot {name} not found in the knot table")
    knot_dict = _knot_table[number_of_crossings][base_name]
    k, symmetry = knot_dict["diagram"], knot_dict["symmetry"]

    if not orientation:
        # unoriented
        if not mirror:
            return unfreeze(k, inplace=False)
        else:
            if symmetry in ("fully amphicheiral", "negative amphicheiral", "positive amphicheiral"):
                return _named(unfreeze(k, inplace=False), base_name + "*")
            elif symmetry in ("chiral", "reversible"):
                return canonical(mirror_diagram(k, inplace=False))  # mirror should add a '*' to the name
            else:
                raise ValueError(f"Invalid symmetry: {symmetry}")

    else:
        # oriented
        k_oriented = orient(k)
        if mirror:
            k_oriented = mirror_diagram(k_oriented, inplace=True)   # adds '*' to the name

        if orientation == "+":
            return _named(canonical(k_oriented), "+" + k_oriented.name)
        elif orientation == "-":
            return _named(canonical(reverse(k_oriented, inplace=True)), "-" + k_oriented.name)
        else:
            raise ValueError(f"Invalid orientation: {orientation}")


def knots_generator(
    crossings: int | list[int] | tuple[int, ...] | None = None,
    mirror: bool = False,
    oriented: bool = False
):
    """
    Yield knots with the given number(s) of crossings.
    """
    _load_knot_table()  # Lazy load here

    if crossings is None:
        crossings = _KNOT_TABLE_CROSSINGS

    crossings = [crossings] if isinstance(crossings, int) else list(crossings)

    if any(n > max(_KNOT_TABLE_CROSSINGS) for n in crossings):
        over = min(n for n in crossings if n > max(_KNOT_TABLE_CROSSINGS))
        raise ValueError(
            f"Only knots with up to {max(_KNOT_TABLE_CROSSINGS)} crossings are supported (got: {over})"
        )
    if any(n < 0 for n in crossings):
        raise ValueError("Knots with negative number of crossings are not supported")

    if not oriented:
        # oriented = False
        for n in crossings:
            for knot_dict in _knot_table[n].values():
                k, symmetry = knot_dict["diagram"], knot_dict["symmetry"]
                yield unfreeze(k, inplace=False)
                if mirror and symmetry in ("chiral", "reversible"):
                    yield canonical(mirror_diagram(k, inplace=False))  # adds '*' to the name
    else:
        # oriented = True
        for n in crossings:
            for knot_dict in _knot_table[n].values():
                k, symmetry = knot_dict["diagram"], knot_dict["symmetry"]
                base_name = k.name
                k = orient(k)  # unfreezes

                # + orientation
                yield _named(canonical(k), "+" + base_name)

                # - orientation
                if symmetry in ("chiral", "negative amphicheiral", "positive amphicheiral"):
                    yield _named(canonical(reverse(k, inplace=False)), "-" + base_name)

                if mirror:
                    # mirror + orientation
                    if symmetry in ("chiral", "reversible"):
                        yield _named(canonical(mirror_diagram(k, inplace=False)), "+" + base_name + "*")

                    if symmetry == "chiral":
                        yield _named(canonical(mirror_diagram(reverse(k, inplace=False))), "-" + base_name + "*")

                """
                                                             +  -  +* -*
                chiral:                +K, +K*, -K, -K*      x  x  x  x
                fully amphicheiral:    +K = +K* = -K = -K*   x  -  -  -
                negative amphicheiral: +K = -K*, +K* = -K    x  x  -  -
                positive amphicheiral: +K = +K*, -K = -K*    x  x  -  -
                reversible:            +K = -K. +K* = -K*    x  -  x  -
                """


def knots(crossings, mirror: bool = False, oriented: bool = False) -> list:
    """
    Return a list of knots with the given number(s) of crossings.
    """
    return list(knots_generator(crossings=crossings, mirror=mirror, oriented=oriented))


def knot_precomputed_homflypt(k: Diagram):
    """
    Retrieve the homflypt polynomial for a given knot diagram if it exists in the precomputed knot data.

    Args:
        k (Diagram): The knot diagram to look up.

    Returns:
        Optional[Any]: The homflypt polynomial if the knot diagram is found
        in the precomputed data; otherwise, None.
    """
    if not settings.use_precomputed_invariants:
        return None

    #from knotpy.invariants._symbols import _x, _y, _tmp

    name = k.name

    # the input knot must have a name
    if not name:
        return None

    # the input knot name must make sense
    parsed = safe_clean_and_parse_name(name)
    if parsed is None:
        return None

    type_name, number_of_crossings, alt_type, index, mirror, orientation = parsed

    # the input must be a knot
    if type_name != "knot":
        return None  # TODO: add link support

    try:
        k_candidate = knot(name)
        # the input PD diagram must be the same as in the knot table
        if canonical(k) != k_candidate:  # TODO: orientation error!
            return None

        # we have found the knot in the table, now retrieve the precomputed homflypt polynomial
        base_name = f"{number_of_crossings}{'' if not alt_type else alt_type}_{index}"
        homflypt_poly = _knot_precomputed_homflypt[number_of_crossings][base_name]
        if mirror:
            homflypt_poly = _homflypt_xyz_mirror(homflypt_poly)

        return homflypt_poly

    except ValueError:
        return None

def identify_knot(k: Diagram) -> str | list | None:

    k = canonical(k)
    n = k.number_of_crossings

    # unorient the knot and save the original to k_oriented (None if unoriented)
    if k.is_oriented():
        k_oriented = k
        k = canonical(unorient(k))
    else:
        k_oriented = None



    # search the knot table for k
    if (result := next((key for key, v in _knot_table[n].items() if v["diagram"] == k), None)) is not None:


        if k_oriented is None:
            return result

        if knot("+" + result) == k_oriented:
            return "+" + result

        if knot("-" + result) == k_oriented:
            return "-" + result

        return ["+" + result, "-" + result]



    k = canonical(simplify_decreasing(k))

    # search the knot table for k
    if (result := next((key for key, v in _knot_table[n].items() if v["diagram"] == k), None)) is not None:
        return result


    # find by homflypt
    result = []
    homflypt_polynomial = homflypt(k, "xyz")

    # check knots
    for n_ in range(0, n + 1):
        result += [key for key, p in _knot_precomputed_homflypt[n_].items() if p == homflypt_polynomial]

    # check mirrors
    for n_ in range(0, n + 1):
        result += [key + "*" for key, p in _knot_precomputed_homflypt[n_].items() if _homflypt_xyz_mirror(p) == homflypt_polynomial]

    if not result:
        return None


    if len(result) == 1 and k_oriented is None:
        return result[0]
    else:
        return [s + key for key in result for s in ["+", "-"]]


def identify(k: Diagram) -> str | list | None:

    if is_knot(k):
        return identify_knot(k)
    elif is_link(k):
        return None
    else:
        return None


if __name__ == "__main__":


    pass

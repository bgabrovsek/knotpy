"""
The link table PD codes were obtained in
[C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.org (e.g. August 4, 2025)]
"""

from __future__ import annotations

__all__ = ["link", "links", "links_generator"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from pathlib import Path
from functools import partial

from knotpy.utils.dict_utils import LazyDict
from knotpy.tables.invariant_reader import load_invariant_table
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram, Diagram
from knotpy.classes.freezing import unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.symmetry import mirror as mirror_diagram
from knotpy.tables.invariant_reader import _eval_diagram, _eval_poly
from knotpy.tables.name import safe_clean_and_parse_name, _named
from knotpy.algorithms.orientation import unorient
from knotpy.algorithms.orientation import reverse
from knotpy.invariants.homflypt import homflypt, _homflypt_xyz_mirror
from knotpy.reidemeister.simplify import simplify_decreasing


_DATA_DIR = Path(__file__).parent / "data"
_LINK_TABLE_CROSSINGS = [2, 4, 5, 6, 7, 8]

# Per-crossing lazy stores
_link_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_precomputed_homflypt: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_precomputed_kauffman: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_precomputed_multivariable_alexander: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_precomputed_components: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]

_loaded_link_table = False

def _load_link_table() -> None:
    """Populate lazy tables for links and selected invariants."""
    global _loaded_link_table
    if _loaded_link_table:
        return

    for n in _LINK_TABLE_CROSSINGS:
        _link_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_{n}.csv.gz", evaluate=False, only_field_name="native notation"
            ),
            eval_function=_eval_diagram,
        )

        _link_precomputed_homflypt[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_homflypt_{n}.csv.gz", evaluate=False, only_field_name="homflypt"
            ),
            eval_function=_eval_poly,
        )

        _link_precomputed_kauffman[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_kauffman_{n}.csv.gz", evaluate=False, only_field_name="kauffman"
            ),
            eval_function=_eval_poly,
        )

        _link_precomputed_multivariable_alexander[n] = LazyDict(
            load_function=partial(
                load_invariant_table,
                filename=_DATA_DIR / f"links_multivariable_alexander_{n}.csv.gz", evaluate=False, only_field_name="alexander"
            ),
            eval_function=_eval_poly,
        )

        _link_precomputed_components[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_components_{n}.csv.gz", evaluate=False, only_field_name="components"
            ),
            eval_function=int  #_eval_components_dict,
        )

    _loaded_link_table = True


def link(name: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """Return the (unfrozen) diagram for a link by name."""
    _load_link_table()  # lazy load

    if (res := safe_clean_and_parse_name(name)) is None:
        raise ValueError(f"Invalid link name: {name}")

    type_name, number_of_crossings, alt_type, index, mirror, orientation = res
    oriented = bool(orientation)

    is_reversed = False
    if oriented and (is_reversed := orientation.startswith("-")):
        # reverse "+" in "-"
        orientation = "".join(["-" if c == "+" else "+" for c in orientation])

    # sanity on type
    if type_name == "knot":
        from knotpy.tables.knot import knot
        return knot(name)
    if type_name in {"theta", "handcuff"}:
        from knotpy.tables.theta import theta
        return theta(name)
    if type_name != "link":
        raise ValueError(f"Invalid link type: {name}")

    if number_of_crossings > max(_LINK_TABLE_CROSSINGS):
        raise ValueError(f"Only links with up to {max(_LINK_TABLE_CROSSINGS)} crossings are supported (got: {name})")

    # reconstruct the link name and retrieve the link
    base_name = f"L{number_of_crossings}{'' if not alt_type else alt_type}_{index}"

    number_of_components = _link_precomputed_components[number_of_crossings][base_name]  # TODO: let _link_components only be int, not dict
    if not orientation:
        orientation = "+" * number_of_components
    elif len(orientation) > number_of_components:
        raise ValueError(f"Cannot find the link {base_name}{orientation} - the link {base_name} has only {number_of_components} components")
    elif len(orientation) < number_of_components:
        orientation += orientation[-1] * (number_of_components - len(orientation))
    base_name_o = base_name + orientation

    if base_name_o not in _link_table[number_of_crossings]:
        raise ValueError(f"Link {name} not found in the link table")

    result = _link_table[number_of_crossings][base_name_o]

    if oriented:

        if is_reversed:
            # reverse the orientation
            result = canonical(reverse(result, inplace=False))
            result.name = base_name[:-len(orientation)] + "".join(["-" if c == "+" else "+" for c in orientation])

        if mirror:
            return canonical(mirror_diagram(result, inplace=False))
        else:
            return unfreeze(result, inplace=False)
    else:
        result = canonical(unorient(result))
        result.name = base_name
        if mirror:
            result = canonical(mirror_diagram(result, inplace=False))
        return result


def links_generator(
    crossings: int | list[int] | tuple[int, ...] | None = None,
    mirror: bool = False,
    oriented: bool = False,
):
    """Yield links with the given number(s) of crossings."""
    _load_link_table()  # lazy load

    if crossings is None:
        crossings = _LINK_TABLE_CROSSINGS
    crossings = [crossings] if isinstance(crossings, int) else list(crossings)

    if any(n > max(_LINK_TABLE_CROSSINGS) for n in crossings):
        over = min(n for n in crossings if n > max(_LINK_TABLE_CROSSINGS))
        raise ValueError(
            f"Only links with up to {max(_LINK_TABLE_CROSSINGS)} crossings are supported (got: {over})"
        )
    if any(n < 0 for n in crossings):
        raise ValueError("Links with negative number of crossings are not supported")

    if not oriented:
        # oriented = False
        for n in crossings:
            for k in _link_table[n].values():

                k = canonical(unorient(k))

                if "-" in k.name:  # for an "unoriented" link only take the orientation "+++...+++"
                    continue
                base_name = "".join(c for c in k.name if c != "+" and c != "-")

                k.name = base_name
                yield k

                if mirror:
                    k_mirror = _named(canonical(mirror_diagram(k, inplace=False)), base_name + "*")
                    if k_mirror != k:
                        yield k_mirror

    else:
        # oriented = True
        for n in crossings:
            for k in _link_table[n].values():
                yield unfreeze(k, inplace=False)
                if mirror:
                    yield canonical(mirror_diagram(k, inplace=False))



def links(crossings=None, mirror: bool = False, oriented: bool = False) -> list:
    """Return a list of links with the given number(s) of crossings."""
    return list(links_generator(crossings=crossings, mirror=mirror, oriented=oriented))




def _identify_oriented_link(k: OrientedPlanarDiagram) -> str | list:
    """Try to get the knot name, e.g. '3_1' of 'k'."""
    #print("--", k)
    from knotpy.tables.knot import _knot_precomputed_homflypt
    from knotpy.tables.knot import _candidates

    # find the exact oriented link (or the mirror) in the link table
    for k_, _ in _candidates(k):
        u_ = k_
        print(u_)
        for key, v in _link_table[k.number_of_crossings].items():
            print(key, v, v == u_)
        if (knot_name := next((key for key, v in _link_table[k.number_of_crossings].items() if v == u_), None)) is not None:
            print("YAY!")
            base_name, signs_str = "".join([c for c in knot_name if c not in "+-"]), "".join([c for c in knot_name if c in "+-"])
            return knot_name + _ + signs_str

    # searching the link table failed, find candidates by homflypt polynomial
    link_name_candidates = []
    k = simplify_decreasing(k, inplace=False)
    homflypt_polynomial = homflypt(k, "xyz")
    # check knots
    for n_ in range(0, k.number_of_crossings + 1):
        link_name_candidates += [key for key, p in _knot_precomputed_homflypt[n_].items() if p == homflypt_polynomial]
    # check mirrors
    for n_ in range(0, k.number_of_crossings + 1):
        link_name_candidates += [key + "*" for key, p in _knot_precomputed_homflypt[n_].items() if _homflypt_xyz_mirror(p) == homflypt_polynomial]

    return link_name_candidates
    #return _remove_symmetry_duplicates([s + name for name in knot_name_candidates for s in "+-"])
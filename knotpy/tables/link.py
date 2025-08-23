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
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.freezing import unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.symmetry import mirror as mirror_diagram
from knotpy.tables.invariant_reader import (
    #_eval_diagram_dict,
    _eval_diagram,
    _eval_homflypt_dict,
    _eval_kauffman_dict,
    _eval_multivariable_alexander_dict,
    #_eval_components_dict,
)
from knotpy.tables.name import clean_name, parse_name
from knotpy.algorithms.orientation import unorient

_DATA_DIR = Path(__file__).parent / "data"
_LINK_TABLE_CROSSINGS = [2, 4, 5, 6, 7, 8]

# Per-crossing lazy stores
_link_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_homflypt_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_kauffman_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_multivariable_alexander_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_components_table: list[dict] = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]

_loaded = False


def _load_link_table() -> None:
    """Populate lazy tables for links and selected invariants."""
    global _loaded
    if _loaded:
        return

    for n in _LINK_TABLE_CROSSINGS:
        _link_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_{n}.csv.gz", evaluate=False, only_field_name="native notation"
            ),
            eval_function=_eval_diagram,
        )

        _link_homflypt_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_homflypt_{n}.csv.gz", evaluate=False, only_field_name="homflypt"
            ),
            eval_function=_eval_homflypt_dict,
        )

        _link_kauffman_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_kauffman_{n}.csv.gz", evaluate=False, only_field_name="kauffman"
            ),
            eval_function=_eval_kauffman_dict,
        )

        _link_multivariable_alexander_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table,
                filename=_DATA_DIR / f"links_multivariable_alexander_{n}.csv.gz", evaluate=False, only_field_name="alexander"
            ),
            eval_function=_eval_multivariable_alexander_dict,
        )

        _link_components_table[n] = LazyDict(
            load_function=partial(
                load_invariant_table, filename=_DATA_DIR / f"links_components_{n}.csv.gz", evaluate=False, only_field_name="components"
            ),
            eval_function=int  #_eval_components_dict,
        )

    _loaded = True


def link(name: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """Return the (unfrozen) diagram for a link by name."""
    _load_link_table()  # lazy load

    name = clean_name(name)
    type_name, number_of_crossings, alt_type, index, mirror, orientation = parse_name(name)
    oriented = bool(orientation)

    # sanity on type
    if type_name == "knot":
        raise ValueError("Knots are not links")
    if type_name in {"theta", "handcuff"}:
        raise ValueError("Theta curves or handcuff links are not links")
    if type_name != "link":
        raise ValueError(f"Invalid link type: {name}")

    if number_of_crossings > max(_LINK_TABLE_CROSSINGS):
        raise ValueError(
            f"Only links with up to {max(_LINK_TABLE_CROSSINGS)} crossings are supported (got: {name})"
        )

    base_name = f"L{number_of_crossings}{'' if not alt_type else alt_type}_{index}"

    number_of_components = _link_components_table[number_of_crossings][base_name]  # TODO: let _link_components only be int, not dict
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
        if mirror:
            return canonical(mirror_diagram(result, inplace=False))  # todo: chexk * in name
        else:
            return unfreeze(result, inplace=False)
    else:
        result = unorient(result)
        result.name = base_name

        if mirror:
            return canonical(mirror_diagram(result, inplace=True))
        else:
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

    if not mirror and not oriented:
        for n in crossings:
            for link_dict in _link_table[n].values():
                yield unfreeze(link_dict["diagram"], inplace=False)
    else:
        raise NotImplementedError("Mirror and oriented link table not supported yet")


def links(crossings, mirror: bool = False, oriented: bool = False) -> list:
    """Return a list of links with the given number(s) of crossings."""
    return list(links_generator(crossings=crossings, mirror=mirror, oriented=oriented))
"""
The link table PD codes were obtained in
[C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.org (eg. August 4, 2025)]

"""

__all__ = ["link", "links", "links_generator"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from pathlib import Path
from functools import partial

from knotpy.utils.dict_utils import LazyDict
from knotpy.tables.invariant_reader import load_invariant_table
from knotpy.classes.freezing import freeze
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.notation.native import from_knotpy_notation
from knotpy.tables.invariant_reader import _evaluate_dictionary
from knotpy.tables.name import clean_name, parse_name
from knotpy.classes.freezing import unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.symmetry import mirror as mirror_diagram
from knotpy.tables.invariant_reader import _eval_diagram_dict, _eval_homflypt_dict, _eval_kauffman_dict, _eval_multivariable_alexander_dict, _eval_components_dict

_DATA_DIR = Path(__file__).parent / "data"
_LINK_TABLE_CROSSINGS = [2, 4, 5, 6, 7, 8]
_link_table = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_homflypt_table = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_kauffman_table = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_multivariable_alexander_table = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]
_link_components_table = [{} for _ in range(max(_LINK_TABLE_CROSSINGS) + 1)]

def _evaluate_diagram(unevaluated_value: str) -> PlanarDiagram | OrientedPlanarDiagram:
    return freeze(from_knotpy_notation(unevaluated_value))  # freeze the diagram

def _load_link_table():
    """Loads the knot table from the data directory."""
    for n in _LINK_TABLE_CROSSINGS:
        _link_table[n] = LazyDict(
            load_function=partial(load_invariant_table, filename=_DATA_DIR / f"links_{n}.csv.gz", evaluate=False),
            eval_function=_eval_diagram_dict
        )

        _link_homflypt_table[n] = LazyDict(
            load_function=partial(load_invariant_table, filename=_DATA_DIR / f"link_homflypt_{n}.csv.gz", evaluate=False),
            eval_function=_eval_homflypt_dict
        )

        _link_kauffman_table[n] = LazyDict(
            load_function=partial(load_invariant_table, filename=_DATA_DIR / f"links_kauffman_{n}.csv.gz", evaluate=False),
            eval_function=lambda _: _eval_kauffman_dict
        )

        _link_kauffman_table[n] = LazyDict(
            load_function=partial(load_invariant_table, filename=_DATA_DIR / f"links_multivariable_alexander_{n}.csv.gz", evaluate=False),
            eval_function=lambda _: _eval_multivariable_alexander_dict
        )

        _link_components_table[n] = LazyDict(
            load_function=partial(load_invariant_table, filename=_DATA_DIR / f"links_components_{n}.csv.gz", evaluate=False),
            eval_function=lambda _: _eval_components_dict
        )

def link(name: str) -> PlanarDiagram | OrientedPlanarDiagram:

    name = clean_name(name)
    type_name, number_of_crossings, alt_type, index, mirror, orientation = parse_name(name)

    # check if the knot name makes sense and is in the knot table
    if type_name == "knot":
        raise ValueError("Knots are not links")
    if type_name == "theta" or type_name == "handcuff":
        raise ValueError("Theta curves or handcuff links are not links")
    if type_name != "link":
        raise ValueError(f"Invalid knot type: {name}")

    if number_of_crossings > max(_LINK_TABLE_CROSSINGS):
        raise ValueError(f"Only links with up to {max(_LINK_TABLE_CROSSINGS)} crossings are supported (got: {name})")

    base_name = f"L{number_of_crossings}{'' if not alt_type else alt_type}_{index}"  # remove all properties (mirror, orientation,...)
    if base_name not in _link_table[number_of_crossings]:
        raise ValueError(f"Link {name} not found in the knot table")

    link_dict = _link_table[number_of_crossings][base_name]

    if not mirror and not orientation:
        return unfreeze(link_dict["diagram"], inplace=False)  # make a copy

    if mirror and not orientation:
        return canonical(mirror_diagram(link_dict["diagram"], inplace=False)) # make a copy

    if orientation:
        raise NotImplementedError("Oriented link table not supported yet")


def links_generator(crossings=None, mirror=False, oriented=False):
    """
    Return a generator of knots with the given number(s) of crossings.

    Args:
        crossings (int or iterable of int): Number(s) of crossings to include.
        mirror (bool): If True, include mirror images of knots.
        oriented (bool): If True, include oriented versions of knots.

    Returns:
        list[PlanarDiagram | OrientedPlanarDiagram]: List of knots
    """
    if crossings is None:
        crossings = _LINK_TABLE_CROSSINGS

    crossings = [crossings] if isinstance(crossings, int) else list(crossings)

    if any(n > max(_LINK_TABLE_CROSSINGS) for n in crossings):
        raise ValueError(f"Only links with up to {max(_LINK_TABLE_CROSSINGS)} crossings are supported (got: {min([n for n in crossings if n > max(_LINK_TABLE_CROSSINGS)])})")

    if any(n < 0 for n in crossings):
        raise ValueError("Links with negative number of crossings are not supported")

    if not mirror and not oriented:
        for n in crossings:
            for link_dict in _link_table[n].values():
                yield unfreeze(link_dict["diagram"], inplace=False)

    else:
        raise NotImplementedError("Mirror and oriented link table not supported yet")


def links(crossings, mirror=False, oriented=False) -> list:
    """
    Return a list of links with the given number(s) of crossings.

    Args:
        crossings (int or iterable of int): Number(s) of crossings to include.
        mirror (bool): If True, include mirror images of links.
        oriented (bool): If True, include oriented versions of links.

    Returns:
        list[PlanarDiagram | OrientedPlanarDiagram]: List of links
    """
    return list(links_generator(crossings=crossings, mirror=mirror, oriented=oriented))

_load_link_table()


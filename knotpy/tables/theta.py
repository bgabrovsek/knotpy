"""
The knot table PD codes were obtained in
[C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.org (eg. August 4, 2025)]

"""

__all__ = ["theta", "thetas", "theta_generator", "handcuff", "handcuffs", "handcuff_generator"]
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
from knotpy.tables.invariant_reader import _eval_diagram_dict, _eval_yamada_dict

_DATA_DIR = Path(__file__).parent / "data"
_THETA_CURVE_TABLE_CROSSINGS = [0, 3, 4, 5]
_theta_curve_table = dict()
_theta_curve_yamada_table = dict()

def _evaluate_diagram(unevaluated_value: str) -> PlanarDiagram | OrientedPlanarDiagram:
    return freeze(from_knotpy_notation(unevaluated_value))  # freeze the diagram

def _load_theta_curve_table():
    global _theta_curve_table, _theta_curve_yamada_table
    """Loads the knot table from the data directory."""
    _theta_curve_table = LazyDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / f"theta_curves.csv.gz", evaluate=False),
        eval_function=_eval_diagram_dict
    )

    _theta_curve_yamada_table = LazyDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / f"theta_curves_yamada.csv.gz", evaluate=False),
        eval_function=_eval_yamada_dict
    )



def theta(name: str) -> PlanarDiagram | OrientedPlanarDiagram:

    name = clean_name(name)
    type_name, number_of_crossings, alt_type, index, mirror, orientation = parse_name(name)

    # check if the knot name makes sense and is in the knot table
    if type_name != "theta" and type_name != "handcuff":
        raise ValueError(f"A {type_name} was requested, but only theta curves are supported.")

    type_letter = {"theta": "T", "handcuff": "H"}[type_name]

    if number_of_crossings > max(_THETA_CURVE_TABLE_CROSSINGS):
        raise ValueError(f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported (got: {name})")

    base_name = f"{type_letter}{number_of_crossings}{'' if not alt_type else alt_type}_{index}"  # remove all properties (mirror, orientation,...)
    # print(base_name)
    # print(_theta_curve_table.keys())
    # print(base_name in _theta_curve_table)

    if base_name not in _theta_curve_table:
        raise ValueError(f"Theta curve {name} not found in the knot table")

    theta_dict = _theta_curve_table[base_name]

    if not mirror and not orientation:
        return unfreeze(theta_dict["diagram"], inplace=False)  # make a copy

    if mirror and not orientation:
        return canonical(mirror_diagram(theta_dict["diagram"], inplace=False)) # make a copy

    if orientation:
        raise NotImplementedError("Oriented theta curves not supported yet")


def theta_generator(crossings=None, mirror=False, oriented=False):
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
        crossings = _THETA_CURVE_TABLE_CROSSINGS
    crossings = {crossings, } if isinstance(crossings, int) else set(crossings)

    if any(n > max(_THETA_CURVE_TABLE_CROSSINGS) for n in crossings):
        raise ValueError(f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported (got: {min([n for n in crossings if n > max(_THETA_CURVE_TABLE_CROSSINGS)])})")

    if any(n < 0 for n in crossings):
        raise ValueError("Theta curves with negative number of crossings are not supported")

    if not mirror and not oriented:
        for key in _theta_curve_table:
            if key.startswith("H"):
                continue
            n = int(key[1:key.find("_")])
            if n not in crossings:
                continue

            yield unfreeze(_theta_curve_table[key]["diagram"], inplace=False)
    else:
        raise NotImplementedError("Mirror and oriented theta curves table not supported yet")


def thetas(crossings=None, mirror=False, oriented=False) -> list:
    """
    Return a list of knots with the given number(s) of crossings.

    Args:
        crossings (int or iterable of int): Number(s) of crossings to include.
        mirror (bool): If True, include mirror images of knots.
        oriented (bool): If True, include oriented versions of knots.

    Returns:
        list[PlanarDiagram | OrientedPlanarDiagram]: List of knots
    """
    return list(theta_generator(crossings=crossings, mirror=mirror, oriented=oriented))

def handcuff(name: str) -> PlanarDiagram | OrientedPlanarDiagram:
    return theta(name)

def handcuff_generator(crossings=None, mirror=False, oriented=False):
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
        crossings = _THETA_CURVE_TABLE_CROSSINGS

    crossings = {crossings, } if isinstance(crossings, int) else set(crossings)

    if any(n > max(_THETA_CURVE_TABLE_CROSSINGS) for n in crossings):
        raise ValueError(f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported (got: {min([n for n in crossings if n > max(_THETA_CURVE_TABLE_CROSSINGS)])})")

    if any(n < 0 for n in crossings):
        raise ValueError("Theta curves with negative number of crossings are not supported")

    if not mirror and not oriented:
        for key in _theta_curve_table:
            if key.startswith("T"):
                continue
            n = int(key[1:key.find("_")])
            if n not in crossings:
                continue

            yield unfreeze(_theta_curve_table[key]["diagram"], inplace=False)
    else:
        raise NotImplementedError("Mirror and oriented theta curves table not supported yet")


def handcuffs(crossings=None, mirror=False, oriented=False) -> list:
    """
    Return a list of knots with the given number(s) of crossings.

    Args:
        crossings (int or iterable of int): Number(s) of crossings to include.
        mirror (bool): If True, include mirror images of knots.
        oriented (bool): If True, include oriented versions of knots.

    Returns:
        list[PlanarDiagram | OrientedPlanarDiagram]: List of knots
    """
    return list(theta_generator(crossings=crossings, mirror=mirror, oriented=oriented))

_load_theta_curve_table()


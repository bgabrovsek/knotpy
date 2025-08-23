"""
The knot table PD codes were obtained in
[C. Livingston and A. H. Moore, KnotInfo: Table of Knot Invariants, knotinfo.org (eg. August 4, 2025)]
"""

__all__ = ["theta", "thetas", "theta_generator", "handcuff", "handcuffs", "handcuff_generator"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from pathlib import Path
from functools import partial

from knotpy.utils.dict_utils import LazyDict
from knotpy.tables.invariant_reader import load_invariant_table
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.tables.name import clean_name, parse_name
from knotpy.classes.freezing import unfreeze
from knotpy.algorithms.canonical import canonical
from knotpy.algorithms.symmetry import mirror as mirror_diagram
from knotpy.tables.invariant_reader import _eval_diagram_dict, _eval_yamada_dict

_DATA_DIR = Path(__file__).parent / "data"
_THETA_CURVE_TABLE_CROSSINGS = [0, 3, 4, 5]

# Lazily populated storages
_theta_curve_table: LazyDict | dict = {}
_theta_curve_yamada_table: LazyDict | dict = {}
_tables_loaded = False


def _load_theta_curve_table() -> None:
    """Load theta/handcuff tables lazily (called once)."""
    global _theta_curve_table, _theta_curve_yamada_table, _tables_loaded
    if _tables_loaded:
        return

    _theta_curve_table = LazyDict(
        load_function=partial(
            load_invariant_table,
            filename=_DATA_DIR / "theta_curves.csv.gz",
            evaluate=False,
        ),
        eval_function=_eval_diagram_dict,
    )

    _theta_curve_yamada_table = LazyDict(
        load_function=partial(
            load_invariant_table,
            filename=_DATA_DIR / "theta_curves_yamada.csv.gz",
            evaluate=False,
        ),
        eval_function=_eval_yamada_dict,
    )

    _tables_loaded = True


def _ensure_loaded() -> None:
    """Guard to ensure tables are available before any public call."""
    if not _tables_loaded:
        _load_theta_curve_table()


def theta(name: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """
    Return a theta (or handcuff) diagram by name.

    Supports names like ``T4_1`` or ``H3_1`` (optionally with mirror/orientation,
    where mirror is supported but oriented is not).
    """
    _ensure_loaded()

    name = clean_name(name)
    type_name, number_of_crossings, alt_type, index, mirror, orientation = parse_name(name)

    # type checks (preserve original behavior/messages)
    if type_name != "theta" and type_name != "handcuff":
        raise ValueError(f"A {type_name} was requested, but only theta curves are supported.")

    type_letter = {"theta": "T", "handcuff": "H"}[type_name]

    if number_of_crossings > max(_THETA_CURVE_TABLE_CROSSINGS):
        raise ValueError(
            f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported (got: {name})"
        )

    base_name = f"{type_letter}{number_of_crossings}{'' if not alt_type else alt_type}_{index}"

    if base_name not in _theta_curve_table:
        raise ValueError(f"Theta curve {name} not found in the knot table")

    theta_dict = _theta_curve_table[base_name]

    if not mirror and not orientation:
        return unfreeze(theta_dict["diagram"], inplace=False)

    if mirror and not orientation:
        return canonical(mirror_diagram(theta_dict["diagram"], inplace=False))

    if orientation:
        raise NotImplementedError("Oriented theta curves not supported yet")


def theta_generator(crossings=None, mirror: bool = False, oriented: bool = False):
    """
    Yield theta curves with the given number(s) of crossings.

    Args:
        crossings: int or iterable of int. If None, all supported crossings are used.
        mirror: not supported (kept for API parity).
        oriented: not supported (kept for API parity).
    """
    _ensure_loaded()

    if crossings is None:
        crossings = _THETA_CURVE_TABLE_CROSSINGS
    crossings = {crossings} if isinstance(crossings, int) else set(crossings)

    if any(n > max(_THETA_CURVE_TABLE_CROSSINGS) for n in crossings):
        raise ValueError(
            f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported "
            f"(got: {min([n for n in crossings if n > max(_THETA_CURVE_TABLE_CROSSINGS)])})"
        )

    if any(n < 0 for n in crossings):
        raise ValueError("Theta curves with negative number of crossings are not supported")

    if not mirror and not oriented:
        for key in _theta_curve_table:
            if key.startswith("H"):  # skip handcuffs here
                continue
            n = int(key[1 : key.find("_")])
            if n not in crossings:
                continue
            yield unfreeze(_theta_curve_table[key]["diagram"], inplace=False)
    else:
        raise NotImplementedError("Mirror and oriented theta curves table not supported yet")


def thetas(crossings=None, mirror: bool = False, oriented: bool = False) -> list:
    """Return a list of theta curves for the requested crossings."""
    return list(theta_generator(crossings=crossings, mirror=mirror, oriented=oriented))


def handcuff(name: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """Alias for theta(name) when the name denotes a handcuff."""
    return theta(name)


def handcuff_generator(crossings=None, mirror: bool = False, oriented: bool = False):
    """
    Yield handcuff links with the given number(s) of crossings.

    Args:
        crossings: int or iterable of int. If None, all supported crossings are used.
        mirror: not supported (kept for API parity).
        oriented: not supported (kept for API parity).
    """
    _ensure_loaded()

    if crossings is None:
        crossings = _THETA_CURVE_TABLE_CROSSINGS
    crossings = {crossings} if isinstance(crossings, int) else set(crossings)

    if any(n > max(_THETA_CURVE_TABLE_CROSSINGS) for n in crossings):
        raise ValueError(
            f"Only theta curves with up to {max(_THETA_CURVE_TABLE_CROSSINGS)} crossings are supported "
            f"(got: {min([n for n in crossings if n > max(_THETA_CURVE_TABLE_CROSSINGS)])})"
        )

    if any(n < 0 for n in crossings):
        raise ValueError("Theta curves with negative number of crossings are not supported")

    if not mirror and not oriented:
        for key in _theta_curve_table:
            if key.startswith("T"):  # skip thetas here
                continue
            n = int(key[1 : key.find("_")])
            if n not in crossings:
                continue
            yield unfreeze(_theta_curve_table[key]["diagram"], inplace=False)
    else:
        raise NotImplementedError("Mirror and oriented theta curves table not supported yet")


def handcuffs(crossings=None, mirror: bool = False, oriented: bool = False) -> list:
    """Return a list of handcuff links for the requested crossings."""
    return list(handcuff_generator(crossings=crossings, mirror=mirror, oriented=oriented))
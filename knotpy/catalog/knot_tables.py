import os
from pathlib import Path
from functools import partial
from time import time

from knotpy.utils.dict_utils import LazyLoadEvalDict
from knotpy.catalog.invariant_reader import load_invariant_table, _lazy_invariant_dict_eval
from knotpy.notation.native import from_knotpy_notation
from knotpy.catalog.diagram_reader import load_diagrams_as_dict

_DATA_DIR = Path(__file__).parent / "data"

def _lazy_load_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True),
        eval_function=_lazy_invariant_dict_eval
    )

def _lazy_load_diagrams_from_invariants(filename):
    return LazyLoadEvalDict(
        load_function=partial(load_invariant_table, filename=_DATA_DIR / filename, lazy=True, field_name="native notation"),
        eval_function=from_knotpy_notation
    )

def _lazy_load_diagrams(filename):
    return LazyLoadEvalDict(
    load_function=partial(load_diagrams_as_dict, filename=_DATA_DIR / filename, lazy=True),
    eval_function=from_knotpy_notation
    )

# Load knot tables with invariants.
_knot_invariants_10 = _lazy_load_invariants("knot_invariants_up_to_10_crossings.csv.gz")
_knot_invariants_11 = _lazy_load_invariants("knot_invariants_11_crossings.csv.gz")
_knot_invariants_12 = _lazy_load_invariants("knot_invariants_12_crossings.csv.gz")
_knot_invariants_13 = _lazy_load_invariants("knot_invariants_13_crossings.csv.gz")

# Load link tables with invariants.
_link_invariants_8 = _lazy_load_invariants("link_invariants_up_to_8_crossings.csv.gz")
_link_invariants_9 = _lazy_load_invariants("link_invariants_9_crossings.csv.gz")
_link_invariants_10 = _lazy_load_invariants("link_invariants_10_crossings.csv.gz")
_link_invariants_11 = _lazy_load_invariants("link_invariants_11_crossings.csv.gz")

# Load knot tables (without invariants).
_knot_table_10 = _lazy_load_diagrams_from_invariants("knot_invariants_up_to_10_crossings.csv.gz")
_knot_table_11 = _lazy_load_diagrams_from_invariants("knot_invariants_11_crossings.csv.gz")
_knot_table_12 = _lazy_load_diagrams_from_invariants("knot_invariants_12_crossings.csv.gz")
_knot_table_13 = _lazy_load_diagrams_from_invariants("knot_invariants_13_crossings.csv.gz")

# Load link tables (without invariants)
_link_table_8 = _lazy_load_diagrams_from_invariants("link_invariants_up_to_8_crossings.csv.gz")
_link_table_9 = _lazy_load_diagrams_from_invariants("link_invariants_9_crossings.csv.gz")
_link_table_10 = _lazy_load_diagrams_from_invariants("link_invariants_10_crossings.csv.gz")
_link_table_11 = _lazy_load_diagrams_from_invariants("link_invariants_11_crossings.csv.gz")

# Load theta-curve and handcuff link table (without invariants)
_theta_table_7 = _lazy_load_diagrams("theta-handcuffs-7-crossings.csv.gz")

# 
# for x in _theta_table_7:
#     print(x, _theta_table_7[x])
#     break
#
# for x in _knot_table_13:
#     print(x, _knot_table_13[x])
#     break


def get_knot_from_name(name):
    """
    possible names:
    3_1
    11a_214
    11n_214
    L10a124{0;0}
    L10n54{1}
    t5_1.2
    -t5_2

    3_1:

    0_1: unknot
    3_1 Trefoil
    4_1 Figure Eight
    5_1: Cinquefoil , pentafoil
    5_2: 3-twist knot
    6_1: Stevedore's Knot
    6_2: The Miller Institute Knot
    7_1:  Septafoil, cinquefoil
    9_1 Nonafoil
    8_19 Non-alternating
Hopf link
Whitehead link
Borromean rings
unlink

    """




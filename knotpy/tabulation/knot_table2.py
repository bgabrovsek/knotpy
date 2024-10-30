"""
class for precomputed knots
"""
import numpy as np
import sympy
import csv
import pathlib

from knotpy.notation.em import from_condensed_em_notation
from knotpy.readwrite.load import load_collection_with_invariants_iterator, _line_reader
from knotpy.utils.lazy import LazyLoadDict, LazyDict

_knot_table_csv = pathlib.Path(__file__).parent / "precomputed/knot_invariants_up_to_13_crossings.csv"

_knot_invariants_eval_functions = {
    #"Diagram": _from_name_diagram_pair,
    "Alexander": sympy.sympify,
    "Jones": sympy.sympify,
    "Conway": sympy.sympify,
    "Kauffman": sympy.sympify,
    "HOMFLYPT": sympy.sympify,
    "Unknotting number": int,
}

def _from_name_diagram_pair(pair):
    diagram = from_condensed_em_notation(pair[1])
    diagram.name = pair[0]
    return diagram


def _load_lazy_precomputed_knot_invariant_values():

    global _knot_invariants_eval_functions
    global _knot_table_csv
    column_delimiter = ";"
    csv_reader = csv.reader(_line_reader(_knot_table_csv), delimiter=column_delimiter)

    # we expect 1st row to be "Name" and the 2nd row to be "CEM notation", followed by invariant names
    header = next(csv_reader)
    if header[0] != "Name":
        raise ValueError(f"First row of {_knot_table_csv} is not 'Name'.")
    if header[1] != "CEM notation":
        raise ValueError(f"First row of {_knot_table_csv} is not 'CEM notation'.")

    result_invariants = dict()

    for row in csv_reader:
        # create the inner lazy dictionary for invariants
        led = LazyDict(eval_function=_knot_invariants_eval_functions)
        led.update(zip(header[2:], row[2:]))
        result_invariants[row[0]] = led  # set knot name to dict of lazy invariants

    return result_invariants


def _load_knot_diagrams():

    global _knot_table_csv
    column_delimiter = ";"
    csv_reader = csv.reader(_line_reader(_knot_table_csv), delimiter=column_delimiter)

    # we expect 1st row to be "Name" and the 2nd row to be "CEM notation", followed by invariant names
    header = next(csv_reader)
    if header[0] != "Name":
        raise ValueError(f"First row of {_knot_table_csv} is not 'Name'.")
    if header[1] != "CEM notation":
        raise ValueError(f"First row of {_knot_table_csv} is not 'CEM notation'.")

    result_diagrams = dict() #LazyDict(eval_function=_from_name_diagram_pair)

    for row in csv_reader:
        result_diagrams[row[0]] = (row[0], row[1])  # contains name and CEM notation
    return result_diagrams

def _load_link_diagrams():

    global _knot_table_csv
    column_delimiter = ";"
    csv_reader = csv.reader(_line_reader(_knot_table_csv), delimiter=column_delimiter)

    # we expect 1st row to be "Name" and the 2nd row to be "CEM notation", followed by invariant names
    header = next(csv_reader)
    if header[0] != "Name":
        raise ValueError(f"First row of {_knot_table_csv} is not 'Name'.")
    if header[1] != "CEM notation":
        raise ValueError(f"First row of {_knot_table_csv} is not 'CEM notation'.")

    result_diagrams = dict() #LazyDict(eval_function=_from_name_diagram_pair)

    for row in csv_reader:
        result_diagrams[row[0]] = (row[0], row[1])  # contains name and CEM notation
    return result_diagrams


# global knot invariants
knot_table = LazyDict(eval_function=_from_name_diagram_pair, load_function=_load_knot_diagrams)
knot_table.invariants = LazyLoadDict(_load_lazy_precomputed_knot_invariant_values)

# global link invariants
knot_table = LazyDict(eval_function=_from_name_diagram_pair, load_function=_load_link_diagrams)
knot_table.invariants = LazyLoadDict(_load_lazy_precomputed_knot_invariant_values)


def _crossings_and_index(s: str):
    a, b = s.split("_")
    if a[-1] == "a" or a[-1] == "n":
        a = a[:-1]
    return int(a), int(b)


def _crossings(s: str):
    return _crossings_and_index(s)[0]


def select_knots(crossings=None, min_crossings=None, max_crossings=None, invariant_value=None):
    """Get knot names that satisfy the condition
    :param crossings:
    :param max_crossings:
    :return:
    """
    global knot_table

    if crossings is None:
        min_crossings = min_crossings or 0
        max_crossings = max_crossings or 1000000
    else:
        if min_crossings is not None or max_crossings is not None:
            raise ValueError("We can either select number of crossings or max number of crossings, not both")
        max_crossings = min_crossings = crossings

    knots = [name for name in sorted(knot_table.keys(), key=lambda x: _crossings_and_index(x))
             if min_crossings <= _crossings(name) <= max_crossings]

    if invariant_value is not None:
        knots = [name for name in knots
                 if all(knot_table.invariants[name][key] == value for key, value in invariant_value.items())]

    return {knot: knot_table[knot] for knot in knots}  # TODO: implement with a table View



if __name__ == "__main__":
    import knotpy as kp
    from time import time

    # draw knot table

    diagrams = list(knot_table.values())
    kp.export_pdf(diagrams, "knot_table.pdf")


    t = time()

    def _inv_list(d):
        return tuple(d[n] for n in ["Alexander","Jones","Conway","Kauffman","HOMFLYPT","Symmetry","Symmetry group"])

    print("Knots", len(select_knots(max_crossings=11)))
    jones = {_inv_list(knot_table.invariants[name]) for name in select_knots(max_crossings=11)}
    print(len(jones))

    print(time()-t)


"""
knots 12966
unique jones 9506
unique all 11696



"""
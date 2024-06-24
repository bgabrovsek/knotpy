""" Loading/saving a collection of diagrams"""

import collections.abc
import gzip
import sympy as sp

from knotpy.notation.pd import to_pd_notation
from knotpy.notation.dispatcher import from_notation_dispatcher, to_notation_dispatcher
__all__ = ["save_collection", "load_collection", "save_invariant_collection", "load_invariant_collection"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def load_collection(filename, notation=None):
    """Load a collection of diagrams from a file. One diagram per line.
    :param filename:
    :param notation:
    :return:
    """

    list_of_diagrams = []

    conversion_function = None  # should there be a default?
    if notation:
        conversion_function = from_notation_dispatcher(notation)
    comment = "#"

    if str(filename).lower().endswith(".gz"):
        file = gzip.open(filename, "rt", encoding='utf-8')
    else:
        file = open(filename, "r")

    for line in file:
        line = line.strip()
        #print("line", line)
        # try to figure out the notation
        if line[0] == comment and "notation" in line and conversion_function is None:
            try:
                words = [word for word in line.split(" ") if word]  # strip
                notation = words[words.index("notation") - 1]
                conversion_function = from_notation_dispatcher(notation)
            except ValueError:
                pass
        # get and convert the diagram
        if line and len(line) > 0 and line[0] != comment:
            if conversion_function is None:
                raise ValueError(f"Cannot convert a diagram without providing a notation ({notation} is provided)")
            k = conversion_function(line)
            list_of_diagrams.append(k)
    file.close()

    return list_of_diagrams


def save_collection(filename, iterable, notation="native", comment=None):
    notation = notation.lower()

    # convert to tuple if the collection of diagrams is given as an iterator
    if isinstance(iterable, collections.abc.Iterator):
        iterable = tuple(iterable)

    # select conversion function
    conversion_function = to_notation_dispatcher(notation)

    if str(filename).lower().endswith(".gz"):
        file = gzip.open(filename, "wt", encoding='utf-8')
    else:
        file = open(filename, "w")

    file.write(f"# {len(iterable)} diagrams in {notation} notation\n")
    if comment:
        file.write(f"# {comment}\n")
    for k in iterable:
        s = conversion_function(k) if not isinstance(k, str) else k
        file.write(s + "\n")

    file.close()


def save_invariant_collection(filename, nested_dict: dict, notation="native", comment=None):
    """Save a dictionary of invariants to csv-like format

    :param filename:
    :param nested_dict:
    :param notation:
    :param comment:
    :return:
    """

    # select conversion function
    notation = notation.lower()
    conversion_function = to_notation_dispatcher(notation)

    # open the file
    if str(filename).lower().endswith(".gz"):
        file = gzip.open(filename, "wt", encoding='utf-8')
    else:
        file = open(filename, "w")

    # write comments and basic data
    file.write(f"# {len(nested_dict)} diagrams with invariants in {notation} notation\n")
    if comment:
        file.write(f"# {comment}\n")

    invariant_names = sorted({inv for val in nested_dict.values() for inv in val})

    # header
    file.write("pd; " + "; ".join(invariant_names) + "\n")

    # data
    for k, d in nested_dict.items():
        s = conversion_function(k) if not isinstance(k, str) else k
        invariant_val_str = [str(d[name]) for name in invariant_names]
        file.write(s + "; " + "; ".join(invariant_val_str) + "\n")

    file.close()

#
# def _string_to_invariant(s:str, invariant:str):
#     invariant = invariant.strip().lower()
#     if "," in s:
#         raise NotImplementedError("Cannot convert tuples to polynomial")
#     else:
#         return sp.simplify(s)

def load_invariant_collection(filename, notation=None):
    """Load a collection of diagrams from a file. One diagram per line.
    :param filename:
    :param notation:
    :return:
    """

    dict_of_diagrams = dict()

    # notation
    conversion_function = None  # should there be a default?
    if notation:
        conversion_function = from_notation_dispatcher(notation)
    comment = "#"

    # open the file
    if str(filename).lower().endswith(".gz"):
        file = gzip.open(filename, "rt", encoding='utf-8')
    else:
        file = open(filename, "r")

    invariant_names = None

    for line in file:
        line = line.strip()
        # try to figure out the notation
        if line[0] == comment and "notation" in line and conversion_function is None:
            try:
                words = [word for word in line.split(" ") if word]  # strip
                notation = words[words.index("notation") - 1]
                conversion_function = from_notation_dispatcher(notation)
            except ValueError:
                pass
        # get and convert the diagram
        if line and len(line) > 0 and line[0] != comment:
            #print(line)
            if conversion_function is None:
                raise ValueError(f"Cannot convert a diagram without providing a notation ({notation} is provided)")

            if invariant_names is None:
                #print("ok.")
                _, *invariant_names = line.split(";")

            else:
                knot_str, *invariant_values = line.split(";")

                #print("Knot", knot_str)
                #print("invariant", invariant_values, invariant_names)


                k = conversion_function(knot_str)
                dict_of_diagrams[k] = {name: sp.sympify(value) for name, value in zip(invariant_names, invariant_values)}
                #print(">>>", k)

    file.close()

    return dict_of_diagrams
import gzip
import csv
import io
from pathlib import Path
import types
from collections.abc import Iterator

from knotpy.notation.dispatcher import to_notation_dispatcher
from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ["save_collection", "save_collection_with_invariants",
           "init_collection", "init_collection_with_invariants",
           "append_to_collection", "append_to_collection_with_invariants",
           "extend_collection", "extend_collection_with_invariants",
           "append_comment"]

__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_open_write_file_data = dict()  # contain format and other data for open files that we are writing in
# keys are "notation", "multiple_diagrams_per_line", "invariant_names"}

def _open_if_not_open(file, mode):
    close_file_at_the_end = False
    if not isinstance(file, (io.IOBase, gzip.GzipFile)):
        file = str(file)
        file = gzip.open(file, mode, encoding='utf-8') if file.endswith(".gz") else open(file, mode)
        close_file_at_the_end = True
    return file, close_file_at_the_end


def _extract_invariant_values(invariant_values, invariant_names):
    """get invariant values from dict or tuple of values"""
    if isinstance(invariant_values, dict):
        return [invariant_values[name] for name in invariant_names]
    elif isinstance(invariant_names, str):
        return [invariant_values]
    else:
        if not invariant_values or not invariant_names:
            return []
        return invariant_values


def append_to_collection_with_invariants(file, diagram, invariants=None):
    """Append a single line of diagram(s) and optionally invariants to a file.
    Diagrams can be PlanarDiagram or set/list/tuple of diagrams (depending on the "multiple_diagrams_per_line" option)

    :param file: open file object or filename
    :param diagram: Planar diagram if  writing single diagrams to a file or list/tuple/set if writing multiple
    :param invariants: list or dict of invariants if they are not given in diagrams as dict
    :return:
    """

    if not diagram:
        return

    global _open_write_file_data

    column_delimiter = ";"
    diagram_delimiter = " & "

    # open the file if filename is provided
    file, close_file_at_the_end = _open_if_not_open(file, "at")
    csv_file = csv.writer(file,  delimiter=column_delimiter)

    # load global data about the open file we are appending to
    notation = _open_write_file_data[file.name]["notation"]
    multiple_diagrams_per_line = _open_write_file_data[file.name]["multiple_diagrams_per_line"]
    invariant_names = _open_write_file_data[file.name]["invariant_names"]

    # check if data structure is ok
    if isinstance(diagram, PlanarDiagram) and multiple_diagrams_per_line:
        file.close()
        raise TypeError("Multiple diagrams expected, but single PlanarDiagram instance was given")

    if isinstance(diagram, (set, list, tuple)) and not multiple_diagrams_per_line:
        file.close()
        raise TypeError(f"Single diagram expected, but {type(diagram)} given")

    # include the name in the notation if needed
    notation_function = to_notation_dispatcher(notation)

    # diagrams to string
    if multiple_diagrams_per_line:
        diag_str = diagram_delimiter.join([(f"{d.name}:" if d.name else f"") + notation_function(d) for d in diagram])
    else:
        diag_str = notation_function(diagram)

    # invariant names to string
    inv_str = _extract_invariant_values(invariant_values=invariants, invariant_names=invariant_names)

    csv_file.writerow([diag_str, *inv_str] if multiple_diagrams_per_line else [str(diagram.name), diag_str, *inv_str])

    if close_file_at_the_end:
        file.close()


def append_to_collection(file, diagram):
    append_to_collection_with_invariants(file, diagram, invariants=[])


def append_comment(file, comment):
    """Append a comment to a file.
    :param file: file object or filename
    :param comment:
    :return:
    """
    comment_indicator = "#"

    file, close_file_at_the_end = _open_if_not_open(file, "at")

    file.write(f"{comment_indicator}{comment}\n")
    if close_file_at_the_end:
        file.close()


def extend_collection_with_invariants(file, data: dict):
    """Append multiple diagrams to invariant collection
    :param file:
    :param data:
    :return:
    """
    global _open_write_file_data

    # open the file if filename is provided
    file, close_file_at_the_end = _open_if_not_open(file, "at")
    if file.name not in _open_write_file_data:
        raise ValueError("Cannot extend a collection of invariants if the header has not been written to the file")

    # determine if keys or values have planar diagrams inside
    key, value = next(iter(data.items()))
    if isinstance(key, PlanarDiagram) or _is_iter_pd(key):
        diagrams_are_keys = True
    elif isinstance(value, PlanarDiagram) or _is_iter_pd(value):
        diagrams_are_keys = False
    else:
        raise ValueError("Could not extract diagrams and invariants from iterable")

    for key, value in data.items():
        append_to_collection_with_invariants(file,
                                             diagram=key if diagrams_are_keys else value,
                                             invariants=value if diagrams_are_keys else key)

    if close_file_at_the_end:
        file.close()


def extend_collection(file, iterable):
    file, close_file_at_the_end = _open_if_not_open(file, "at")
    if file.name not in _open_write_file_data:
        raise ValueError("Cannot extend a collection if the header has not been written to the file")

    for diagram in iterable:
        append_to_collection(file, diagram)

    if close_file_at_the_end:
        file.close()


def init_collection_with_invariants(file, multiple_diagrams_per_line=False, notation="CEM", invariant_names=None, comment=None):
    """Inits the file that contains invariants collections
    :param file: file name (creates new file) or open file handler
    :param multiple_diagrams_per_line: will each line contain one diagram or multiple lines?
    :param notation:
    :param invariant_names:
    :param comment:
    :return:

    TODO: add the option to write to a file without clearing it, for example, if we rerun the process (maybe mode=a or r)
    """
    global _open_write_file_data

    column_delimiter = ";"
    if invariant_names is None:
        invariant_names = []

    # open the file
    file, close_file_at_the_end = _open_if_not_open(file, "wt")
    csv_writer = csv.writer(file, delimiter=column_delimiter)  # quoting=csv.QUOTE_MINIMAL

    # save file notation and if there are multiple diagrams per line
    _open_write_file_data[file.name] = {"notation": notation,
                                        "multiple_diagrams_per_line": multiple_diagrams_per_line,
                                        "invariant_names": invariant_names}
    # write comment
    if comment:
        append_comment(file, comment)

    # write header
    if isinstance(invariant_names, str):
        invariant_names = [invariant_names]
    if multiple_diagrams_per_line:
        csv_writer.writerow([f"{notation.strip()} notations", *invariant_names])
    else:
        csv_writer.writerow(["Name", f"{notation.strip()} notation", *invariant_names])

    if close_file_at_the_end:
        file.close()


def init_collection(file, multiple_diagrams_per_line=False, notation="CEM", comment=None):
    """Init a file that contains a list of diagrams."""
    init_collection_with_invariants(file=file, multiple_diagrams_per_line=multiple_diagrams_per_line, notation=notation,
                                    invariant_names=[], comment=comment)


def _is_iter_pd(data):
    # is data a list/set/tuple of PlanarDiagram instances (nested once), raises StopIteration if list is empty
    return isinstance(data, (set, list, tuple)) and isinstance(next(iter(data)), PlanarDiagram)  # TODO: next(..., None) returns None if no generator


def _is_iter_iter_pd(data):
    # data is a list/set/tuple of list/set/tuple of PlanarDiagram instances (nested twice)
    # raises StopIteration if list is empty
    return isinstance(data, (set, list, tuple)) and _is_iter_pd(next(iter(data)))


def _extract_invariant_names(invariant_values, invariant_names=None):
    """get invariant names from values (dict) and names or names if values are set/list"""

    # if invariant values are provided as dict, names are also in the dict keys
    if isinstance(invariant_values, dict):

        if invariant_names is None:
            return list(invariant_values)  # names are only in dict keyes

        if isinstance(invariant_names, str) and invariant_names in invariant_values:
            return [invariant_names]

        if set(invariant_names).issubset(invariant_values):
            return list(invariant_names)  # filter only the names if they are stored as keys and names
        else:
            raise ValueError("Not all listed invariant names are in invariant values dictionary")

    if isinstance(invariant_values, (list, tuple)):
        if len(invariant_values) == len(invariant_names):
            return list(invariant_names)
        else:
            raise ValueError("Number of invariant names does not match the number of invariant values")

    if not invariant_values and not invariant_names:
        return []

    if isinstance(invariant_names, str):  # only one invariant is given
        return invariant_names

    raise ValueError("Invariant values must be a list or tuple or string or None")



def save_collection_with_invariants(filename, data: dict, invariant_names=None, notation="CEM", comment=None):
    """Save diagrams to a file. The diagrams and invariants should be dictionaries, where either keys or values are
    diagrams or invariant values
    :param filename:
    :param data:
    :param invariant_names: if None, invariants are extracted from values, or they are no invariants if we have no values
    :param notation:
    :param comment:
    :return:
    """

    global _open_write_file_data


    # determine if keys or values have planar diagrams inside
    key, value = next(iter(data.items()))
    if isinstance(key, PlanarDiagram) or _is_iter_pd(key):
        diagrams_are_keys = True
        invariant_names = _extract_invariant_names(value, invariant_names)
        multiple_diagrams_per_line = not isinstance(key, PlanarDiagram)

    # {invariants: diagrams}
    elif isinstance(value, PlanarDiagram) or _is_iter_pd(value):
        diagrams_are_keys = False
        invariant_names = _extract_invariant_names(key, invariant_names)
        multiple_diagrams_per_line = not isinstance(value, PlanarDiagram)

    # something else
    else:
        raise ValueError("Could not extract diagrams and invariants from iterable")

    filename = str(filename)
    with gzip.open(str(filename), "wt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "wt") as file:

        init_collection_with_invariants(file=file,
                                        multiple_diagrams_per_line=multiple_diagrams_per_line,
                                        notation=notation,
                                        invariant_names=invariant_names,
                                        comment=comment)

        for key, value in data.items():
            append_to_collection_with_invariants(file,
                                                 diagram=key if diagrams_are_keys else value,
                                                 invariants=value if diagrams_are_keys else key)

        if file.name in _open_write_file_data:
            del _open_write_file_data[file.name]



def save_collection(filename, iterable, notation="CEM", comment=None):
    """
    Save diagrams to a file.  The data can be a list/tuple/set of diagrams or list/tuple/set of list/tuple/set diagrams.
    If iterable is a generator, then the function expects a generator of diagrams
    :param filename:
    :param iterable: diagrams
    :param notation:
    :param comment:
    :return:
    """
    global _open_write_file_data

    filename = str(filename)
    with gzip.open(str(filename), "wt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "wt") as file:

        if comment:
            append_comment(file, comment)

        # if no data is given, close and exit
        if not iterable:
            file.close()
            return

        if not hasattr(iterable, "__len__") or _is_iter_pd(iterable):
            multiple_diagrams_per_line = False
        elif _is_iter_iter_pd(iterable):
            multiple_diagrams_per_line = True
        else:
            raise TypeError("iterable should be iterator over diagrams or iterator of iterators of diagrams")

        init_collection(file, multiple_diagrams_per_line=multiple_diagrams_per_line, notation=notation, comment=None)
        # TODO: add comment with number of diagrams

        for k in iterable:
            append_to_collection_with_invariants(file, k, invariants=[])

        if file.name in _open_write_file_data:
            del _open_write_file_data[file.name]


if __name__ == "__main__":
    # testing
    import knotpy as kp
    import sympy
    k31 = kp.from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", name="3_1")
    k41 = kp.from_pd_notation("[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]", name="4_1")
    k51 = kp.from_pd_notation("[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]", name="5_1")
    k52 = kp.from_pd_notation("[[1,5,2,4],[3,9,4,8],[5,1,6,10],[7,3,8,2],[9,7,10,6]]", name="5_2")
    k61 = kp.from_pd_notation("[[1,7,2,6],[3,10,4,11],[5,3,6,2],[7,1,8,12],[9,4,10,5],[11,9,12,8]]", name="6_2")

    j31 = sympy.sympify("t+ t^3-t^4")
    j41 = sympy.sympify("t^(-2)-t^(-1)+ 1-t+ t^2")
    j51 = sympy.sympify("t^2+ t^4-t^5+ t^6-t^7")

    h31 = sympy.sympify("(2*v^2-v^4)+v^2*z^2").expand()
    h41 = sympy.sympify("v^(-2)-1+v^2-z^2").expand()
    h51 = sympy.sympify("(3*v^4-2*v^6)+(4*v^4-v^6)*z^2+v^4*z^4").expand()


    set_of_knots = {k31, k41, k51}
    set_of_knots2 = {k61, k52}

    collection_knots = [{k31, k41}, {k51, k52, k61}]
    collection_knots2 = [{k31, k41}, {k61}]


    # save_collection("set_knots.txt", set_of_knots,comment="just a set of knots")
    # save_collection("set_knotss.txt", collection_knots,comment="just a set of knots")

    init_collection("set_init.txt", False)
    append_to_collection("set_init.txt", k31)
    append_to_collection("set_init.txt", k41)
    extend_collection("set_init.txt", {k51, k52})


    init_collection("set_init2.txt", True)
    append_to_collection("set_init2.txt", {k51, k52})
    append_to_collection("set_init2.txt", {k31, k41})
    extend_collection("set_init2.txt", collection_knots)

    inv1 = {j31: k31, j41: k41, j51: k51}
    inv2 = {j31: [k31, k41], j41: [k51], j51: [k52, k61]}
    inv3 = {(j31, h31): [k31, k41], (j41, h51): [k51], (j51, j31): [k52, k61]}
    inv4 = {k31: {"jones":j51, "homflypt":h41}, k41: {"jones":j31, "homflypt":h51}}

    save_collection_with_invariants("set_inv1.txt", inv1, invariant_names="Jones")
    print("___1___")

    save_collection_with_invariants("set_inv2.txt", inv2, invariant_names="Jones")
    print("___2___")

    save_collection_with_invariants("set_inv3.txt", inv3, invariant_names=["jones", "homflypt"])
    print("___3___")

    save_collection_with_invariants("set_inv4.txt", inv4)
    print("___4___")

    save_collection_with_invariants("set_inv4_j.txt", inv4, ["jones"])
    print("___5___")

    save_collection_with_invariants("set_inv4_jj.txt", inv4, "jones")
    exit()

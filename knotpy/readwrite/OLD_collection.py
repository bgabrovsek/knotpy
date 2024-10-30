""" Loading/saving a collection of diagrams"""

import collections.abc
import gzip
from collections import defaultdict
import sympy
import csv
import io
import sympy as sp
from pathlib import Path

from knotpy.notation.pd import to_pd_notation
from knotpy.notation.dispatcher import from_notation_dispatcher, to_notation_dispatcher
from knotpy.notation.em import to_condensed_em_notation
from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ["save_collection"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_open_file_data = dict()  # contain format and other data for open files that we are writing in

"""
Specifications:

1) save one knot to file
2) save a list of knots to file
3) save a list of knots with properties and invariants to file
4) save a list of knots sharing an invariant

"""


def _line_reader(filename, ignore_first_n_lines=0, max_lines=None, comment_indicator="#"):
    """Read lines, ignored empty lines, commented lines, etc.
    :param filename:
    :param ignore_first_n_lines:
    :param max_lines:
    :param comment_indicator:
    :return:
    """
    if max_lines == 0:
        return
    filename = str(filename)
    line_count = 0
    with (gzip.open(filename) if filename.endswith(".gz") else open(filename)) as file:
        for line in file:
            line = line.strip()
            if line and (comment_indicator is None or not line.startswith(comment_indicator)):
                line_count += 1
                if line_count > ignore_first_n_lines:
                    yield line
                    if max_lines is not None and line_count >= max_lines:
                        break


def count_lines(filename):
    # return how many non-empty non-commented lines are in filename
    return sum(1 for _ in _line_reader(filename))


"""
Load/save collection of diagrams (one diagram per line)
"""

def _chunkify_generator(original_generator, n):
    chunk = []
    for value in original_generator:
        chunk.append(value)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:  # yield the last chunk if it's not empty
        yield chunk


def load_invariants_iterator(filename, notation="CEM", ignore_first_n_lines=0, max_diagrams=None):
    """Iterate over a collection of diagram and invariants in a file. The file should contain one diagram per line.
    :param filename: input
    :param notation: default if "cem"
    :param ignore_first_n_lines:
    :param max_diagrams: maximal diagrams to load (iterate over with)
    :return: diagram
    """

    if max_diagrams == 0:
        return

    comment_indicator = "#"
    column_separator = ";"

    # function that converts from notation to PlanarDiagram
    notation_function = from_notation_dispatcher(notation) if notation else None

    header = None  # header is a list of strings
    name_row_index = 0  # in what row the diagram name is stored
    code_row_index = 1  # in what row the diagram notation is stored
    invariant_rows_indices = []  # in what rows invariants are stored

    count_yielded = 0  # count how many diagrams were yielded
    count_diagrams = 0  # count how many diagrams there are (some could be skipped)


    for row in csv.reader(_line_reader(filename)):

        # is there a header?
        if header is None and any("notation" in cell.lower() for cell in row):
            name_row_index, code_row_index = None, None  # reset the indices
            header = [cell.strip() for cell in row]
            header_lower = [cell.lower() for cell in header]
            if "name" in header_lower:
                name_row_index = header_lower.index("name")
            code_row_index = [i for i, cell in enumerate(header_lower) if "notation" in cell][0]
            # extract notation from header, e.g. for "PD notation", notation is "pd" (lower case)
            notation = header_lower[code_row_index][:header_lower[code_row_index].find(notation)].strip()
            # all other rows are invariants
            invariant_rows_indices = [i for i in range(len(header)) if i != name_row_index and i != code_row_index]
            continue

        count_diagrams += 1

        # should we skip the diagram?
        if count_diagrams <= ignore_first_n_lines:
            continue

        # load the diagram

        # we must have a notation function
        if notation_function is None:
            raise ValueError(f"Cannot convert a diagram without providing a notation ({notation} is provided)")

        code, name, invariants = None, None, []  # default values

        # extract name, code, invariants
        code = row[code_row_index] if code_row_index is not None else None
        name = row[name_row_index] if name_row_index is not None else None
        invariants = [row[i] for i in invariant_rows_indices]

        try:
            diagram = notation_function(code)
        except:
            raise ValueError(f"Invalid diagram notation {str(code)}.")

        if name is not None:
            diagram.name = name

        # convert invariants as a dictionary if invariant names are given
        if header is not None and all(header[i] for i in invariant_rows_indices):
            invariants = dict(zip([header[i] for i in invariant_rows_indices], invariants))

        yield diagram, invariants
        count_yielded += 1

        if count_yielded >= max_diagrams:
            break


def load_collection_iterator(filename, notation="CEM", max_diagrams=None):
    """Iterate over a collection of diagram in a file. The file should contain one diagram per line.
    :param filename: input
    :param notation: default if cem
    :param max_diagrams: maximal diagrams to load (iterate over with)
    :return: diagram
    """
    for diagram, invariants in load_invariants_iterator(filename, notation, max_diagrams=max_diagrams):
        yield diagram


def load_collection(filename, notation="CEM", max_diagrams=None):
    """Load a collection of diagrams from a file. One diagram per line.
    :param filename:
    :param notation:
    :param max_diagrams:
    :return:
    """
    # TODO: if saved in canonical, it does not load in caonnical ?!?
    return list(load_collection_iterator(filename, notation, max_diagrams=max_diagrams))




def append_to_collection(filename, iterable, notation="native"):
    """

    :param filename:
    :param iterable:
    :param notation:
    :param comment:
    :return:
    """
    column_separator = ": "
    # select conversion function
    conversion_function = to_notation_dispatcher(notation.strip().lower())

    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "at", encoding='utf-8') if filename.endswith(".gz") else open(filename, "at")

    if isinstance(iterable, PlanarDiagram) or isinstance(iterable, str):
        iterable = [iterable]

    for k in iterable:
        s = conversion_function(k) if not isinstance(k, str) else k
        file.write(str(k.name) if k.name is not None else "")
        file.write(column_separator)
        file.write(f"{s}\n")

    file.close()


"""
Load/save collection of diagrams with given invariants.
Can contain one diagram and list of computed invariants per line, or, 
can contain a list of diagrams
"""


def _force_diagrams_to_list(something):
    """Force diagrams or list of diagrams to be a list or tuple.

    :param something:
    :return:
    """
    if all(not isinstance(something, t) for t in (list, set, tuple, PlanarDiagram)):
        raise ValueError(f"Diagram list {something} of unknown format.")
    return something
    # if isinstance(something, list):
    #     return something
    # if isinstance(something, tuple) or isinstance(something, set):
    #     return list(something)
    # if isinstance(something, PlanarDiagram):
    #     return something
    # raise ValueError(f"Diagram list {something} of unknown format.")


def _force_invariants_to_dictionary(something, invariant_names=None):
    """Force invariants to be a dictionary {invariant name: invariant value}, they can be given as lists, etc.
    :param something: list/tuple, dictionary or value 
    :param invariant_names: list of names 
    :return: dictionary {invariant name: invariant value}
    """
    # if no invariants are given, return empty dictionary
    if not something and not invariant_names:
        return dict()

    if isinstance(something, list) or isinstance(something, tuple):
        if invariant_names is None:
            return ValueError("Invariant names must be given if invariants are given as a list or tuple")
        if len(something) != len(invariant_names):
            return ValueError("Number of invariants does not match number of invariant names")
        return dict(zip(invariant_names, something))

    if isinstance(something, dict):
        return something

    if not isinstance(invariant_names, list) or not isinstance(invariant_names, tuple):
        invariant_names = [invariant_names]

    # something is an invariant value (not a list/tuple)
    if len(invariant_names) == 1:
        return {invariant_names[0]: something}
    else:
        raise ValueError(f"Invariant names {invariant_names} should be an invariant name or list of invariant names ")

    #raise ValueError(f"Cannot detect {something} as a invariant value or list/tuple/dict of invariant values ")


def _pair_to_diagrams_and_invariants(a, b, invariant_names=None):
    """Parameters a and b can be either diagrams or invariants. Diagrams can be given as a list or PlanarDiagram,
    invariants can be given as a list or tuple.
    :param a: diagram(s) or invariants(s)
    :param b: diagram(s) or invariants(s)
    :param invariant_names: if invariants are in list form, invariant names must be given
    :return: list of diagrams, dictionary of invariants {invariant name: invariant value}
    """
    # make sure diagrams and invariants are not just values (not list/tuples)

    # a or b is a PlanarDiagram
    if isinstance(a, PlanarDiagram):
        return _force_diagrams_to_list(a), _force_invariants_to_dictionary(b, invariant_names)

    if isinstance(b, PlanarDiagram):
        return _force_diagrams_to_list(b), _force_invariants_to_dictionary(a, invariant_names)

    # a or b is a list/tuple/set of PlanarDiagrams
    if (isinstance(a, list) or isinstance(a, tuple) or isinstance(a, set)) and a:
        if isinstance(next(iter(a)), PlanarDiagram):
            return _force_diagrams_to_list(a), _force_invariants_to_dictionary(b, invariant_names)
        
    if (isinstance(b, list) or isinstance(b, tuple) or isinstance(b, set)) and b:
        if isinstance(next(iter(b)), PlanarDiagram):
            return _force_diagrams_to_list(b), _force_invariants_to_dictionary(a, invariant_names)

    raise ValueError(f"Could not extract diagram/invariant information from {a} and {b}")


def _diagram_invariant_data_iterator(data, invariant_names=None):
    """Iterate over data that contains diagrams and invariant values. Data may consist of:
    - a tuple/list of the form [(diagrams(s), list or dict of invariants), ...]
    - a dictionary {tuple of invariants or invariant: diagram(s)}
    - a dictionary {diagram: list or dict of invariants}
    """
    if isinstance(data, list) or isinstance(data, tuple) or isinstance(data, set):
        for item in data:
            if len(item) == 1:
                yield _pair_to_diagrams_and_invariants(item[0], [], invariant_names)
            if len(item) == 2:
                yield _pair_to_diagrams_and_invariants(item[0], item[1], invariant_names)
            if len(item) >= 3:
                yield _pair_to_diagrams_and_invariants(item[0], item[1:], invariant_names)

    if isinstance(data, dict):
        for a, b in data.items():
            yield _pair_to_diagrams_and_invariants(a, b, invariant_names)

    raise TypeError("Can only extract diagram and invariant if they are given as type list/tuple/set/dict.")



def _write_header(file, notation, invariant_names, comment):
    comment_indicator = "#"
    column_delimiter = ";"
    if comment:
        file.write(f"{comment_indicator} {comment}\n")

    csv_writer = csv.writer(file, delimiter=column_delimiter)
    csv_writer.writerow(["Name", f"{notation.strip()} notation", *invariant_names])


def save_invariant_collection(filename, data, notation="CEM", invariant_names=None, comment=None):
    """For each diagram or set of diagrams save its invariant values. Each row consist of name; notation(s); and invariants.
    :param filename:
    :param data: can consist of a list [diagram(s), invariants], dict {diagram(s): invariants},
    or dict {invariants: diagram(s)}, where diagrams and invariants are given as dicts or lists=tuples
    :param notation:
    :param invariant_names: in case invariants are given as tuples/lists, a list of invariants must be given
    :param comment:
    :return:
    """


    pass




def _diagrams_to_string(diagrams, notation_function, diagram_separator):
    """diagrams to string"""
    if isinstance(diagrams, PlanarDiagram):
        return notation_function(diagrams)
    else:
        return diagram_separator.join([notation_function(d) for d in diagrams])  # should we sort?




def _is_pds(data, can_be_pd=True):
    """Return True if data is a PlanarDiagram or a set/list/tuple of PlanarDiagrams"""
    if can_be_pd and isinstance(data, PlanarDiagram):
        return True
    if isinstance(data, (set, list, tuple)) and isinstance(next(iter(data)), PlanarDiagram):
        return True
    return False





def append_bunch_to_invariant_collection(file, data):
    """Append a multiple line of diagram(s) and optional invariants to a file.
     Options of the diagram structure:
     - a list/set of diagrams, {diagram1, diagram2, ...} if multiple_diagrams_per_line = False
     - a list/set of list/set of diagrams {{diagram1, diagram2,...}, {diagram3, diagram4,...}, ...} if multiple_diagrams_per_line = True
     - a dict where keys are an invariant: {value1: diagram(s), value2: diagram(s), ...}
     - a dict where keys are tuples of invariants: {values1: diagram(s), values2: diagram(s), ...}
     - a dict where keys are a diagram: {diagram1: invariant(s), diagram2: invariant(s), ...}
     - a dict where keys are tuples of diagrams: {tuple of diagrams1: invariants(s), tuple of diagrams1: diagram(s), ...}

    :param file: open file instance or filename
    :param data: list/tuple/set/dict
    :return:
    """
    if not data:
        return

    close_file_at_the_end = False
    # open the file
    if not isinstance(file, (io.IOBase, gzip.GzipFile)):
        file = gzip.open(file, "at", encoding='utf-8') if file.endswith(".gz") else open(file, "at")
        close_file_at_the_end = True

    # data is just a list and no invariants are given
    if _is_iter_pds(data):  # data is a list of diagrams or a list of list of diagrams if multiple diagrams per line allowed
        for item in data:
            append_to_invariant_collection(file, item)

    # data is a dict with invariants
    elif isinstance(data, dict):
        for key, value in data.items():
            if _is_pds(key):  # keys are diagrams or list of diagrams if multiple diagrams per line allowed
                append_to_invariant_collection(file, diagram=key, invariants=value)
            elif _is_pds(value):  # values are diagrams or list of diagrams if multiple diagrams per line allowed
                append_to_invariant_collection(file, diagram=value, invariants=key)
            else:
                file.close()
                raise ValueError("Keys or values of input must be diagram(s)")

    if close_file_at_the_end:
        file.close()


def append_to_collection(file, diagram):
    if _is_pds(diagram, can_be_pd=True):
        raise TypeError("Input must be a PlanarDiagram or set/list of PlanarDiagrams if multiple diagrams per line are allowed")
    append_to_invariant_collection(file, diagram)


def append_bunch_to_collection(file, data):
    if isinstance(data, PlanarDiagram):
        raise TypeError("Input must be a set/list of diagrams")
    if _is_iter_pds(data):
        append_bunch_to_invariant_collection(file, data)
    else:
        raise TypeError("Input must consist of list/set of Planar diagrams or list/set of list/set of diagrams if multiple diagrams per line are allowed")



def save_collection(filename, iterable, notation="CEM", comment=None):
    """Save diagrams in file. The data can be a list/tuple/set of diagrams or list/tuple/set of list/tuple/set diargams.
    In the first case, the head will be e.g. "Name, CEM notation.",
    in the second case, the head will be e.g. "CEM notations", where each notation is separated by "&",
    :param filename:
    :param data:
    :param notation:
    :param comment:
    :return:
    """

    column_separator = ": "

    # select conversion function
    conversion_function = to_notation_dispatcher(notation.strip().lower())

    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "wt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "wt")

    if comment:
        file.write(f"# {comment}\n")
    if hasattr(iterable, "__len__"):
        file.write(f"# {len(iterable)} diagrams in {notation} notation\n")

    if isinstance(iterable, PlanarDiagram) or isinstance(iterable, str):
        iterable = [iterable]

    # TODO: write header

    count = 0
    for k in iterable:
        s = conversion_function(k) if not isinstance(k, str) else k
        file.write(str(k.name) if k.name is not None else "")
        file.write(column_separator)
        file.write(f"{s}\n")
        count += 1

    file.close()
    print(f"Saved {count} dagrams to {filename}.")

    pass


def save_invariant_collection(filename, data, invariant_names, notation, comment=None):
    """
    :param filename:
    :param data:
    :param invariant_names:
    :param notation:
    :param comment:
    :return:
    """

    comment_indicator = "#"
    column_separator = "; "
    diagram_separator = " & "
    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "wt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "wt")

    # comments
    if comment:
        file.write(f"{comment_indicator} {comment}\n")
    file.write(f"{comment_indicator} {notation} notation\n")
    # header
    columns = (["Diagram"] + list(invariant_names)) if "diagram" != invariant_names[0].lower() else list(invariant_names)
    file.write(f"{column_separator.join(columns)}\n")

    notation_function = to_notation_dispatcher(notation)

    for diagrams, invariants in _data_iterator(data, invariant_names):

        # convert diagram to strings
        if isinstance(diagrams, PlanarDiagram):
            diagrams_string = notation_function(diagrams)
        else:
            if len(diagrams) != 1:
                diagrams_string = diagram_separator.join([notation_function(d) for d in diagrams])
            else:
                diagrams_string = notation_function(diagrams[0]) + diagram_separator

        # convert invariants/polynomials to string
        invariant_strings = [str(i) for i in invariants]

        # create row consisting of the diagram(s), followed by invariants
        row = [diagrams_string] + invariant_strings

        file.write(f"{column_separator.join(row)}\n")
    file.close()



def load_invariant_collection_header(filename):
    """Get the header of the diagram and invariant collection file. The header contains "Diagrams", followed by
    invariant names.
    :param filename:
    :return:

    # TODO: get notation from file header
    """

    comment_indicator = "#"
    column_separator = ";"
    #diagram_separator = "&"
    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "rt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "rt")

    header = None

    for line in file:
        line = line.strip()
        if not line or line.startswith(comment_indicator):
            continue
        file.close()
        return [q.strip() for q in line.split(column_separator)]




def load_invariant_collection_iterator(filename, notation):
    """

    :param filename:
    :param notation:
    :return:

    # TODO: get notation from file header
    """

    comment_indicator = "#"
    column_separator = ";"
    diagram_separator = "&"
    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "rt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "rt")

    notation_function = from_notation_dispatcher(notation) if notation else None  # should there be a default?

    header = None
    diagram_index = None

    for line in file:

        line = line.strip()

        if not line:
            continue

        if line.startswith(comment_indicator):
            continue

        row = [q.strip() for q in line.split(column_separator)]

        if header is None:
            header = row
            diagram_index = [q.lower() for q in header].index("diagram")
            continue

        # actually load data

        # convert invariants to polynomials

        invariants = row[:diagram_index] + row[diagram_index + 1:]
        invariants = tuple(sympy.sympify(i) for i in invariants)

        # convert codes to PlanarDiagram objects

        diagrams = row[diagram_index]

        if diagram_separator in diagrams:  # has more than one diagram in line
            diagrams = [q.strip() for q in diagrams.split(diagram_separator)]
            diagrams = [notation_function(q) for q in diagrams if q]
        else:
            diagrams = notation_function(diagrams)

        yield diagrams, invariants

    file.close()


def load_invariant_collection(filename, notation):
    print("Loading invariants...")
    return [
        q for q in load_invariant_collection_iterator(filename, notation)
    ]


def invariant_collection_group_sizes(filename, notation):
    #header = load_invariant_collection_header(filename)
    #number_of_groups = 0
    #number_of_diagrams = 0
    group_sizes = defaultdict(int)
    for d, i in load_invariant_collection_iterator(filename, notation):
        #number_of_groups += 1
        if isinstance(d, PlanarDiagram):
            #number_of_diagrams += 1
            group_sizes[1] += 1
        else:
            #number_of_groups += len(d)
            group_sizes[len(d)] += 1

    return group_sizes

if __name__ == "__main__":
    # testing
    import knotpy as kp
    import sympy
    k31 = kp.from_pd_notation("[[1,5,2,4],[3,1,4,6],[5,3,6,2]]", name="3_1")
    k41 = kp.from_pd_notation("[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]", name="4_1")
    k51 = kp.from_pd_notation("[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]", name="5_1")
    k52 = kp.from_pd_notation("[[1,5,2,4],[3,9,4,8],[5,1,6,10],[7,3,8,2],[9,7,10,6]]")
    k61 = kp.from_pd_notation("[[1,7,2,6],[3,10,4,11],[5,3,6,2],[7,1,8,12],[9,4,10,5],[11,9,12,8]]")

    j31 = sympy.sympify("t+ t^3-t^4")
    j41 = sympy.sympify("t^(-2)-t^(-1)+ 1-t+ t^2")
    j31 = sympy.sympify("t^2+ t^4-t^5+ t^6-t^7")

    h31 = sympy.sympify("(2*v^2-v^4)+v^2*z^2").expand()
    k41 = sympy.sympify("(v^(-2)-1+v^2)-z^2").expand
    k41 = sympy.sympify("(3*v^4-2*v^6)+(4*v^4-v^6)*z^2+v^4*z^4").expand()

    set_of_knots = {k31, k41, k51}
    collection_knots = [{k31, k41}, {k51, k52, k61}]

    save_collection("set_knots.txt", set_of_knots,comment="jsut a set of knots")
    save_invariant_collection("set_inv_1.txt", set_of_knots,comment="jsut a set of knots")

    exit()
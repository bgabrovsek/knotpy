""" Loading/saving a collection of diagrams"""

import collections.abc
import gzip
from collections import defaultdict
import sympy
import sympy as sp

from knotpy.notation.pd import to_pd_notation
from knotpy.notation.dispatcher import from_notation_dispatcher, to_notation_dispatcher
from knotpy.classes.planardiagram import PlanarDiagram

__all__ = ["save_collection", "load_collection", "save_invariant_collection", "load_invariant_collection",
           "append_to_collection", "count_lines", "load_collection_iterator", "load_invariant_collection_iterator",
           "append_invariant_collection", "load_invariant_collection_header", "invariant_collection_group_sizes"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


def count_lines(filename):
    if not isinstance(filename, str):
        filename = str(filename)
    f = gzip.open(filename) if filename.endswith(".gz") else open(filename)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization
    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    f.close()
    return lines

"""
Load/save collection of diagrams (one diagram per line)
"""


def load_collection_iterator(filename, notation=None, max_diagrams=None):
    """Iterate over a collection of diagram in a file. The file should contain one diagram per line.
    :param filename:
    :param notation:
    :param max_diagrams:
    :return:
    """
    notation_function = from_notation_dispatcher(notation) if notation else None  # should there be a default?
    comment_indicator = "#"
    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "rt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "r")
    count = 0

    for line in file:

        if max_diagrams is not None and max_diagrams <= count:
            break
        line = line.strip()

        if line.startswith(comment_indicator):
            # if there is a comment, then perhaps it contains the notation
            try:
                words = [word.strip().lower() for word in line.split(" ") if word]  # strip
                notation = words[words.index("notation") - 1]
                notation_function = from_notation_dispatcher(notation)
            except ValueError:
                pass
        elif len(line) > 0:

            # get the diagram string and convert it
            count += 1
            if notation_function is None:
                raise ValueError(f"Cannot convert a diagram without providing a notation ({notation} is provided)")
            diagram = notation_function(line)
            yield diagram

    file.close()


def load_collection(filename, notation=None, max_diagrams=None):
    """Load a collection of diagrams from a file. One diagram per line.
    :param filename:
    :param notation:
    :param max_diagrams:
    :return:
    """
    return list(load_collection_iterator(filename, notation, max_diagrams))


def save_collection(filename, iterable, notation="native", comment=None):
    """

    :param filename:
    :param iterable:
    :param notation:
    :param comment:
    :return:
    """

    # select conversion function
    conversion_function = to_notation_dispatcher(notation.strip().lower())

    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "wt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "wt")

    if comment:
        file.write(f"# {comment}\n")
    file.write(f"# {len(iterable)} diagrams in {notation} notation\n")

    if isinstance(iterable, PlanarDiagram) or isinstance(iterable, str):
        iterable = [iterable]

    for k in iterable:
        s = conversion_function(k) if not isinstance(k, str) else k
        file.write(f"{s}\n")

    file.close()


def append_to_collection(filename, iterable, notation="native"):
    """

    :param filename:
    :param iterable:
    :param notation:
    :param comment:
    :return:
    """

    # select conversion function
    conversion_function = to_notation_dispatcher(notation.strip().lower())

    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "at", encoding='utf-8') if filename.endswith(".gz") else open(filename, "at")

    if isinstance(iterable, PlanarDiagram) or isinstance(iterable, str):
        iterable = [iterable]

    for k in iterable:
        s = conversion_function(k) if not isinstance(k, str) else k
        file.write(f"{s}\n")

    file.close()


"""
Load/save collection of diagrams with given invariants.
Can contain one diagram and list of computed invariants per line, or, 
can contain a list of diagrams
"""


def _to_list(item):
    # convert to list
    if isinstance(item, list):
        return item
    elif isinstance(item, tuple):
        return item
    elif isinstance(item, dict):
        if invariant_names is None:
            raise ValueError("If invariants are given as a dict, invariant names should be provided")
        return [item[n] for n in invariant_names]
    elif isinstance(item, set):
        return list(item)
    else:
        return [item]

def _split_diagram_invariants(a, b, invariant_names=None):

    a_list = _to_list(a)
    b_list = _to_list(b)

    # yield diagrams, invariants
    if isinstance(a_list[0], PlanarDiagram):
        # return only planar diagram if not in a set-like object, invariant(s) in a list
        return (a_list[0] if isinstance(a, PlanarDiagram) else a_list), b_list
    else:
        return (b_list[0] if isinstance(b, PlanarDiagram) else b_list), a_list

def _data_iterator(data, invariant_names=None):
    """iterate over data, where data contains diagrams or invariants in various ways.
    The generator yields a tuple (diagram or a list of diagrams, list of invariants)

    The data values can consist of:
    - a tuple (diagram(s), invariant(s))
    - a tuple (invariants(s), diagram(s))
    - a dict {invariant(s): diagram(s)}
    - a dict {diagram: invariant(s)}
    """


    def pairs_generator(data):
        # data generator to pairs
        if isinstance(data, dict):
            for key, value in data.items():
                yield key, value
        else:
            for key, value in data:
                yield key, value


    # no data
    if not data:
        return

    for a, b in data.items() if isinstance(data, dict) else data:
        yield _split_diagram_invariants(a, b, invariant_names)


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


def append_invariant_collection(filename, diagrams, invariants, notation):
    """

    :param filename:
    :param diagrams:
    :param invariants:
    :param notation:
    :return:
    """

    #comment_indicator = "#"
    column_separator = "; "
    diagram_separator = " & "
    filename = str(filename)  # convert to string in case of Path object
    file = gzip.open(filename, "at", encoding='utf-8') if filename.endswith(".gz") else open(filename, "at")

    notation_function = to_notation_dispatcher(notation)

    invariant_strings = [str(i) for i in _to_list(invariants)]

    if isinstance(diagrams, PlanarDiagram):
        diagrams_string = notation_function(diagrams)
    else:
        if len(diagrams) != 1:
            diagrams_string = diagram_separator.join([notation_function(d) for d in diagrams])
        else:
            diagrams_string = notation_function(diagrams[0]) + diagram_separator

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

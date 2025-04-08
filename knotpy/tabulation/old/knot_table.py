"""
class for precomputed knots
"""
import sympy
import csv
import pathlib
import re

from knotpy.notation.em import from_condensed_em_notation
#from knotpy.tabulation.reader import _line_reader
from knotpy.tabulation.lazy_dict import LazyLoadDict, LazyDict

_knot_table_csv_filename = pathlib.Path(__file__).parent / "precomputed/knot_invariants_13.csv"
_link_table_csv_filename = pathlib.Path(__file__).parent / "precomputed/link_invariants_11.csv"


def _int(s: str):
    """Return int(str) if str contains an int and None otherwise"""
    return int(s) if s.isdigit() else None


_knot_invariants_eval_functions = {
    "Alexander": sympy.sympify,
    "Jones": sympy.sympify,
    "Conway": sympy.sympify,
    "Kauffman": sympy.sympify,
    "HOMFLYPT": sympy.sympify,
    "Unknotting number": _int,
}

_link_invariants_eval_functions = {
    "Alexander": sympy.sympify,
    "Jones": sympy.sympify,
    "Conway": sympy.sympify,
    "Kauffman": sympy.sympify,
    "HOMFLYPT": sympy.sympify,
    "Khovanov": sympy.sympify,
    "Components": _int,
    "Splitting number": _int,
    "Unlinking number": int,
}

def _from_name_diagram_pair(pair):
    """return the diagram from the pair = (name, diagram)"""
    diagram = from_condensed_em_notation(pair[1])
    diagram.name = pair[0]
    return diagram


def _parse_name(name):
    """Parse a knot/list name and return a tuple of extracted components.
    The function supports the following formats:
    - ``"n_i"``: Returns a tuple ``(n, i)``, where ``n`` and ``i`` are integers.
    - ``"nx_i"``: Returns a tuple ``(n, x, i)``, where ``n`` and ``i`` are integers, and ``x`` is either "a" or "n".
    - ``"Lnx_i{s}"``: Returns a tuple ``(n, x, i, s)``, where ``n`` and ``i`` are integers, ``x`` is either "a" or "n",
      and ``s`` is a list of integers extracted from within the curly braces.

    :param name: A string in the format ``"n_i"``, ``"nx_i"``, or ``"Lnx_i{s}"``.
    :type name: str
    :return: A tuple containing the parsed components based on the input format.
    :rtype: tuple
    :raises ValueError: If the input does not match any of the expected formats.

    # Examples:
    #     >>> parse_name("13_43")
    #     (13, 43)
    #     >>> parse_name("13n_14")
    #     (13, 'n', 14)
    #     >>> parse_name("13a_14")
    #     (13, 'a', 14)
    #     >>> parse_name("L8a16{1,0}")
    #     (8, 'a', 16, [1, 0])
    #     >>> parse_name("L19n7{2}")
    #     (19, 'n', 7, [2])

    """

    # Pattern for "n_i" format
    match_simple = re.match(r"^(\d+)_(\d+)$", name)
    if match_simple:
        n, i = match_simple.groups()
        return int(n), int(i)

    # Pattern for "mx_i" format
    match_with_x = re.match(r"^(\d+)([an])_(\d+)$", name)
    if match_with_x:
        n, x, i = match_with_x.groups()
        return int(n), x, int(i)

    # Pattern for "Lmx_i{s}" format
    match_with_L = re.match(r"^L(\d+)([an])(\d+)\{([\d,]*)\}$", name)
    if match_with_L:
        m, x, i, s = match_with_L.groups()
        s_list = tuple(map(int, s.split(','))) if s else tuple()
        return int(m), x, int(i), s_list

    # Raise an error if the format does not match
    raise ValueError("Invalid format")

# print(parse_name("13_43"))        # Output: (13, 43)
# print(parse_name("13n_14"))       # Output: (13, 'n', 14)
# print(parse_name("13a_14"))       # Output: (13, 'a', 14)
# print(parse_name("L8a16{1,0}"))   # Output: (8, 'a', 16, [1, 0])
# print(parse_name("L19n7{2}"))     # Output: (19, 'n', 7, [2])

def _crossings(s: str):
    """Return the number of crossings from the enumeration (3_1 -> 3)"""
    return _parse_name(s)[0]


def _load_lazy_precomputed_invariant_values(filename_csv, invariants_eval_functions):
    """ Loads data form the file _knot_table_csv in a lazy waz, so it initializes the data on-the-fly"""

    column_delimiter = ";"
    csv_reader = csv.reader(_line_reader(filename_csv), delimiter=column_delimiter)

    # we expect 1st row to be "Name" and the 2nd row to be "CEM notation", followed by invariant names
    header = next(csv_reader)
    if header[0] != "Name":
        raise ValueError(f"First row of {filename_csv} is not 'Name'.")
    if header[1] != "CEM notation":
        raise ValueError(f"First row of {filename_csv} is not 'CEM notation'.")

    result_invariants = dict()

    for row in csv_reader:
        # create the inner lazy dictionary for invariants
        led = LazyDict(eval_function=invariants_eval_functions)
        led.update(zip(header[2:], row[2:]))
        result_invariants[row[0]] = led  # set knot name to dict of lazy invariants

    return result_invariants


def _load_diagrams(filename_csv):
    """Separately load just the diagrams, since they are assigned to a different variable than the invariants
    :return:
    """

    column_delimiter = ";"
    csv_reader = csv.reader(_line_reader(filename_csv), delimiter=column_delimiter)

    # we expect 1st row to be "Name" and the 2nd row to be "CEM notation", followed by invariant names
    header = next(csv_reader)
    if header[0] != "Name":
        raise ValueError(f"First row of {filename_csv} is not 'Name'.")
    if header[1] != "CEM notation":
        raise ValueError(f"First row of {filename_csv} is not 'CEM notation'.")

    result_diagrams = dict() #LazyDict(eval_function=_from_name_diagram_pair)

    for row in csv_reader:
        result_diagrams[row[0]] = (row[0], row[1])  # contains name and CEM notation
    return result_diagrams


# global knot table and invariants
knot_table = LazyDict(eval_function=_from_name_diagram_pair,
                      load_function=lambda: _load_diagrams(_knot_table_csv_filename))

knot_invariants = LazyLoadDict(lambda: _load_lazy_precomputed_invariant_values(_knot_table_csv_filename,
                                                                               _knot_invariants_eval_functions))

# global link table and invariants
link_table = LazyDict(eval_function=_from_name_diagram_pair,

                      load_function=lambda: _load_diagrams(_link_table_csv_filename))
link_invariants = LazyLoadDict(lambda: _load_lazy_precomputed_invariant_values(_link_table_csv_filename,
                                                                               _link_invariants_eval_functions))


def filter_table(table_to_filter, crossings=None, min_crossings=None, max_crossings=None, invariant_value=None):
    """Get knot names that satisfy the condition
    :param table_to_filter:
    :param crossings:
    :param max_crossings:
    :return:
    """
    if table_to_filter is knot_table or table_to_filter is knot_invariants:
        table = knot_table
        invariants = knot_invariants
    elif table_to_filter is link_table:
        table = link_table
        invariants = link_invariants
    else:
        raise NotImplementedError("Can only filter knot, link table")

    if crossings is None:
        min_crossings = min_crossings or 0
        max_crossings = max_crossings or 100000000
    else:
        if min_crossings is not None or max_crossings is not None:
            raise ValueError("We can either select number of crossings or max number of crossings, not both")
        max_crossings = min_crossings = crossings

    knots = [name for name in sorted(table.keys(), key=lambda x: _parse_name(x))
             if min_crossings <= _crossings(name) <= max_crossings]

    if invariant_value is not None:
        knots = [name for name in knots
                 if all(invariants[name][invariant_name] == value for invariant_name, value in invariant_value.items())]

    return knots #{knot: table[knot] for knot in knots}  # TODO: implement with a table View



if __name__ == "__main__":
    # draw knot table


    print(filter_table(link_table, max_crossings=7))

    exit()

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
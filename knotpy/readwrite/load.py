import gzip
import csv
import io
from pathlib import Path
from itertools import chain

from knotpy.notation.dispatcher import from_notation_dispatcher
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.readwrite.save import _open_if_not_open

__all__ = ["load_collection", "load_collection_with_invariants",
           "load_headerless_collection", "load_headerless_collection_with_invariants",
           "load_collection_with_invariants_header",
           "load_collection_iterator",
           "load_collection_with_invariants_iterator",
           "load_collection_chunk_iterator", "load_collection_with_invariants_chunk_iterator",
           "count_lines"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

_open_read_file_data = dict()  # contain format and other data for open files that we are writing in
# keys are "notation", "multiple_diagrams_per_line", "invariant_names", "name_index", "notation_index", "invariant_indices"


def _line_reader(file, ignore_first_n_lines=0, max_lines=None):
    """Read lines, ignored empty lines, commented lines, etc.
    :param file:
    :param ignore_first_n_lines:
    :param max_lines:
    :return:
    """

    comment_indicator = "#"

    if max_lines == 0:
        return

    file, close_file_at_the_end = _open_if_not_open(file, "rt")
    line_count = 0
    for line in file:
        line = line.strip()
        if line and (comment_indicator is None or not line.startswith(comment_indicator)):
            line_count += 1
            if line_count > ignore_first_n_lines:
                yield line
                if max_lines is not None and line_count >= max_lines:
                    break

    if close_file_at_the_end:
        file.close()


def count_lines(filename):
    # return how many non-empty non-commented lines are in filename
    return sum(1 for _ in _line_reader(filename))


def load_collection_with_invariants_header(file):
    """Get the header of the diagram and invariant collection file. The header contains "Diagrams", followed by
    invariant names.
    :param file:
    :return:
    """

    global _open_read_file_data

    column_delimiter = ";"

    # open
    file, close_file_at_the_end = _open_if_not_open(file, "rt")

    header = None

    # read 1st line # TODO: make better, without for loop, maybe next()
    for row in csv.reader(_line_reader(file, max_lines=1), delimiter=column_delimiter):

        header = [cell.strip() for cell in row]
        header_lower = [cell.lower() for cell in header]

        # get indices of name and notation
        name_index = header_lower.index("name") if "name" in header_lower else None
        notation_index, notation_cell = next(((i, c) for i, c in enumerate(header_lower) if "notation" in c), None)

        if notation_index is None:
            raise ValueError(f"Cannot find csv header in {file.name}")

        # extract notation from header, e.g. for "PD notation", notation is "pd" (lower case)
        notation = notation_cell[:notation_cell.find("notation")].strip()
        multiple_diagrams_per_line = "notations" in notation_cell  # do we have one or more diagrams per line?

        # all other rows are invariants
        invariant_indices = [i for i in range(len(header)) if i != name_index and i != notation_index]
        invariant_names = [header[i] for i in invariant_indices]

        _open_read_file_data[file.name] = {
            "notation": notation,
            "multiple_diagrams_per_line": multiple_diagrams_per_line,
            "name_index": name_index,
            "notation_index": notation_index,
            "invariant_indices": invariant_indices,
            "invariant_names": invariant_names,
        }

    if close_file_at_the_end:
        file.close()

    return header


def load_collection_with_invariants_iterator(file, ignore_first_n_lines=0, max_diagrams=None, return_method=None):
    """Iterate over a collection of diagram and invariants in a file. The file should contain one diagram per line.
    :param file: input file object or filename
    :param ignore_first_n_lines:
    :param max_diagrams: maximal diagrams to load (iterate over with)
    :param return_method: can be "invariant dictionary" or "diagram dictionary"
    :return: diagram
    """

    global _open_read_file_data

    column_delimiter = ";"
    diagram_delimiter = " & "

    if max_diagrams == 0:
        return

    # open file
    file, close_file_at_the_end = _open_if_not_open(file, "rt")

    # check if header loaded and load header from global variable
    if file.name not in _open_read_file_data:
        load_collection_with_invariants_header(file)

    notation = _open_read_file_data[file.name]["notation"]
    multiple_diagrams_per_line = _open_read_file_data[file.name]["multiple_diagrams_per_line"]
    name_index = _open_read_file_data[file.name]["name_index"]
    notation_index = _open_read_file_data[file.name]["notation_index"]
    invariant_indices = _open_read_file_data[file.name]["invariant_indices"]
    invariant_names = _open_read_file_data[file.name]["invariant_names"]

    notation_function = from_notation_dispatcher(notation)

    count_yielded = 0  # count how many diagrams were yielded
    count_diagrams = 0  # count how many diagrams there are (some could be skipped)

    for row in csv.reader(_line_reader(file), delimiter=column_delimiter):

        count_diagrams += 1
        if count_diagrams <= ignore_first_n_lines:  # should we skip the diagram?
            #print("Count=", count_diagrams, "ignore", row)
            continue
        #else:
        #    print("Count=", count_diagrams, "not ignore", row)

        code = row[notation_index]
        name = row[name_index] if name_index is not None else None

        # load the diagrams

        if multiple_diagrams_per_line:
            diagram = []
            for sub_code in code.split(diagram_delimiter):
                try:
                    # extract name and code and convert
                    if ":" in sub_code:
                        sub_code_name = sub_code[:sub_code.find(":")].strip()
                        sub_code_code = sub_code[sub_code.find(":") + 1:].strip()
                    else:
                        sub_code_name = None
                        sub_code_code = sub_code.strip()
                    diagram.append(notation_function(sub_code_code))
                    diagram[-1].name = sub_code_name
                except:
                    raise ValueError(f"Invalid diagram notation {str(code)}.")
        else:
            # convert code to diagram
            try:
                diagram = notation_function(code)
            except:
                raise ValueError(f"Invalid diagram notation {str(code)}.")
            diagram.name = name

        invariant_values = [row[i] for i in invariant_indices]
        # TODO: should we simpyfy?

        # return method
        if return_method and "invariant dict" in return_method.lower():
            yield {tuple(invariant_values): diagram}

        elif return_method and "diagram dict" in return_method.lower():
            if multiple_diagrams_per_line:
                raise ValueError("Cannot return data as diagram dictionary if there are multiple diagrams per line")
            yield {diagram: tuple(invariant_values)}

        elif return_method is None:
            invariant_dict = dict(zip(invariant_names, invariant_values))
            yield diagram, invariant_dict

        else:
            raise ValueError(f"Unknown return method {return_method}")

        count_yielded += 1
        if max_diagrams is not None and count_yielded >= max_diagrams:
            break

    del _open_read_file_data[file.name]

    if close_file_at_the_end:
        file.close()


def load_collection_iterator(file, ignore_first_n_lines=0, max_diagrams=None):
    #print("ignore:", ignore_first_n_lines, "max", max_diagrams)
    for diagram, invariant_dict in load_collection_with_invariants_iterator(file, ignore_first_n_lines=ignore_first_n_lines, max_diagrams=max_diagrams):
        yield diagram

def load_collection_chunk_iterator(file, chunk_size, return_method=None):
    chunk = 0
    while True:
        result = [*load_collection_iterator(file, ignore_first_n_lines=chunk * chunk_size, max_diagrams=chunk_size)]
        chunk += 1
        if result:
            yield result
        else:
            break


def load_collection_with_invariants_chunk_iterator(file, chunk_size, return_method=None):
    chunk = 0
    while True:
        result = [*load_collection_with_invariants_iterator(file, ignore_first_n_lines=chunk * chunk_size, max_diagrams=chunk_size, return_method=return_method)]
        chunk += 1
        if result:
            yield result
        else:
            break


# TEST CHUNKS

# for x in load_collection_chunk_iterator("set_inv2.txt", chunk_size=3):
#     print("Len:", len(x))
#     for q in x:
#         print(*q)
    #print(x)

def load_collection_with_invariants(filename, return_method=None):
    """Return diagram and invariants stored in a file
    :param filename:
    :param return_method: can be "invariant dictionary" or "diagram dictionary"
    :return: list of pairs [diagram, invariants as a dictionary]
    """

    # return method
    if return_method and "invariant dict" in return_method.lower():
        return dict(chain.from_iterable(d.items() for d in load_collection_with_invariants_iterator(filename, return_method=return_method)))

    elif return_method and "diagram dict" in return_method.lower():
        return dict(chain.from_iterable(d.items() for d in load_collection_with_invariants_iterator(filename, return_method=return_method)))

    elif return_method is None:
        return [*load_collection_with_invariants_iterator(filename)]
    else:
        raise ValueError(f"Unknown return method {return_method}")


# for x in load_collection_with_invariants_chunk_iterator("set_inv2.txt", chunk_size=3):
#     print("Len:", len(x))
#     for q in x:
#         print(*q)
#
# exit()

def load_collection(filename):
    """Return diagram and invariants stored in a file
    :param filename:
    :return: list of pairs [diagram, invariants as a dictionary]
    """
    return [diag for diag, inv in load_collection_with_invariants_iterator(filename)]


def load_headerless_collection_with_invariants(filename, notation, name_index=None, diagram_index=None, invariant_names=None, delimiter=";"):
    """Load data in non-standard format.
    :param filename:
    :param notation:
    :param name_index:
    :param diagram_index:
    :param invariant_names:
    :param delimiter:
    :return:
    """
    raise NotImplementedError()


def load_headerless_collection(filename, notation):
    """Load data in non-standard format.
    :param filename:
    :param notation:
    :return:
    """

    notation_function = from_notation_dispatcher(notation)

    filename = str(filename)

    with gzip.open(filename, "rt", encoding='utf-8') if filename.endswith(".gz") else open(filename, "rt") as file:
        return [notation_function(line.strip()) for line in file]



if __name__ == "__main__":

    coll = ["set_init.txt", "set_init2.txt", "set_knots.txt", "set_knotss.txt"]
    coll = ["set_init.txt", "set_init2.txt", "set_knots.txt", "set_knotss.txt"]
    inv = ["set_inv1.txt", "set_inv2.txt", "set_inv3.txt", "set_inv4.txt", "set_inv4_j.txt", "set_inv4_jj.txt"]

    for f in   ["set_inv1.txt", "set_inv4_j.txt", "set_inv4_jj.txt", "set_inv4.txt"]:
        data = load_collection_with_invariants(f)
        for x, i in data:
            print(x)
            print(i)

    print()
    for f in   [ "set_inv2.txt", "set_inv3.txt", ]:
        print(f)
        data = load_collection_with_invariants(f)
        for x, i in data:
            print(*x)
            print(i)

    for f in  ["set_init.txt","set_knots.txt"]:
        print(f)
        data = load_collection(f)
        for x in data:
            print(x)

    for f in  ["set_init2.txt","set_knotss.txt"]:
        print(f)
        data = load_collection(f)
        for x in data:
            print(*x)

    print("..........")

    for f in   ["set_inv1.txt", "set_inv4_j.txt", "set_inv4_jj.txt", "set_inv4.txt"]:
        for x, i in load_collection_with_invariants_iterator(f):
            print(x)
            print(i)

    print()
    for f in   [ "set_inv2.txt", "set_inv3.txt", ]:
        print(f)

        for x, i in  load_collection_with_invariants_iterator(f):
            print(*x)
            print(i)

    for f in  ["set_init.txt","set_knots.txt"]:
        print(f)
        for x in load_collection_iterator(f):
            print(x)

    for f in  ["set_init2.txt","set_knotss.txt"]:
        print(f)
        for x in load_collection_iterator(f):
            print(*x)
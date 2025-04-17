from abc import ABC, abstractmethod
import gzip
import csv
from pathlib import Path

from knotpy.notation.dispatcher import to_notation_dispatcher


class InvariantTableWriter(ABC):
    """
    Abstract base class for file writers.

    - Handles file opening, closing, and resource management.
    - Supports writing format headers and optional comments.
    """

    def __init__(self, filename, name_is_key, invariant_fieldnames: list, notation="native", comment=None,):

        """
        Initializes the invariant writer.

        :param filename: Path to the output file.
        :param notation: The diagram notation ('dowker', 'gauss', etc.).
        :param comment: (Optional) A comment to add at the start of the file.
        """
        filename = Path(filename)
        self.name_is_key = name_is_key
        self.file = gzip.open(filename, mode="wt", newline='', encoding='utf-8') if filename.name.endswith(".gz") else open(filename, mode="wt", newline='',)
        self.notation_key = notation + " notation"  # diagram header
        self.to_notation = to_notation_dispatcher(notation.lower())  # function to convert diagram to notation

        # key of the dictionary can be either the name of the knot or the knot itself
        fieldnames = ["name", self.notation_key] if name_is_key else [self.notation_key]
        fieldnames.extend(list(invariant_fieldnames))

        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)  # the csv writer
        self.writer.writeheader()

        # Write optional comment
        if comment:
            for line in comment.strip().split("\n"):
                self.write_comment(line)

    def write_comment(self, comment):
        self.file.write(f"# {comment}\n")

    def close(self):
        """Closes the file."""
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def write_invariant(self, key, invariant_dictionary):

        # Is the key of the dictionary the diagram name (e.g. "3_1", "4_1") or the PlanarDiagram instance itself?
        if self.name_is_key:
            diagram = invariant_dictionary["diagram"]

            # Do not save the diagram name if keys are names.
            if diagram_is_named := ("name" in diagram.attr):
                save_diagram_name = diagram.attr["name"]
                #del diagram.attr["name"]  # do not delete it. this causes complications latter

            row = {
                "name": key,
                self.notation_key: self.to_notation(invariant_dictionary["diagram"])
            }

            if diagram_is_named:
                diagram.attr["name"] = save_diagram_name

            for inv in self.writer.fieldnames:
                if inv != "name" and inv != self.notation_key:
                    row[inv] = invariant_dictionary[inv]

            self.writer.writerow(row)
        else:
            row = {
                self.notation_key: self.to_notation(key)
            }
            for inv in self.writer.fieldnames:
                if inv != self.notation_key:
                    row[inv] = invariant_dictionary[inv]

            self.writer.writerow(row)


def save_invariant_table(filename, table, notation="native", comment=None):
    """
    Format of table can be either:
        {
        diagram1: {invariant1: value1, invariant2: value2},
        diagram2: {invariant1: value1, ...}
        }

    or
        {
        name1: {diagram:diagram1, invariant1: value1, invariant2: value2},
        name2: {diagram:diagram1, invariant1: value1, ...}
        }
    """
    if not table:
        return

    # are keys in the table knot names (e.g. "3_1", "4_2") or are they PlanarDiagram instances?
    name_is_key = isinstance(next(iter(table)), str)
    # get a list of invariant names
    invariant_fieldnames = list(next(iter(table.values())).keys())
    if name_is_key:
        invariant_fieldnames.remove("diagram")

    w = InvariantTableWriter(filename=filename, name_is_key=name_is_key, invariant_fieldnames=invariant_fieldnames, notation=notation, comment=comment)
    for key, value in table.items():
        w.write_invariant(key, value)

    w.close()
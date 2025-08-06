
import gzip
import csv
from pathlib import Path

from knotpy import unfreeze
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.attributes import clear_temporary_attributes
from knotpy.notation.dispatcher import to_notation_dispatcher


class InvariantTableWriter:
    """
    Abstract base class for file writers.

    - Handles file opening, closing, and resource management.
    - Supports writing format headers and optional comments.
    """

    def __init__(self, filename, notation="native", comment=None):
        """
        Args:
            filename:
            invariant_field_names:
            notation:
            comment:
        """


        filename = Path(filename)
        #self.name_is_key = name_is_key
        self.file = gzip.open(filename, mode="wt", newline='', encoding='utf-8') if filename.name.endswith(".gz") else open(filename, mode="wt", newline='',)
        self.notation_key = notation + " notation"  # diagram header
        self.to_notation = to_notation_dispatcher(notation.lower())  # function to convert diagram to notation
        self.field_names = None
        #
        # # key of the dictionary can be either the name of the knot or the knot itself
        # field_names = ["name", self.notation_key] if name_is_key else [self.notation_key]
        # field_names.extend(list(invariant_field_names))

        self.writer = csv.DictWriter(self.file, fieldnames=[])  # the csv writer

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

        # init the header
        if self.field_names is None:
            self.field_names = list(invariant_dictionary)
            if isinstance(key, int):
                key = str(key)
            if isinstance(key, str):
                # The primary key is a diagram (string) name.
                if "name" not in self.field_names:
                    self.field_names.append("name")

            elif isinstance(key, (PlanarDiagram, OrientedPlanarDiagram)):
                # The primary key is a planar diagram instance.
                if "diagram" not in self.field_names:
                    self.field_names.append("diagram")
            else:
                raise TypeError(f"Invalid key type ({type(key)}, should be string or (Oriented)PlanarDiagram")

            self.field_names = sorted(self.field_names, key=lambda k: (k != "name", k != "diagram"))

            # add notation instead of "diagram" in CSV header
            self.field_names = [s if s != "diagram" else self.notation_key for s in self.field_names]
            self.writer.fieldnames = self.field_names  # update CSV header
            self.writer.writeheader()

        row = invariant_dictionary.copy()

        # Write the line.
        if isinstance(key, int):
            key = str(key)

        if isinstance(key, str): # The primary key is a string name.
            # update the diagram
            if (k := row.get("diagram", None)) is not None:
                k = k.copy()
                k = unfreeze(k)
                clear_temporary_attributes(k)
                # the name is the key, no need to repeat it - not true, it is cumbersome to recover the name in lazy evaluation
                # if "name" in k.attr:
                #     del k.attr["name"]
                # update the diagram in the dictionary/row
                del row["diagram"]
                row[self.notation_key] = self.to_notation(k)

            row["name"] = key

        elif isinstance(key, PlanarDiagram): # The primary key is a planar diagram.
            k = key.copy()
            k = unfreeze(k)
            clear_temporary_attributes(k)
            # update the diagram in the dictionary/row
            if "diagram" in row:
                del row["diagram"]
            row[self.notation_key] = self.to_notation(k)
        else:
            raise TypeError(f"Invalid key type ({type(key)}, should be string or (Oriented)PlanarDiagram")

        self.writer.writerow(row)
        #
        #
        #
        # # Is the key of the dictionary the diagram name (e.g. "3_1", "4_1") or the PlanarDiagram instance itself?
        # if self.name_is_key:
        #     diagram = invariant_dictionary["diagram"]
        #
        #     # Do not save the diagram name if keys are names.
        #     if diagram_is_named := ("name" in diagram.attr):
        #         save_diagram_name = diagram.attr["name"]
        #         #del diagram.attr["name"]  # do not delete it. this causes complications latter
        #
        #     row = {
        #         "name": key,
        #         self.notation_key: self.to_notation(invariant_dictionary["diagram"])
        #     }
        #
        #     if diagram_is_named:
        #         diagram.attr["name"] = save_diagram_name
        #
        #     for inv in self.writer.fieldnames:
        #         if inv != "name" and inv != self.notation_key:
        #             row[inv] = invariant_dictionary[inv]
        #
        #     self.writer.writerow(row)
        # else:
        #     row = {
        #         self.notation_key: self.to_notation(key)
        #     }
        #     for inv in self.writer.fieldnames:
        #         if inv != self.notation_key:
        #             row[inv] = invariant_dictionary[inv]
        #
        #     self.writer.writerow(row)


def save_invariant_table(filename, table, notation="native", comment=None):
    """
    Save a table of knot/link invariants to a CSV file.

    Parameters:
        filename (str or Path):
            The output file path. The file will be saved in CSV or compressed CSV (.csv.gz) format.

        table (dict or list):
            The invariant data to save. Accepted formats include:

            1. Dictionary with diagrams as keys:
                {
                    diagram1: {invariant1: value1, invariant2: value2},
                    diagram2: {invariant1: value1, ...}
                }

            2. Dictionary with names as keys and diagrams included:
                {
                    name1: {"diagram": diagram1, invariant1: value1, invariant2: value2},
                    name2: {"diagram": diagram2, ...}
                }

            3. Dictionary with names as keys, no diagram field:
                {
                    name1: {invariant1: value1, invariant2: value2},
                    name2: {invariant1: value1, ...}
                }

            4. List of dicts with diagrams:
                [
                    {"diagram": diagram1, invariant1: value1, invariant2: value2},
                    ...
                ]

            5. List of dicts with names and diagrams:
                [
                    {"name": name1, "diagram": diagram1, invariant1: value1, ...},
                    ...
                ]

            6. List of dicts with names only:
                [
                    {"name": name1, invariant1: value1, invariant2: value2},
                    ...
                ]

        notation (str, optional):
            The diagram notation to use for serialization. Default is "native".

        comment (str, optional):
            A comment to include at the top of the file as a header.

    Returns:
        None

    Notes:
        This function writes the data to file. It does not return anything.

        TODO: if string, put ''
    """
    if not table:
        return

    if isinstance(table, dict):

        w = InvariantTableWriter(filename=filename, notation=notation, comment=comment)
        for key, inv_dict in table.items():
            w.write_invariant(key, inv_dict)
        w.close()

    elif isinstance(table, list | tuple):
        w = InvariantTableWriter(filename=filename, notation=notation, comment=comment)
        for row in table:
            if "name" in row:
                key = row["name"]
            elif "diagram" in row:
                key = row["diagram"]
            else:
                raise ValueError("The invariant list must contain dictionaries with either a 'name' or 'diagram' key.")
            w.write_invariant(key, row)
        w.close()
    else:
        raise TypeError(f"Invalid table type ({type(table)}, should be dict, list, or tuple")


    #
    #
    #
    # # are keys in the table knot names (e.g. "3_1", "4_2") or are they PlanarDiagram instances?
    #
    # # get a list of invariant names
    #
    # if isinstance(table, dict):
    #     name_is_key = isinstance(next(iter(table)), str)  # dictionary keys are strings (names)
    #     invariant_field_names = list(next(iter(table.values())).keys())
    # elif isinstance(table, list | tuple):
    #     name_is_key = "name" in [key.lower() for key in table[0]]
    #     invariant_field_names = list(table[0].keys())
    # else:
    #     raise TypeError(f"Invalid table type ({type(table)}, should be dict, list, or tuple")
    #
    # print("fields:", invariant_field_names, "(name is key)" if name_is_key else "(name is NOT key)")
    #
    # if name_is_key:
    #     invariant_field_names.remove("diagram")
    #
    # w = InvariantTableWriter(filename=filename, name_is_key=name_is_key, invariant_field_names=invariant_field_names, notation=notation, comment=comment)
    #
    #
    # if isinstance(table, dict):
    #     for key, inv_dict in table.items():
    #         w.write_invariant(key, inv_dict)
    # else:
    #     for inv_dict in table:
    #         w.write_invariant(inv_dict["name"] if name_is_key else inv_dict["diagram"], {k: v for k, v in inv_dict.items() if k.lower() != "name" and (k.lower() != "diagram" or not name_is_key)})
    #
    # w.close()
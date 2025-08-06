import csv
import gzip
from sympy import sympify
from pathlib import Path
from sympy.core.sympify import SympifyError

from knotpy.notation.dispatcher import from_notation_dispatcher
from knotpy.notation.native import from_knotpy_notation
from knotpy.classes.freezing import freeze

def _clean_csv_lines(file):
    for line in file:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue  # skip empty or commented-out lines
        # remove inline comments
        line_no_comment = line.split("#", 1)[0].rstrip()
        if line_no_comment:
            yield line_no_comment + "\n"  # re-add newline for csv reader


def _evaluate_value(field_name: str | None, unevaluated_value: str):
    """Evaluate the value 'unevaluated_value' as a planar diagram, a string, integer, or SymPy expression."""
    unevaluated_value = unevaluated_value.strip()
    # Do we have a diagram or an invariant value?
    if field_name is not None and "notation" in field_name:
        from_notation = from_notation_dispatcher(field_name.split(" ")[0])
        return freeze(from_notation(unevaluated_value))  # freeze the diagram
    else:
        # Figure out how to evaluate 'unevaluated_value'.
        # Case 1: Looks like a descriptive string (e.g. "chiral", "some label")
        if unevaluated_value.replace(" ", "").isalpha() and len(unevaluated_value) > 1:
            return unevaluated_value  # return as plain string, e.g. knot property "chiral"
        try:
            # Case 2: Try to interpret as integer
            return int(unevaluated_value)
        except ValueError:
            pass
        try:
            # Case 3: Parse as SymPy expression
            return sympify(unevaluated_value)
        except SympifyError:
            # Fall back to plain string
            return unevaluated_value


def _evaluate_dictionary(unevaluated_dict):
    return {
        "diagram" if "notation" in key else key:  _evaluate_value(key, value)
        for key, value in unevaluated_dict.items()
    }


def load_invariant_table(filename, evaluate: bool=True, only_field_name=None):
    """
    Loads an invariant table from a given file. The table is returned as a dictionary of dictionaries.
    If a field name is specified, the function returns a dictionary of values corresponding to that field.
    Handles both regular and gzipped files. The function supports "lazy non-evaluation" (keeps values as strings) when
    specified.

    Args:
        filename: The path to the file containing the invariant table.
        evaluate: Whether to enable lazy evaluation of the table contents. Default is False.
        only_field_name: The field name to extract specific values from the table. If None, parses the full table.

    Returns:
        dict: A dictionary containing the parsed invariant table. The structure depends on the presence of
              the `field_name` argument, the table content, and the `lazy` flag.

    Raises:
        ValueError: If the input file format is invalid, if the required 'notation' column is missing, or if
                    the given field name does not exist in the table.
    """
    filename = Path(filename)

    print(f"Loading {filename}")

    f = gzip.open(filename, "rt") if filename.name.endswith(".gz") else open(filename, "rt")
    reader = csv.DictReader(_clean_csv_lines(f))

    # If there is a field named 'name', then dictionary keys are knot/diagram names, otherwise they are PlanarDiagram instances.
    name_is_key = "name" in reader.fieldnames

    if only_field_name is not None and only_field_name not in reader.fieldnames:
        raise ValueError(f"Cannot find column '{only_field_name}'")

    # Get the "* notation" field in the header and replace it with "diagram".
    notation_column_name = next((field for field in reader.fieldnames if "notation" in field), None)

    if not name_is_key and notation_column_name is None:
        raise ValueError("The table does not contain a column named 'name' or a column containing the string 'notation'")

    result = {}

    # Load the dictionary.
    for row in reader:
        key = row.pop("name") if name_is_key else _evaluate_value(notation_column_name, row.pop(notation_column_name))

        # Values are only a singular field name or the whole dictionary?
        if only_field_name:
            result[key] = _evaluate_value(row[only_field_name]) if evaluate else only_field_name
        else:
            result[key] = _evaluate_dictionary(row) if evaluate else row

    f.close()

    return result


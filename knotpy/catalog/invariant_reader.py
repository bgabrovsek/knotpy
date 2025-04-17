import csv
import gzip
from functools import partial
import warnings
from sympy import sympify
from pathlib import Path

from knotpy.notation.dispatcher import from_notation_dispatcher
from knotpy.utils.dict_utils import LazyEvalDict, LazyLoadEvalDict

def _clean_csv_lines(file):
    for line in file:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue  # skip empty or commented-out lines
        # remove inline comments
        line_no_comment = line.split("#", 1)[0].rstrip()
        if line_no_comment:
            yield line_no_comment + "\n"  # re-add newline for csv reader

_keyword_evaluation_function = {
    "alexander": sympify,
    "jones": sympify,
    "conway": sympify,
    "homflypt": sympify,
    "homfly": sympify,
    "kauffman": sympify,
    "components": int,
    "splitting": int,
    "unknotting": int,
    "unlinking": int,
    "symmetry": str,
    "symmetry_group": str
}


def _lazy_invariant_value_eval(fieldname, unevaluated_value):

    fieldname = fieldname.lower()
    if fieldname in _keyword_evaluation_function:
        return _keyword_evaluation_function[fieldname](unevaluated_value)
    elif "notation" in fieldname:
        from_notation = from_notation_dispatcher(fieldname.split(" ")[0])
        return from_notation(unevaluated_value)
    else:
        warnings.warn(f"Unrecognized invariant: {fieldname}")

def _lazy_invariant_dict_eval(unevaluated_dict):
    return {
        "diagram" if "notation" in key else key:  _lazy_invariant_value_eval(key, value)
        for key, value in unevaluated_dict.items()
    }



def load_invariant_table(filename, lazy=False, field_name=None):
    """
    returns a dict of dicts, if fieldname is given, returns a dict of values
    """
    # TODO: add "lazy" flag
    # TODO: add option to partially read table up to some number of crossings
    filename = Path(filename)

    data = {}
    f = gzip.open(filename, "rt") if filename.name.endswith(".gz") else open(filename, "rt")
    reader = csv.DictReader(_clean_csv_lines(f))

    # If there is a "field" named "name", then dictionary keys are knot names, otherwise they are PlanarDiagram instances.
    name_is_key = "name" in reader.fieldnames

    # Get the index of "* notation" field in the header
    notation_index = [index for index, field in enumerate(reader.fieldnames) if " notation" in field][0]

    notation_column_header = reader.fieldnames[notation_index]
    if "notation" not in notation_column_header:
        raise ValueError("Invalid file format: Missing notation column header")
    notation = notation_column_header.split(" ")[0].strip().lower()
    from_notation = from_notation_dispatcher(notation)

    for row in reader:
        if name_is_key:
            key = row.pop("name")
            if field_name:
                if field_name not in row:
                    raise ValueError(f"Invalid fieldname: {field_name}")
                data[key] = row[field_name] if lazy else _lazy_invariant_value_eval(field_name, row[field_name])
            else:
                data[key] = row if lazy else _lazy_invariant_dict_eval(row)
        else:
            key = row.pop(notation_column_header)
            key = from_notation(key)
            data[key] = row if lazy else _lazy_invariant_dict_eval(row)

    f.close()

    return data


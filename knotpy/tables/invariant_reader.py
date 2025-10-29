"""
Utilities for loading knot/link invariant tables from CSV (optionally gzipped).

Features
--------
- Skips blank lines and comments (`# ...`), including inline comments.
- Accepts either a ``name`` column (names become keys) or a ``* notation`` column
  (the parsed diagram becomes the key).
- Optional evaluation of values:
  * Diagram fields (``* notation``) are parsed via the appropriate dispatcher and
    frozen for hashability.
  * Other fields: try int → SymPy expression → fall back to raw string.
- All SymPy imports are local to the functions that need them, so this module
  imports quickly when SymPy is not used.
"""

from __future__ import annotations

__all__ = ["load_invariant_table"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"

import csv
import gzip
from pathlib import Path
from typing import Any, Iterable
import sympy as sp

from knotpy.classes.planardiagram import Diagram
from knotpy.notation.dispatcher import from_notation_dispatcher
from knotpy.notation.native import from_knotpy_notation
from knotpy.classes.freezing import lock
from knotpy.invariants._symbols import SYMBOL_LOCALS


def _clean_csv_lines(file) -> Iterable[str]:
    """
    Yield CSV lines with comments and blank lines removed.

    - Entire comment lines (starting with '#') are skipped.
    - Inline comments after '#' are stripped.
    - Trailing newlines are normalized so :class:`csv.DictReader` can consume them.
    """
    for line in file:
        # strip potential BOM only on the first chunk
        if line.startswith("\ufeff"):
            line = line.lstrip("\ufeff")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        line_no_comment = line.split("#", 1)[0].rstrip()
        if line_no_comment:
            yield line_no_comment + "\n"


def _eval_diagram_symmetry_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing a native diagram string and a symmetry descriptor."""
    return {
        "diagram": lock(from_knotpy_notation(uneval_dict["native notation"])),
        "symmetry": uneval_dict["symmetry"],
    }


def _eval_diagram_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing only a native diagram string."""
    return {"diagram": lock(from_knotpy_notation(uneval_dict["native notation"]))}

def _eval_diagram(uneval_diagram: str) -> Diagram:
    """Evaluate a row containing only a native diagram string."""
    return lock(from_knotpy_notation(uneval_diagram))

def _eval_poly(uneval_poly: str) -> sp.Expr:
    """Evaluate a row containing only a SymPy polynomial string."""
    return sp.sympify(uneval_poly, locals=SYMBOL_LOCALS)

def _eval_homflypt_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing a HOMFLYPT polynomial."""
    return {"homflypt": sp.sympify(uneval_dict["homflypt"], locals=SYMBOL_LOCALS)}


def _eval_kauffman_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing a Kauffman polynomial."""
    return {"kauffman": sp.sympify(uneval_dict["kauffman"], locals=SYMBOL_LOCALS)}


def _eval_yamada_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing a Yamada polynomial."""
    return {"yamada": sp.sympify(uneval_dict["yamada"], locals=SYMBOL_LOCALS)}


def _eval_multivariable_alexander_dict(uneval_dict: dict) -> dict:
    """Evaluate a row containing a multivariable Alexander polynomial."""
    return {
        "multivariable alexander": sp.sympify(
            uneval_dict["multivariable alexander"], locals=SYMBOL_LOCALS
        )
    }


# def _eval_components_dict(uneval_dict: dict) -> dict:
#     """Evaluate a row containing a symbolic or numeric component count."""
#     from sympy import sympify  # local import for fast module load
#     return {"components": sympify(uneval_dict["components"], locals=SYMBOL_LOCALS)}

# def _eval_components_int(uneval) -> dict:
#     """Evaluate a row containing a symbolic or numeric component count."""
#     return int(uneval)

def _evaluate_value(field_name: str | None, unevaluated_value: str) -> Any:
    """
    Evaluate a single CSV cell into a Python object.

    Behavior:
      - If ``field_name`` contains ``"notation"``, parse a diagram using the detected notation
        and freeze it for hashability.
      - Otherwise:
          * if the value is purely alphabetic words (e.g. ``"chiral"``), return the raw string,
          * else try ``int``,
          * else try to parse as a SymPy expression,
          * else fall back to the original string.
    """

    # print("VAL", field_name, "->", unevaluated_value)

    unevaluated_value = unevaluated_value.strip()

    # Diagram fields: e.g. "native notation", "dowker notation", "gauss notation", ...
    if field_name is not None and "notation" in field_name.lower():
        from_notation = from_notation_dispatcher(field_name.split()[0].lower())
        return lock(from_notation(unevaluated_value))

    if unevaluated_value.lower() == "none":
        return None

    # Otherwise, invariant / property value
    if unevaluated_value.replace(" ", "").isalpha() and len(unevaluated_value) > 1:
        return unevaluated_value  # plain descriptor like "chiral"


    if "_" in unevaluated_value:
        return unevaluated_value

    if unevaluated_value.lstrip("-").isdigit():
        return int(unevaluated_value)

    try:
        return sp.sympify(unevaluated_value)
    except Exception:
        # Fall back to plain string (covers SympifyError and others)
        return unevaluated_value


def _evaluate_dictionary(unevaluated_dict: dict[str, str]) -> dict[str, Any]:
    """
    Evaluate a CSV row dict, converting any ``* notation`` column to key ``'diagram'``
    and parsing other fields via :func:`_evaluate_value`.
    """

    #print("EVAL", unevaluated_dict)

    return {
        ("diagram" if "notation" in key else key): _evaluate_value(key, value)
        for key, value in unevaluated_dict.items()
    }


def load_invariant_table(
    filename: str | Path,
    evaluate: bool = True,
    only_field_name: str | None = None,
) -> dict[Any, Any]:
    """
    Load an invariant table from CSV (optionally gzipped) into a dictionary.

    The table must include either:
      - a ``name`` column (keys are names), or
      - a column whose header contains ``"notation"`` (keys are parsed diagrams).

    Line handling:
      - Lines beginning with ``#`` are ignored.
      - Inline comments after ``#`` are stripped.
      - Blank lines are skipped.

    Evaluation:
      - If ``evaluate=True`` (default), diagram/notational fields are parsed into frozen diagrams,
        numeric fields are parsed into integers where possible, and other values are parsed
        using SymPy (with a plain-string fallback).
      - If ``evaluate=False``, raw strings are returned unchanged.

    Args:
        filename: Path to the CSV or ``.gz`` file.
        evaluate: Whether to evaluate/parse cell values (True) or keep raw strings (False).
        only_field_name: If provided, return a dict keyed by name/diagram mapping to the value
            from this single column.

    Returns:
        A dictionary mapping keys (names or diagrams) to either:
          - a single value (when ``only_field_name`` is provided), or
          - a dictionary of evaluated fields for each row.

    Raises:
        ValueError: If the header contains neither ``name`` nor any ``* notation`` column,
                    or if ``only_field_name`` is not present in the header.
    """
    filename = Path(filename)

    # choose opener based on extension
    opener = gzip.open if filename.name.endswith(".gz") else open


    with opener(filename, "rt", encoding="utf-8") as f:

        reader = csv.DictReader(_clean_csv_lines(f))

        # Fail fast if no header row is present
        if not reader.fieldnames:
            return {}  # or raise ValueError("Empty or invalid CSV")

        # If there is a 'name' field, dictionary keys are names; else they are (parsed) diagrams.
        name_is_key = "name" in reader.fieldnames if reader.fieldnames else False

        if only_field_name is not None and (not reader.fieldnames or only_field_name not in reader.fieldnames):
            raise ValueError(f"Cannot find column '{only_field_name}'")

        # Find the first header containing 'notation'
        notation_column_name = next((field for field in (reader.fieldnames or []) if "notation" in field), None)

        if not name_is_key and notation_column_name is None:
            raise ValueError(
                "The table does not contain a column named 'name' or a column containing the string 'notation'"
            )

        result: dict[Any, Any] = {}

        # Load rows
        for row in reader:

            #print("ROW", row)

            key = row.pop("name") if name_is_key else _evaluate_value(
                notation_column_name, row.pop(notation_column_name)  # type: ignore[arg-type]
            )

            # Single field or full row?
            if only_field_name:
                result[key] = (
                    _evaluate_value(only_field_name, row[only_field_name]) if evaluate else row[only_field_name]
                )
            else:
                result[key] = _evaluate_dictionary(row) if evaluate else row

    return result
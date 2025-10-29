import gzip
import csv
from pathlib import Path

from knotpy import unfreeze
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.attributes import clear_temporary_attributes
from knotpy.notation.dispatcher import to_notation_dispatcher


class InvariantTableWriter:
    """
    Writer for invariant tables (CSV or gzipped CSV).

    - Opens and closes the output file (plain or .gz).
    - Lazily initializes the CSV header from the first row written.
    - Converts diagrams to the requested notation when writing.
    """

    def __init__(self, file_obj, notation: str = "native", comment: str | None = None) -> None:
        """
        Args:
            file_obj: An already-open text file object.
            notation: Diagram notation for serialization (e.g. ``"native"``).
            comment: Optional multi-line string to be prefixed as ``# ...`` lines.
        """
        self.file = file_obj
        self.notation_key = notation + " notation"
        self.to_notation = to_notation_dispatcher(notation.lower())
        self.field_names: list[str] | None = None
        self.writer = csv.DictWriter(self.file, fieldnames=[])

        if comment:
            for line in comment.strip().split("\n"):
                self.write_comment(line)

    def write_comment(self, comment: str) -> None:
        self.file.write(f"# {comment}\n")

    def write_invariant(
        self,
        key: str | int | PlanarDiagram | OrientedPlanarDiagram,
        invariant_dictionary: dict,
    ) -> None:
        if self.field_names is None:
            self.field_names = list(invariant_dictionary)
            if isinstance(key, int):
                key = str(key)
            if isinstance(key, str):
                if "name" not in self.field_names:
                    self.field_names.append("name")
            elif isinstance(key, (PlanarDiagram, OrientedPlanarDiagram)):
                if "diagram" not in self.field_names:
                    self.field_names.append("diagram")
            else:
                raise TypeError(
                    f"Invalid key type ({type(key)}); expected str or (Oriented)PlanarDiagram"
                )

            self.field_names = sorted(self.field_names, key=lambda k: (k != "name", k != "diagram"))
            self.field_names = [s if s != "diagram" else self.notation_key for s in self.field_names]
            self.writer.fieldnames = self.field_names
            self.writer.writeheader()

        row = invariant_dictionary.copy()

        if isinstance(key, int):
            key = str(key)

        if isinstance(key, str):
            if (k := row.get("diagram", None)) is not None:
                k = unfreeze(k.copy())
                clear_temporary_attributes(k)
                del row["diagram"]
                row[self.notation_key] = self.to_notation(k)
            row["name"] = key

        elif isinstance(key, PlanarDiagram):
            k = unfreeze(key.copy())
            clear_temporary_attributes(k)
            if "diagram" in row:
                del row["diagram"]
            row[self.notation_key] = self.to_notation(k)

        else:
            raise TypeError(
                f"Invalid key type ({type(key)}); expected str or (Oriented)PlanarDiagram"
            )

        self.writer.writerow({k: (v if v is not None else "None") for k, v in row.items()})


def save_invariant_table(
    filename: str | Path,
    table: dict | list | tuple,
    notation: str = "native",
    comment: str | None = None,
) -> None:
    """
    Save a table of knot/link invariants to CSV (optionally gzipped).
    Supports dict, list, or tuple in documented shapes.
    """
    if not table:
        return

    filename = Path(filename)
    opener = gzip.open if filename.name.endswith(".gz") else open

    # Context manager for file open/close
    with opener(filename, mode="wt", newline="", encoding="utf-8") as f:
        writer = InvariantTableWriter(file_obj=f, notation=notation, comment=comment)

        if isinstance(table, dict):
            for key, inv_dict in table.items():
                writer.write_invariant(key, inv_dict)

        elif isinstance(table, (list, tuple)):
            for row in table:
                if "name" in row:
                    key = row["name"]
                elif "diagram" in row:
                    key = row["diagram"]
                else:
                    raise ValueError(
                        "The invariant list must contain dictionaries with either a 'name' or 'diagram' key."
                    )
                writer.write_invariant(key, row)

        else:
            raise TypeError(f"Invalid table type ({type(table)}); should be dict, list, or tuple")
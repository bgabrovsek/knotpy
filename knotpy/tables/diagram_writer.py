"""
Module for writing planar diagram(s) data to files in various notations and formats.
"""

from __future__ import annotations

from abc import ABC
import gzip
from pathlib import Path
from typing import Iterable, Sequence, Union

from knotpy.notation.dispatcher import to_notation_dispatcher

__all__ = ["DiagramWriter", "save_diagrams", "DiagramSetWriter", "save_diagram_sets"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"


PathLike = Union[str, Path]


class _BaseDiagramWriter(ABC):
    """
    Abstract base class for diagram file writers.

    Responsibilities:
    - Open/close the output file (optionally gzipped).
    - Write the notation header and optional comments.
    - Provide a conversion function for the chosen notation.
    """

    def __init__(self, filename: PathLike, notation: str = "native", comment: str | None = None) -> None:
        """
        Initialize the writer.

        Args:
            filename: Path to the output file. If it ends with ``.gz``, the file
                is written in gzip text mode.
            notation: Target diagram notation (e.g., ``"native"``, ``"dowker"``, ``"gauss"``).
            comment: Optional multi-line string to be written as ``#``-prefixed
                comment lines at the start of the file.
        """
        filename = Path(filename)
        self.filename: Path = filename

        # Open file (gzipped if ".gz")
        self.file = (
            gzip.open(self.filename, "wt", encoding="utf-8")
            if filename.name.endswith(".gz")
            else open(self.filename, "wt", encoding="utf-8")
        )

        # Write notation header
        self.file.write(f"{notation} notation\n")

        # Write optional comments (line-by-line, prefixed with #)
        if comment:
            for line in comment.strip().split("\n"):
                self.write_comment(line)

        if notation:
            self.to_notation = to_notation_dispatcher(notation.lower())
        else:
            raise ValueError("Output format (diagram notation) must be provided")

    def write_comment(self, comment: str) -> None:
        """Write a single comment line (prefixed with ``# ``)."""
        self.file.write(f"# {comment}\n")

    def close(self) -> None:
        """Close the underlying file handle."""
        self.file.close()

    # Context manager protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class DiagramWriter(_BaseDiagramWriter):
    """
    Writer for single diagrams—one diagram per line.

    Uses the chosen notation to convert each diagram to a string representation
    and writes it to the file, separated by newlines.
    """

    def write_diagram(self, diagram) -> None:
        """
        Convert and write a single diagram.

        Args:
            diagram: A diagram object compatible with the chosen notation dispatcher.
        """
        self.file.write(self.to_notation(diagram) + "\n")

    def write_diagrams(self, diagrams: Iterable) -> None:
        """
        Convert and write multiple diagrams, one per line.

        Args:
            diagrams: Iterable of diagram objects.
        """
        for diagram in diagrams:
            self.write_diagram(diagram)


class DiagramSetWriter(_BaseDiagramWriter):
    """
    Writer for *sets* (or lists) of diagrams—one set per line.

    Each set is written on a single line, joining member diagrams with ``" & "``.
    """

    def write_diagram_set(self, diagram_set: Sequence) -> None:
        """
        Convert and write a single set of diagrams on one line.

        Args:
            diagram_set: Sequence (or set/list) of diagrams.
        """
        line = " & ".join(self.to_notation(diagram) for diagram in diagram_set)
        self.file.write(line + "\n")


def save_diagrams(filename: PathLike, diagrams: Iterable, notation: str = "native", comment: str | None = None) -> None:
    """
    Write multiple diagrams to a file (one per line).

    Args:
        filename: Path to the output file. If it ends with ``.gz``, the file is gzipped.
        diagrams: Iterable of diagram objects to write.
        notation: Target diagram notation (e.g., ``"native"``, ``"dowker"``, ``"gauss"``).
        comment: Optional multi-line comment written at the top of the file.
    """
    if not diagrams:
        return

    with DiagramWriter(filename=filename, notation=notation, comment=comment) as writer:
        for diagram in diagrams:
            writer.write_diagram(diagram)


def save_diagram_sets(filename: PathLike, diagram_sets: Iterable[Sequence], notation: str = "native", comment: str | None = None) -> None:
    """
    Write multiple sets of diagrams to a file (one set per line).

    Each set is joined with ``" & "`` on its line.

    Args:
        filename: Path to the output file. If it ends with ``.gz``, the file is gzipped.
        diagram_sets: Iterable of sequences (or sets/lists) of diagrams.
        notation: Target diagram notation (e.g., ``"native"``, ``"dowker"``, ``"gauss"``).
        comment: Optional multi-line comment written at the top of the file.
    """
    with DiagramSetWriter(filename=filename, notation=notation, comment=comment) as writer:
        for diagrams in diagram_sets:
            writer.write_diagram_set(diagrams)
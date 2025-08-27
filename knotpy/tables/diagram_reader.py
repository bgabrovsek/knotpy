"""
Module for reading, parsing, and handling planar diagram(s) data from various file formats.
"""

from __future__ import annotations

import gzip
import mmap
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Iterable, Iterator, List, Optional

from knotpy.notation.dispatcher import from_notation_dispatcher

__all__ = [
    "DiagramReader",
    "diagram_reader",
    "load_diagrams",
    "count_lines",
    "DiagramSetReader",
    "diagram_set_reader",
    "load_diagram_sets",
]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"


class _BaseDiagramReader(ABC):
    """
    Abstract base class for file readers.

    - Handles file opening, closing, and resource management.
    - Detects/uses the notation header on the first line, unless overridden.
    """

    def __init__(self, filename: str | Path, notation: Optional[str] = None) -> None:
        """
        Initialize the reader. If ``notation`` is provided, it overrides the file header.

        Args:
            filename: Path to the diagram file.
            notation: Optional notation (e.g. ``"dowker"``, ``"gauss"``, ``"native"``).
        """
        filename = Path(filename)
        self.filename: Path = filename
        # Open text file (gzipped if ".gz")
        self._file = (
            gzip.open(self.filename, "rt", encoding="utf-8")
            if filename.name.endswith(".gz")
            else open(self.filename, "rt")
        )
        self.from_notation = None

        if notation:
            self.from_notation = from_notation_dispatcher(notation.lower())
        else:
            self._initialize_format()  # Read from header if not provided

    def _initialize_format(self) -> None:
        """Read the first line to determine the diagram notation from the header."""
        first_line = self._file.readline().strip()
        if not first_line.endswith("notation"):
            raise ValueError("Missing notation header")

        notation = first_line.split(" ")[0].lower()
        self.from_notation = from_notation_dispatcher(notation.lower())

    @abstractmethod
    def _parse_line(self, line: str):
        """Parse a single content line according to the detected/selected notation."""
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """
        Iterate lazily over parsed lines.

        Skips the header if present and ignores empty/comment lines.
        """
        if self.from_notation is None:
            raise RuntimeError("Diagram format could not be determined.")

        first_line = True
        while True:
            line = self._file.readline()
            if not line:
                break  # EOF

            if first_line and self.from_notation is not None:
                first_line = False
                if line.strip().endswith("notation"):
                    continue  # skip header line

            parsed_line = self._parse_line(line)
            if parsed_line is not None:
                yield parsed_line  # yield only valid parsed lines

    def close(self) -> None:
        """Close the underlying file handle."""
        self._file.close()

    # Context manager protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class DiagramReader(_BaseDiagramReader):
    """Reader that returns parsed diagrams (one per non-empty, non-comment line)."""

    def _parse_line(self, line: str):
        # Strip trailing comments and whitespace
        line = line.split("#", 1)[0].strip()
        if not line:
            return None
        return self.from_notation(line)


class LazyDiagramReader(_BaseDiagramReader):
    """Reader that returns raw (unparsed) diagram strings."""

    def _parse_line(self, line: str) -> Optional[str]:
        line = line.split("#", 1)[0].strip()
        if not line:
            return None
        return line


class DiagramSetReader(_BaseDiagramReader):
    """Reader that returns a list of parsed diagrams per line, split by ``" & "``."""

    def _parse_line(self, line: str):
        line = line.split("#", 1)[0].strip()
        if not line:
            return None
        return [self.from_notation(row.strip()) for row in line.split(" & ")]


class LazyDiagramSetReader(_BaseDiagramReader):
    """Reader that returns a list of raw (unparsed) diagram strings per line."""

    def _parse_line(self, line: str):
        line = line.split("#", 1)[0].strip()
        if not line:
            return None
        return [row.strip() for row in line.split(" & ")]


def diagram_reader(filename: str | Path, notation: Optional[str] = None):
    """
    Simplified iterator interface for reading single-diagram files.

    Args:
        filename: Path to the file.
        notation: Optional notation (e.g. ``"dowker"``, ``"gauss"``). If ``None``,
            it is read from the file header.

    Yields:
        Parsed diagram objects.
    """
    with DiagramReader(filename, notation) as reader:
        yield from reader


def diagram_set_reader(filename: str | Path, notation: Optional[str] = None):
    """
    Simplified iterator interface for reading diagram-set files (one set per line).

    Args:
        filename: Path to the file.
        notation: Optional notation (e.g. ``"dowker"``, ``"gauss"``). If ``None``,
            it is read from the file header.

    Yields:
        Lists of parsed diagram objects.
    """
    with DiagramSetReader(filename, notation) as reader:
        yield from reader


def load_diagrams(filename: str | Path, notation: Optional[str] = None) -> List:
    """
    Load all diagrams from a file at once (eager).

    Args:
        filename: Path to the file containing diagram data.
        notation: Optional notation (e.g. ``"dowker"``, ``"gauss"``). If ``None``,
            it is detected from the file header.

    Returns:
        A list of parsed diagram objects.
    """
    with DiagramReader(filename, notation) as reader:
        return list(reader)


def load_diagrams_as_dict(filename: str | Path, notation: Optional[str] = None, lazy: bool = False) -> dict:
    """
    Load all diagrams from a file into a dictionary keyed by name.

    If ``lazy=True``, values are raw strings and names are extracted from the
    string via a simple regex (``['name'='...']``). If ``lazy=False``, values
    are parsed diagram objects and keys are taken from ``diagram.name``.

    Args:
        filename: Path to the file containing diagram data.
        notation: Optional notation (ignored if ``lazy=True``). If ``None``, it
            is detected from the file header.
        lazy: If ``True``, return raw strings; otherwise return parsed diagrams.

    Returns:
        A dictionary mapping names to either raw strings or diagram objects.

    Raises:
        ValueError: If both ``notation`` is provided and ``lazy=True``.
    """

    def _name_from_str(s: str) -> Optional[str]:
        # Extract name from a trailing attribute like "['name'='...']"
        if match := re.search(r"\['name'='([^']+)'\]", s):
            return match.group(1)
        return None

    if notation is not None and lazy:
        raise ValueError("Cannot specify notation and lazy=True at the same time")

    if lazy:
        with LazyDiagramReader(filename) as reader:
            return {_name_from_str(diagram): diagram for diagram in reader}
    else:
        with DiagramReader(filename, notation) as reader:
            return {diagram.name: diagram for diagram in reader}


def load_diagram_sets(filename: str | Path, notation: Optional[str] = None) -> List[list]:
    """
    Load all diagram sets from a file at once (eager).

    Args:
        filename: Path to the file containing diagram sets.
        notation: Optional notation (e.g. ``"dowker"``, ``"gauss"``). If ``None``,
            it is detected from the file header.

    Returns:
        A list of diagram sets, where each set is a list of parsed diagrams.
    """
    with DiagramSetReader(filename, notation) as reader:
        return list(reader)


def count_lines(filename: str | Path) -> int:
    """
    Count the number of non-empty, non-comment lines in a text file efficiently.

    Notes:
        Uses ``mmap`` for speed on large files. A line is counted if, after
        stripping whitespace, it is non-empty and does not begin with ``#``.

    Args:
        filename: Path to the text file.

    Returns:
        The number of relevant lines.
    """
    with open(filename, "r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            return sum(
                1
                for line in iter(mm.readline, b"")
                if (stripped := line.strip()) and not stripped.startswith(b"#")
            )


if __name__ == "__main__":
    pass
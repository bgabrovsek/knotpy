import mmap
import gzip
from pathlib import Path
import re

from knotpy.notation.dispatcher import from_notation_dispatcher
from abc import ABC, abstractmethod

__all__ = ["DiagramReader", "diagram_reader", "load_diagrams",
           "count_lines",
           "DiagramSetReader", "diagram_set_reader", "load_diagram_sets"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

# TODO: support lazy diagram evaluation
#
# class _BaseDiagramReader(ABC):
#     """
#     Abstract base class for file readers.
#
#     - Handles file opening, closing, and resource management.
#     - Supports reading format headers.
#     """
#
#     def __init__(self, filename, notation=None):
#         """
#         Initializes the reader. If `diagram_format` is provided, it overrides the file header.
#
#         :param filename: Path to the diagram file.
#         :param notation: (Optional) Format type ('dowker' or 'gauss').
#         """
#         filename = Path(filename)
#         self.filename = filename
#         self._file = gzip.open(self.filename, "r+b") if filename.name.endswith(".gz") else open(self.filename, "r+b")
#         self._file = open(filename, "r+b")  # Open in binary mode for mmap
#         self._mm = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
#
#         self.from_notation = None
#         # if self.diagram_format not in {"dowker", "gauss", None}:
#         #     raise ValueError(f"Unsupported notation format: {self.diagram_format}")
#
#         if notation:
#             self.from_notation = from_notation_dispatcher(notation.lower())
#         else:
#             self._initialize_format()  # Read from header if not provided
#
#     def _initialize_format(self):
#         """Reads the first line to determine the diagram format from the header."""
#         first_line = self._mm.readline().decode().strip()
#         if not first_line.endswith("notation"):
#             raise ValueError("Missing notation header")
#
#         notation = first_line.split(" ")[0].lower()
#         self.from_notation = from_notation_dispatcher(notation.lower())
#
#     @abstractmethod
#     def _parse_line(self, line):
#         """Parses a line based on the detected format."""
#         pass
#
#     def __iter__(self):
#         """Makes the reader an iterable that processes lines lazily using mmap."""
#         if self.from_notation is None:
#             raise RuntimeError("Diagram format could not be determined.")
#
#         first_line = True
#         while True:
#             line = self._mm.readline().decode()
#             if not line:
#                 break  # Stop at EOF
#
#             if first_line and self.from_notation is not None:
#                 first_line = False
#                 if line.strip().endswith("notation"):
#                     continue  # Skip header if format was explicitly given
#
#             parsed_line = self._parse_line(line)
#             if parsed_line is not None:
#                 yield parsed_line  # Yield only valid parsed lines
#
#     def close(self):
#         """Closes the memory-mapped file and underlying file."""
#         self._mm.close()
#         self._file.close()
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         self.close()


class _BaseDiagramReader(ABC):
    """
    Abstract base class for file readers.

    - Handles file opening, closing, and resource management.
    - Supports reading format headers.
    """

    def __init__(self, filename, notation=None):
        """
        Initializes the reader. If `diagram_format` is provided, it overrides the file header.

        :param filename: Path to the diagram file.
        :param notation: (Optional) Format type ('dowker' or 'gauss').
        """
        filename = Path(filename)
        self.filename = filename
        self._file = gzip.open(self.filename, "rt", encoding="utf-8") if filename.name.endswith(".gz") else open(self.filename, "rt")
        self.from_notation = None
        if notation:
            self.from_notation = from_notation_dispatcher(notation.lower())
        else:
            self._initialize_format()  # Read from header if not provided

    def _initialize_format(self):
        """Reads the first line to determine the diagram format from the header."""
        first_line = self._file.readline().strip()
        if not first_line.endswith("notation"):
            raise ValueError("Missing notation header")

        notation = first_line.split(" ")[0].lower()
        self.from_notation = from_notation_dispatcher(notation.lower())

    @abstractmethod
    def _parse_line(self, line):
        """Parses a line based on the detected format."""
        pass

    def __iter__(self):
        """Makes the reader an iterable that processes lines lazily using mmap."""
        if self.from_notation is None:
            raise RuntimeError("Diagram format could not be determined.")

        first_line = True
        while True:
            line = self._file.readline()
            if not line:
                break  # Stop at EOF

            if first_line and self.from_notation is not None:
                first_line = False
                if line.strip().endswith("notation"):
                    continue  # Skip header if format was explicitly given

            parsed_line = self._parse_line(line)
            if parsed_line is not None:
                yield parsed_line  # Yield only valid parsed lines

    def close(self):
        """Closes the memory-mapped file and underlying file."""
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class DiagramReader(_BaseDiagramReader):
    def _parse_line(self, line):
        line = line.split("#", 1)[0].strip()  # Remove comments and strip spaces
        if not line:
            return None  # Ignore empty lines
        return self.from_notation(line)  # parse diagram

class LazyDiagramReader(_BaseDiagramReader):
    def _parse_line(self, line):
        line = line.split("#", 1)[0].strip()  # Remove comments and strip spaces
        if not line:
            return None  # Ignore empty lines
        return line  # do not parse diagram

class DiagramSetReader(_BaseDiagramReader):
    def _parse_line(self, line):
        line = line.split("#", 1)[0].strip()  # Remove comments and strip spaces
        if not line:
            return None  # Ignore empty lines

        return [self.from_notation(row.strip()) for row in line.split(" & ")]  # parse diagram

class LazyDiagramSetReader(_BaseDiagramReader):
    def _parse_line(self, line):
        line = line.split("#", 1)[0].strip()  # Remove comments and strip spaces
        if not line:
            return None  # Ignore empty lines

        return [row.strip() for row in line.split(" & ")]  # do not parse diagram


###  `read_diagrams` Function (One-Liner API)**
def diagram_reader(filename, notation=None):
    """
    Simplified interface for reading diagram files.

    :param filename: Path to the file.
    :param notation: (Optional) Format type ('dowker' or 'gauss'). If None, read from header.
    :yield: Parsed diagrams.
    """
    with DiagramReader(filename, notation) as reader:
        yield from reader  # Directly yield from DiagramFileReader's iterator

def diagram_set_reader(filename, notation=None):
    """
    Simplified interface for reading diagram files.

    :param filename: Path to the file.
    :param notation: (Optional) Format type ('dowker' or 'gauss'). If None, read from header.
    :yield: Parsed diagrams.
    """
    with DiagramSetReader(filename, notation) as reader:
        yield from reader  # Directly yield from DiagramFileReader's iterator

def load_diagrams(filename, notation=None):
    """
    Loads all diagrams from a file at once.

    :param filename: Path to the file containing diagram data.
    :param notation: (Optional) Format type ('dowker', 'gauss', etc.).
                           If None, it will be detected from the file header.
    :return: A list of all parsed diagrams.
    """


    with DiagramReader(filename, notation) as reader:
        return list(reader)  # Load all diagrams into memory at once

def load_diagrams_as_dict(filename, notation=None, lazy=False):
    """
    Loads all diagrams from a file at once.

    :param filename: Path to the file containing diagram data.
    :param notation: (Optional) Format type ('dowker', 'gauss', etc.).
                           If None, it will be detected from the file header.
    :return: A list of all parsed diagrams.
    """

    def _name_from_str(s):
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

def load_diagram_sets(filename, notation=None):
    """
    Loads all diagrams from a file at once.

    :param filename: Path to the file containing diagram data.
    :param notation: (Optional) Format type ('dowker', 'gauss', etc.).
                           If None, it will be detected from the file header.
    :return: A list of all parsed diagrams.
    """
    with DiagramSetReader(filename, notation) as reader:
        return list(reader)  # Load all diagrams into memory at once

def count_lines(filename):
    """
    Counts the number of non-empty, non-comment lines in a Python file efficiently.

    :param filename: Path to the Python file.
    :return: The count of relevant lines.
    """
    with open(filename, "r+b") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            return sum(
                1 for line in iter(mm.readline, b'')  # Read line by line
                if (stripped := line.strip()) and not stripped.startswith(b"#")  # Strip spaces and ignore comments
            )


if __name__ == "__main__":
    pass
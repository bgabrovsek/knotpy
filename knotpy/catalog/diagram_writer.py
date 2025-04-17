from abc import ABC, abstractmethod
import gzip

from knotpy.notation.dispatcher import to_notation_dispatcher

__all__ = ["DiagramWriter", "save_diagrams", "DiagramSetWriter", "save_diagram_sets"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _BaseDiagramWriter(ABC):
    """
    Abstract base class for file writers.

    - Handles file opening, closing, and resource management.
    - Supports writing format headers and optional comments.
    """

    def __init__(self, filename, notation="native", comment=None,):

        """
        Initializes the writer.

        :param filename: Path to the output file.
        :param notation: The diagram notation ('dowker', 'gauss', etc.).
        :param comment: (Optional) A comment to add at the start of the file.
        """

        # if mode != "w" and mode != "a":
        #     raise ValueError("Only write 'w' or append 'a' modes are supported in the writer")

        self.filename = filename
        self.file = gzip.open(self.filename, "wt", encoding="utf-8") if filename.endswith(".gz") else open(self.filename, "wt", encoding="utf-8")

        # Write format header
        self.file.write(f"{notation} notation\n")

        # Write optional comment
        if comment:
            for line in comment.strip().split("\n"):
                self.write_comment(line)

        if notation:
            self.to_notation = to_notation_dispatcher(notation.lower())
        else:
            raise ValueError("Output format (diagram notation) must be provided")

    def write_comment(self, comment):
        self.file.write(f"# {comment}\n")

    def close(self):
        """Closes the file."""
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class DiagramWriter(_BaseDiagramWriter):
    """
    A file writer for knot diagrams.
    - Writes one diagram at a time per line, using a given notation.
    - Supports adding an optional comment at the start of the file.
    """

    def write_diagram(self, diagram):
        """
        Converts and writes a single diagram to the file.
        :param diagram: The diagram object.
        """
        self.file.write(self.to_notation(diagram) + "\n")

    def write_diagrams(self, diagrams):
        """
        Converts and writes a single diagram to the file.
        :param diagrams: A list of diagram object.
        """
        for diagram in diagrams:
            self.write_diagram(diagram)


class DiagramSetWriter(_BaseDiagramWriter):

    def write_diagram_set(self, diagram_set):
        """
        Converts and writes a set/list of diagrams to the file on a single line.

        :param diagram_set: A set/list of diagrams.
        """

        line = " & ".join(self.to_notation(diagram) for diagram in diagram_set)
        self.file.write(line + "\n")


    pass

def save_diagrams(filename, diagrams, notation="native", comment=None):
    """
    Writes multiple diagrams to a file at once.

    :param filename: Path to the output file.
    :param diagrams: A list of diagrams to write.
    :param notation: The diagram notation ('dowker', 'gauss', etc.).
    :param to_string_func: Function to convert diagrams into strings.
    :param comment: (Optional) A comment to add at the start of the file.
    """
    with DiagramWriter(filename=filename, notation=notation, comment=comment) as writer:
        for diagram in diagrams:
            writer.write_diagram(diagram)


def save_diagram_sets(filename, diagram_sets, notation="native", comment=None):
    """
    Writes multiple sets of diagrams to a file at once.

    :param filename: Path to the output file.
    :param diagrams: A list of diagrams to write.
    :param notation: The diagram notation ('dowker', 'gauss', etc.).
    :param to_string_func: Function to convert diagrams into strings.
    :param comment: (Optional) A comment to add at the start of the file.
    """
    with DiagramSetWriter(filename=filename, notation=notation, comment=comment) as writer:
        for diagrams in diagram_sets:
            writer.write_diagram_set(diagrams)
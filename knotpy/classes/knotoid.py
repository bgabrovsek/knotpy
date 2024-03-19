from functools import cached_property

from knotpy.classes.planardiagram import PlanarDiagram, _NodeCachedPropertyResetter
from knotpy.classes.knot import Knot
from knotpy.classes.node import Crossing, Terminal #BivalentVertex,
from knotpy.classes.views import FilteredNodeView

__all__ = ['Knotoid']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


class Knotoid(Knot):

    # init the descriptor instance, parameter keys are node types, values are cached propery names
    _nodes: dict = _NodeCachedPropertyResetter(Crossing="crossings",
                                               BivalentVertex="bivalent_vertices",
                                               Terminal="terminals")

    def __init__(self, **attr):
        self._nodes = dict()
        super().__init__(**attr)

    @cached_property
    def terminals(self):
        """Node object holding the adjacencies of each node."""
        return FilteredNodeView(self._nodes, node_type=Terminal)

    def add_terminal(self, terminal_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        terminal = terminal_for_adding

        if terminal is None:
            raise ValueError("None cannot be a crossing")

        if terminal not in self._nodes:
            self._nodes[terminal] = Terminal()
        self._nodes[terminal].attr.update(attr)

    def add_terminals_from(self, terminals_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        for terminal in terminals_for_adding:
            self.add_terminal(terminal, **attr)


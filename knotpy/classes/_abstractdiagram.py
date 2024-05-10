from abc import ABC, ABCMeta, abstractmethod
from functools import cached_property

from knotpy.classes.views import FilteredNodeView
from knotpy.classes.node import *


class _NodeDiagram(ABC):
    """

    """
    _nodes: dict

    @abstractmethod
    def add_node(self, node_for_adding, create_using: type, degree=None, **attr):
        pass

    @abstractmethod
    def add_nodes_from(self, nodes_for_adding, create_using=None, **attr):
        pass

class _CrossingDiagram(_NodeDiagram, metaclass=ABCMeta):

    @cached_property
    def crossings(self):
        """Node object holding the adjacencies of each crossing."""
        return FilteredNodeView(self._nodes, node_type=Crossing)

    def add_crossing(self, crossing_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=crossing_for_adding, create_using=Crossing, degree=4, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        for node in crossings_for_adding:
            self.add_crossing(crossings_for_adding=node, **attr)


class _VirtualCrossingDiagram(_NodeDiagram, metaclass=ABCMeta):

    @cached_property
    def virtual_crossings(self):
        """Node object holding the adjacencies of each crossing."""
        return FilteredNodeView(self._nodes, node_type=VirtualCrossing)

    def add_virtual_crossing(self, crossing_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=crossing_for_adding, create_using=VirtualCrossing, degree=4, **attr)

    def add_virtual_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        for node in crossings_for_adding:
            self.add_virtual_crossing(crossings_for_adding=node, **attr)


class _VertexDiagram(_NodeDiagram, metaclass=ABCMeta):

    @cached_property
    def vertices(self):
        """Node object holding the adjacencies of each crossing."""
        return FilteredNodeView(self._nodes, node_type=Vertex)

    def add_vertex(self, vertex_for_adding, degree=None, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=vertex_for_adding, create_using=Vertex, degree=degree, **attr)

    def add_vertices_from(self, vertices_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        for node in vertices_for_adding:
            self.add_vertex(vertex_for_adding=node, **attr)


class _TerminalDiagram(_NodeDiagram, metaclass=ABCMeta):

    @cached_property
    def terminals(self):
        """Node object holding the adjacencies of each crossing."""
        return FilteredNodeView(self._nodes, node_type=Terminal)

    def add_terminal(self, terminal_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=terminal_for_adding, create_using=Terminal, degree=1, **attr)

    def add_terminals_from(self, terminal_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        for node in terminal_for_adding:
            self.add_terminal(terminal_for_adding=node, **attr)


class _BondDiagram(_NodeDiagram, metaclass=ABCMeta):

    @cached_property
    def bonds(self):
        """Node object holding the adjacencies of each crossing."""
        return FilteredNodeView(self._nodes, node_type=Bond)

    def add_bond(self, bond_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=bond_for_adding, create_using=Bond, degree=4, **attr)

    def add_bonds_from(self, bonds_for_adding, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        for node in bonds_for_adding:
            self.add_bond(bond_for_adding=node, **attr)



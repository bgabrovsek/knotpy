from abc import ABC, ABCMeta, abstractmethod
from functools import cached_property

from knotpy.classes.views import FilteredNodeView
from knotpy.classes.node import *


class _NodeDiagram(ABC):
    """
    Abstract base class for node-based planar diagrams. Nodes can be vertices, crossings, or virtual crossings.

    This class defines the interface for handling nodes in planar diagrams.
    Subclasses must implement methods for adding nodes individually or in bulk.

    :ivar _nodes: A dictionary storing the nodes of the diagram.
    :type _nodes: dict
    """
    _nodes: dict

    @abstractmethod
    def add_node(self, node_for_adding, create_using: type, degree=None, **attr):
        pass

    @abstractmethod
    def add_nodes_from(self, nodes_for_adding, create_using=None, **attr):
        pass

    def is_frozen(self):
        """Returns True if the given diagram is frozen, False otherwise."""
        try:
            return self.frozen
        except AttributeError:
            return False


class _CrossingDiagram(_NodeDiagram, metaclass=ABCMeta):
    """
    Abstract base class for diagrams containing crossings.

    This class extends `_NodeDiagram` to handle crossings in a planar diagram.
    Crossings are represented as nodes with degree 4, where even positions (0, 2) are "under endpoints" and odd positions
    (1, 3) are "over endpoints"

    :ivar crossings: A view of all crossings in the diagram.
    :type crossings: FilteredNodeView
    """

    @cached_property
    def crossings(self):
        """
        Return a view of all crossings in the diagram.

        :return: A filtered node view containing only crossings.
        :rtype: FilteredNodeView
        """
        return FilteredNodeView(self._nodes, node_type=Crossing)

    def add_crossing(self, crossing_for_adding, **attr):
        """
        Add or update a crossing in the diagram.

        :param crossing_for_adding: The crossing to add or update.
        :type crossing_for_adding: Hashable
        :param attr: Additional attributes for the crossing (color, weight, ...)
        """

        self.add_node(node_for_adding=crossing_for_adding, create_using=Crossing, degree=4, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """
        Add multiple crossings to the diagram.

        :param crossings_for_adding: An iterable of crossings to add.
        :type crossings_for_adding: Iterable of hashable instances
        :param attr: Additional attributes for the crossings.
        """
        for node in crossings_for_adding:
            self.add_crossing(crossings_for_adding=node, **attr)

    def sign(self, crossing):
        return self._nodes[crossing].sign()


class _VirtualCrossingDiagram(_NodeDiagram, metaclass=ABCMeta):
    """
    Abstract base class for diagrams containing virtual crossings.

    This class extends `_NodeDiagram` to handle virtual crossings in a planar diagram.
    Virtual crossings are represented as nodes with degree 4.

    :ivar virtual_crossings: A view of all virtual crossings in the diagram.
    :type virtual_crossings: FilteredNodeView
    """

    @cached_property
    def virtual_crossings(self):
        """
        Return a view of all virtual crossings in the diagram.

        :return: A filtered node view containing only virtual crossings.
        :rtype: FilteredNodeView
        """
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

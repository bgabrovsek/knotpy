from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Hashable, Iterable
from functools import cached_property

from knotpy.classes.node import Crossing, Node, Vertex, VirtualCrossing
from knotpy.classes.views import FilteredNodeView

__all__ = [
    "_NodeDiagram",
    "_CrossingDiagram",
    "_VirtualCrossingDiagram",
    "_VertexDiagram",
]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


class _NodeDiagram(ABC):
    """Abstract base for node-based planar diagrams.

    Nodes can be vertices, classical crossings, or virtual crossings. Subclasses
    must implement methods for adding nodes (individually or in bulk).

    Attributes:
        _nodes (dict[Hashable, Node]): Mapping from node identifiers to node instances.
    """

    _nodes: dict[Hashable, Node]

    @abstractmethod
    def add_node(
        self,
        node_for_adding: Hashable,
        create_using: type,
        degree: int | None = None,
        **attr: object,
    ) -> None:
        """Add (or update) a single node.

        Args:
            node_for_adding: Node identifier (hashable).
            create_using: Concrete node class to construct (e.g., ``Vertex`` or ``Crossing``).
            degree: Optional degree for the new node (e.g., 4 for crossings).
            **attr: Additional node attributes.
        """

    @abstractmethod
    def add_nodes_from(
        self,
        nodes_for_adding: Iterable[Hashable] | dict[Hashable, Node],
        create_using: type | None = None,
        **attr: object,
    ) -> None:
        """Add (or update) a collection of nodes.

        Args:
            nodes_for_adding: Iterable of node identifiers or a mapping of identifiers to node instances.
            create_using: Concrete node class to use for construction when identifiers are provided.
            **attr: Additional attributes applied to created/updated nodes.
        """

    def is_locked(self) -> bool:
        """Return whether the diagram is frozen.

        Returns:
            bool: ``True`` if frozen; otherwise ``False``.
        """
        try:
            return getattr(self, "frozen") == "locked"
        except AttributeError:
            return False

    def is_frozen(self) -> bool:
        """Return whether the diagram is frozen.

        Returns:
            bool: ``True`` if frozen; otherwise ``False``.
        """
        try:
            return bool(getattr(self, "frozen"))
        except AttributeError:
            return False


class _CrossingDiagram(_NodeDiagram, metaclass=ABCMeta):
    """Abstract base for diagrams that contain classical crossings.

    Crossings are nodes of degree 4; even endpoints (0, 2) are "under", odd endpoints (1, 3) are "over".

    Attributes:
        crossings (FilteredNodeView): View of all classical crossings.
    """

    @cached_property
    def crossings(self) -> FilteredNodeView:
        """Return a view of all classical crossings.

        Returns:
            FilteredNodeView: Filtered node view containing only classical crossings.
        """
        return FilteredNodeView(self._nodes, node_type=Crossing)

    def add_crossing(self, crossing_for_adding: Hashable, **attr: object) -> None:
        """Add or update a classical crossing.

        Args:
            crossing_for_adding: Crossing identifier (hashable).
            **attr: Additional attributes (e.g., color, weight).
        """
        self.add_node(
            node_for_adding=crossing_for_adding,
            create_using=Crossing,
            degree=4,
            **attr,
        )

    def add_crossings_from(
        self, crossings_for_adding: Iterable[Hashable], **attr: object
    ) -> None:
        """Add or update multiple classical crossings.

        Args:
            crossings_for_adding: Iterable of crossing identifiers.
            **attr: Additional attributes applied to each crossing.
        """
        for node in crossings_for_adding:
            # FIX: use the correct parameter name for the single-add method
            self.add_crossing(crossing_for_adding=node, **attr)

    def sign(self, crossing: Hashable) -> int:
        """Return the sign of a crossing.

        Args:
            crossing: Crossing identifier.

        Returns:
            int: Crossing sign (usually ``+1`` or ``-1``).
        """
        return self._nodes[crossing].sign()


class _VirtualCrossingDiagram(_NodeDiagram, metaclass=ABCMeta):
    """Abstract base for diagrams that contain virtual crossings.

    Virtual crossings are modeled as nodes of degree 4.

    Attributes:
        virtual_crossings (FilteredNodeView): View of all virtual crossings.
    """

    @cached_property
    def virtual_crossings(self) -> FilteredNodeView:
        """Return a view of all virtual crossings.

        Returns:
            FilteredNodeView: Filtered node view containing only virtual crossings.
        """
        return FilteredNodeView(self._nodes, node_type=VirtualCrossing)

    def add_virtual_crossing(
        self, crossing_for_adding: Hashable, **attr: object
    ) -> None:
        """Add or update a virtual crossing.

        Args:
            crossing_for_adding: Crossing identifier (hashable).
            **attr: Additional attributes.
        """
        self.add_node(
            node_for_adding=crossing_for_adding,
            create_using=VirtualCrossing,
            degree=4,
            **attr,
        )

    def add_virtual_crossings_from(
        self, crossings_for_adding: Iterable[Hashable], **attr: object
    ) -> None:
        """Add or update multiple virtual crossings.

        Args:
            crossings_for_adding: Iterable of crossing identifiers.
            **attr: Additional attributes applied to each virtual crossing.
        """
        for node in crossings_for_adding:
            # FIX: use the correct parameter name for the single-add method
            self.add_virtual_crossing(crossing_for_adding=node, **attr)


class _VertexDiagram(_NodeDiagram, metaclass=ABCMeta):
    """Abstract base for diagrams that contain vertices."""

    @cached_property
    def vertices(self) -> FilteredNodeView:
        """Return a view of all vertices.

        Returns:
            FilteredNodeView: Filtered node view containing only vertices.
        """
        return FilteredNodeView(self._nodes, node_type=Vertex)

    def add_vertex(
        self, vertex_for_adding: Hashable, degree: int | None = None, **attr: object
    ) -> None:
        """Add or update a vertex.

        Args:
            vertex_for_adding: Vertex identifier (hashable).
            degree: Vertex degree (``None`` if not constrained).
            **attr: Additional attributes.
        """
        self.add_node(
            node_for_adding=vertex_for_adding,
            create_using=Vertex,
            degree=degree,
            **attr,
        )

    def add_vertices_from(
        self, vertices_for_adding: Iterable[Hashable], **attr: object
    ) -> None:
        """Add or update multiple vertices.

        Args:
            vertices_for_adding: Iterable of vertex identifiers.
            **attr: Additional attributes applied to each vertex.
        """
        for node in vertices_for_adding:
            self.add_vertex(vertex_for_adding=node, **attr)


if __name__ == "__main__":
    pass

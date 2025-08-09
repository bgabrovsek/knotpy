from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from functools import cached_property
from itertools import chain
from typing import Any

from knotpy.utils.dict_utils import compare_dicts
from knotpy.utils.decorators import total_ordering_from_compare
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node import Node, Crossing, Vertex, VirtualCrossing
from knotpy.classes.views import NodeView, EndpointView, ArcView, FaceView, FilteredNodeView
from knotpy.classes._abstractdiagram import _CrossingDiagram, _VertexDiagram, _VirtualCrossingDiagram

__all__ = ["PlanarDiagram", "OrientedPlanarDiagram", "Diagram", "DiagramCollection", "UnorientedDiagramCollection"]
__version__ = "0.1.1"
__author__ = "Boštjan Gabrovšek"


class _NodeCachedPropertyResetter:
    """Data descriptor that resets cached properties related to node-type views.

    For details on descriptors, see https://docs.python.org/3/howto/descriptor.html.

    This descriptor ensures that when the internal mapping ``_nodes`` changes,
    derived views (e.g., crossings, vertices, virtual crossings, faces, …) are
    invalidated and recomputed on next access.

    Args:
        _node_type_property_names (dict[str, str]): Mapping from node type names
            (e.g., ``"Vertex"``) to the corresponding cached property name
            (e.g., ``"vertices"``) that should be cleared when ``_nodes`` changes.
    """

    def __init__(self, **_node_type_property_names: str) -> None:
        """Initialize the descriptor.

        Args:
            _node_type_property_names (dict[str, str]): Mapping of node-type
                names to cached property names.
        """
        self._node_type_property_names: dict[str, str] = _node_type_property_names

    def add_property_name(self, **_node_type_property_names: str) -> None:
        """Register additional node-type-specific cached properties.

        Args:
            _node_type_property_names (dict[str, str]): Additional mappings of
                node-type names to cached property names.
        """
        self._node_type_property_names.update(_node_type_property_names)

    def __set__(self, obj: PlanarDiagram, value: dict[Hashable, Node]) -> None:
        """Set ``_nodes`` and reset cached properties.

        The instance variable ``_nodes`` has changed; remove cached properties so
        that all derived views are recomputed on next access.

        Args:
            obj (PlanarDiagram): Diagram instance whose ``_nodes`` is being set.
            value (dict[Hashable, Node]): New mapping of nodes to node instances.
        """
        od = obj.__dict__
        od["_nodes"] = value

        # Common cached properties on all planar diagrams
        for common in ("nodes", "endpoints", "arcs", "faces"):
            if common in od:
                del od[common]

        # Node-type-specific cached properties
        for node_type in self._node_type_property_names:
            prop_name = self._node_type_property_names[node_type]
            if prop_name in od:
                del od[prop_name]


@total_ordering_from_compare
class PlanarDiagram(_CrossingDiagram, _VertexDiagram, _VirtualCrossingDiagram):
    """Planar diagram for spatial graphs, knots, links, and related structures.

    The diagram holds nodes (vertices/crossings), endpoints (incidences of nodes),
    arcs (pairs of endpoints), and faces (regions). Many of these are derived
    views over the core ``_nodes`` structure and cached lazily.

    Attributes:
        _nodes (dict[Hashable, Node]): Internal mapping from node identifiers to node instances.
        attr (dict[str, Any]): Diagram-level attributes (e.g., name, framing, meta).
    """

    # Cache views of specific node types (vertices, crossings, virtual crossings)
    _nodes: dict[Hashable, Node] = _NodeCachedPropertyResetter(
        Vertex="vertices",
        Crossing="crossings",
        VirtualCrossing="virtual_crossings",
    )

    def __init__(self, incoming_diagram_data: Any | None = None, **attr: Any) -> None:
        """Initialize a planar diagram.

        If no data is provided, an empty diagram is created. Otherwise, the diagram
        is populated from the provided input.

        Args:
            incoming_diagram_data: Data used to construct/populate the diagram, or ``None``.
            **attr: Diagram attributes to set (e.g., ``name``, ``framing``).
        """
        super(_CrossingDiagram, self).__init__()

        if incoming_diagram_data is None:
            self._nodes = {}
            self.attr: dict[str, Any] = {}
        else:
            planar_diagram_from_data(incoming_data=incoming_diagram_data, create_using=self)

        self.attr.update(attr)

    def clear(self) -> None:
        """Remove all nodes and attributes from the diagram."""
        self._nodes = {}
        self.attr = {}

    def copy(self, copy_using: type[PlanarDiagram] | None = None, **attr: Any) -> PlanarDiagram:
        """Return a shallow copy of the diagram.

        Serves for converting, e.g., oriented to unoriented diagrams.

        Args:
            copy_using (Optional[type[PlanarDiagram]]): Concrete diagram type to create;
                defaults to ``type(self)``.

        Returns:
            PlanarDiagram: New diagram instance with duplicated structure and attributes.
        """
        copy_using = copy_using or type(self)
        the_copy = planar_diagram_from_data(incoming_data=self, create_using=copy_using)
        the_copy.attr.update(attr)
        return the_copy

    # Views

    @cached_property
    def nodes(self) -> NodeView:
        """Return a view of the diagram's nodes, providing adjacency information.

        Returns:
            NodeView: View of nodes backed by the internal mapping.
        """
        return NodeView(self._nodes)

    @cached_property
    def endpoints(self) -> EndpointView:
        """Return a view of endpoints.

        Returns:
            EndpointView: View of all endpoints in the diagram.
        """
        return EndpointView(self._nodes)

    @cached_property
    def arcs(self) -> ArcView:
        """Return a view of arcs (pairs of endpoints).

        Returns:
            ArcView: View of diagram arcs.
        """
        return ArcView(self._nodes)

    @cached_property
    def faces(self) -> FaceView:
        """Return a view of faces (regions enclosed by arcs).

        Returns:
            FaceView: View of diagram faces.
        """
        return FaceView(self._nodes)

    # Basic protocol

    def __len__(self) -> int:
        """Return the number of nodes in the diagram.

        Returns:
            int: Number of nodes.
        """
        return len(self._nodes)

    def _compare(self, other: Any, compare_attributes: bool | Sequence[str] = True) -> int:
        """Compare two diagrams by structure and (optionally) attributes.

        The ordering is defined by:
        1) type, 2) number of nodes, 3) number of endpoints,
        4) degree sequence, 5) node identifiers,
        6) per-node endpoint structure, 7) framing, 8) diagram attributes.

        Args:
            other: Object to compare with (must be a PlanarDiagram of same dynamic type).
            compare_attributes: If ``False`` → ignore attributes. If ``True`` → compare all
                attributes except transient ones. If a collection → compare only those keys.

        Returns:
            int: ``1`` if ``self > other``, ``-1`` if ``self < other``, else ``0``.
        """
        # 1) type
        if type(self) is not type(other):
            # REVIEW: original returned a TypeError object, which breaks ordering.
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}.")

        # 2) number of nodes
        s_nn, o_nn = len(self._nodes), len(other._nodes)
        if s_nn != o_nn:
            return -1 if s_nn < o_nn else 1

        # 3) number of endpoints
        s_ep = sum(len(self._nodes[node]._inc) for node in self._nodes)
        o_ep = sum(len(other._nodes[node]._inc) for node in other._nodes)
        if s_ep != o_ep:
            return -1 if s_ep < o_ep else 1

        # 4) degree sequence (FIX: other used self twice)
        deg_seq_self = sorted(len(self._nodes[node]) for node in self._nodes)
        deg_seq_other = sorted(len(other._nodes[node]) for node in other._nodes)
        if deg_seq_self != deg_seq_other:
            return -1 if deg_seq_self < deg_seq_other else 1

        # 5) node identifiers
        self_nodes_sorted = sorted(self._nodes)
        other_nodes_sorted = sorted(other._nodes)
        if self_nodes_sorted != other_nodes_sorted:
            return -1 if self_nodes_sorted < other_nodes_sorted else 1

        # 6) per-node endpoint structure
        for node in self_nodes_sorted:
            cmp = self._nodes[node]._compare(other._nodes[node], compare_attributes=compare_attributes)
            if cmp:
                return int(cmp)

        # 7) framing (treat None as 0)
        self_fr = self.framing or 0
        other_fr = other.framing or 0
        if self_fr != other_fr:
            return 1 if self_fr > other_fr else -1

        # 8) attributes (skip private-like keys and a small fixed set)
        exclude_keys = (
            {"name", "framing", "frozen"}
            | {a for a in self.attr if isinstance(a, str) and a.startswith("_")}
            | {a for a in other.attr if isinstance(a, str) and a.startswith("_")}
        )
        if compare_attributes is True:
            return compare_dicts(self.attr, other.attr, exclude_keys=exclude_keys)
        if isinstance(compare_attributes, (list, set, tuple)):
            return compare_dicts(
                self.attr,
                other.attr,
                exclude_keys=exclude_keys,
                include_only_keys=compare_attributes,
            )

        return 0

    def __getitem__(self, item: Any) -> Any:
        """Return a diagram element by description.

        Note:
            This is a placeholder. Implement as needed to support item-based access.

        Raises:
            NotImplementedError: Always, until implemented.
        """
        raise NotImplementedError()

    # Node operations

    def add_node(
        self,
        node_for_adding: Hashable,
        create_using: type,
        degree: int | None = None,
        **attr: Any,
    ) -> None:
        """Add or update a single node.

        Args:
            node_for_adding: Node identifier (hashable).
            create_using: Node class to construct (e.g., ``Vertex`` or ``Crossing``).
            degree: Degree of the node (optional).
            **attr: Additional attributes to store on the node.

        Raises:
            TypeError: If ``create_using`` is not a type.
            ValueError: If ``node_for_adding`` is ``None``.
            NotImplementedError: If attempting to change an existing node's concrete type.
        """
        if create_using is not None and not isinstance(create_using, type):
            raise TypeError(f"Creating node with create_using instance {create_using} not yet supported.")

        node = node_for_adding
        if node is None:
            raise ValueError(f"None cannot be a {create_using.__name__.lower()}")

        if node not in self._nodes:
            if not isinstance(create_using, type):
                create_using = type(create_using)
            self._nodes[node] = create_using(degree=degree)
        elif type(self._nodes[node]) is not create_using:
            # REVIEW: consider supporting a safe node-type conversion path here.
            raise NotImplementedError("Node type change not implemented")

        self._nodes[node].attr.update(attr)

    def add_nodes_from(
        self,
        nodes_for_adding: Iterable[Hashable] | dict[Hashable, Node],
        create_using: type | None = None,
        **attr: Any,
    ) -> None:
        """Add or update multiple nodes.

        Args:
            nodes_for_adding: Iterable of node identifiers or mapping to existing node instances.
            create_using: Node class used when creating from identifiers.
            **attr: Additional attributes applied to created/updated nodes.
        """
        if isinstance(nodes_for_adding, dict):
            for node, inst in nodes_for_adding.items():
                # carry over degree and attributes from instance + new attrs
                self.add_node(
                    node_for_adding=node,
                    create_using=type(inst),
                    degree=len(inst),
                    **(inst.attr | attr),
                )
        else:
            for node in nodes_for_adding:
                if "degree" in attr:
                    self.add_node(node_for_adding=node, create_using=create_using, **attr)
                else:
                    self.add_node(node_for_adding=node, create_using=create_using, degree=None, **attr)

    def add_crossings_from(self, crossings_for_adding: Iterable[Hashable], **attr: Any) -> None:
        """Add or update multiple classical crossings.

        Args:
            crossings_for_adding: Iterable of crossing identifiers.
            **attr: Additional attributes for crossings.
        """
        self.add_nodes_from(nodes_for_adding=crossings_for_adding, create_using=Crossing, **attr)

    def add_vertex(self, vertex_for_adding: Hashable, degree: int | None = None, **attr: Any) -> None:
        """Add or update a vertex.

        Args:
            vertex_for_adding: Vertex identifier.
            degree: Optional vertex degree.
            **attr: Additional attributes.
        """
        self.add_node(node_for_adding=vertex_for_adding, create_using=Vertex, degree=degree, **attr)

    def permute_node(self, node: Hashable, permutation: dict[int, int] | Sequence[int]) -> None:
        """Permute positions of a node's endpoints.

        If ``permutation = {0: 0, 1: 2, 2: 3, 3: 1}`` (or a list/tuple with these images),
        and the CCW endpoints are ``[a, b, c, d]``, the new endpoints become ``[a, d, b, c]``.

        Args:
            node: Node whose endpoints should be permuted.
            permutation: Mapping or sequence describing the new positions.

        Notes:
            Endpoint attributes are preserved via ``set_endpoint``. Loops may require special care.
        """
        if isinstance(permutation, (list, tuple)):
            permutation = dict(enumerate(permutation))

        old_adj_node_data = list(self.nodes[node])  # CCW sequence (adjacent endpoints)
        old_node_data = list(self.endpoints[node])
        for ep, adj_ep in zip(old_node_data, old_adj_node_data):
            self.set_endpoint(
                endpoint_for_setting=adj_ep,
                adjacent_endpoint=(ep.node, permutation[ep.position]),
                create_using=type(ep),
                **ep.attr,
            )
            self._nodes[ep.node][permutation[ep.position]] = adj_ep

    def convert_node(self, node_for_converting: Hashable, node_type: type) -> None:
        """Convert a node's concrete type (e.g., vertex → crossing).

        Args:
            node_for_converting: Node identifier.
            node_type: Target node class (e.g., ``Crossing``).
        """
        node_inst = self._nodes[node_for_converting]
        if type(node_inst) is not node_type:
            self._nodes[node_for_converting] = node_type(
                incoming_node_data=node_inst._inc,  # REVIEW: relies on internal shape
                degree=len(node_inst),
                *node_inst.attr,  # REVIEW: confirm the node constructor signature supports this splat
            )

    def convert_nodes(self, nodes_for_converting: Iterable[Hashable], node_type: type) -> None:
        """Convert multiple nodes to a given concrete type.

        Args:
            nodes_for_converting: Iterable of node identifiers.
            node_type: Target node class (e.g., ``Crossing``).
        """
        for node in nodes_for_converting:
            self.convert_node(node, node_type)

    def remove_node(self, node_for_removing: Hashable, remove_incident_endpoints: bool = True) -> PlanarDiagram:
        """Remove a node (optionally removing incident endpoints).

        Args:
            node_for_removing: Node identifier to remove.
            remove_incident_endpoints: If ``False``, leaves dangling endpoints (breaks planarity).

        Returns:
            PlanarDiagram: The diagram (mutated).
        """
        node = node_for_removing
        if remove_incident_endpoints:
            self.remove_endpoints_from(self._nodes[node])
        del self._nodes[node]
        return self

    def remove_nodes_from(self, nodes_for_removal: Iterable[Hashable], remove_incident_endpoints: bool = True) -> None:
        """Remove multiple nodes.

        Args:
            nodes_for_removal: Iterable of node identifiers.
            remove_incident_endpoints: If ``False``, leaves dangling endpoints.
        """
        for node in nodes_for_removal:
            self.remove_node(node, remove_incident_endpoints)

    def degree(self, node: Hashable) -> int:
        """Return a node's degree.

        Args:
            node: Node identifier.

        Returns:
            int: Degree of the node.
        """
        return len(self._nodes[node])

    def relabel_nodes(self, mapping: dict[Hashable, Hashable]) -> None:
        """Relabel nodes using a (possibly partial) mapping.

        Args:
            mapping: Node-identifier mapping. Unmapped nodes keep original identifiers.
        """
        self._nodes = {mapping.get(node, node): node_inst for node, node_inst in self._nodes.items()}
        for ep in self.endpoints:
            ep.node = mapping.get(ep.node, ep.node)

    # Endpoint operations

    def set_endpoint(
        self,
        endpoint_for_setting: Endpoint | tuple[Hashable, int],
        adjacent_endpoint: Endpoint | tuple[Hashable, int],
        create_using: type = Endpoint,
        **attr: Any,
    ) -> None:
        """Set an endpoint to the specified adjacent endpoint, updating attributes.

        Args:
            endpoint_for_setting: Endpoint instance or pair ``(node, position)`` to modify.
            adjacent_endpoint: Endpoint instance or pair ``(node, position)`` to set as the twin.
            create_using: Endpoint class to construct if tuples are provided. If an instance is given,
                its concrete type is used and attributes copied.
            **attr: Additional attributes for the adjacent endpoint.

        Raises:
            TypeError: If ``create_using`` is not a type.
            ValueError: If orientation constraints are violated.
        """
        # Promote create_using if the adjacent is oriented but create_using is generic Endpoint
        if isinstance(adjacent_endpoint, (OutgoingEndpoint, IngoingEndpoint)) and create_using is Endpoint:
            create_using = type(adjacent_endpoint)

        if not isinstance(create_using, type):
            raise TypeError("Creating endpoint with create_using instance not yet supported.")

        if self.is_oriented() and not create_using.is_oriented():
            raise ValueError(
                f"Cannot add an unoriented endpoint ({create_using.__name__}) to an oriented diagram ({type(self).__name__})"
            )
        if not self.is_oriented() and create_using.is_oriented():
            raise ValueError(
                f"Cannot add an oriented ({create_using.__name__}) endpoint to an unoriented diagram ({type(self).__name__})"
            )

        node, node_pos = endpoint_for_setting

        # Normalize inputs to tuples; copy attributes if Endpoint instances are provided
        if isinstance(endpoint_for_setting, Endpoint):
            endpoint_for_setting = (endpoint_for_setting.node, endpoint_for_setting.position)
        if isinstance(adjacent_endpoint, Endpoint):
            attr = adjacent_endpoint.attr | attr
            adjacent_endpoint = (adjacent_endpoint.node, adjacent_endpoint.position)

        adj = create_using(*adjacent_endpoint, **attr)

        # Ensure node has capacity for this position
        for _ in range(node_pos + 1 - len(self._nodes[node])):
            self._nodes[node].append(Node)

        self._nodes[node][node_pos] = adj

    def twin(self, endpoint: Endpoint | tuple[Hashable, int]) -> Endpoint:
        """Return the opposite endpoint (twin) of an endpoint.

        Args:
            endpoint: Endpoint instance or pair ``(node, position)``.

        Returns:
            Endpoint: The twin endpoint instance.
        """
        node, position = endpoint
        return self._nodes[node][position]

    def endpoint_from_pair(self, endpoint_pair: Endpoint | tuple[Hashable, int | str]) -> Endpoint:
        """Return the endpoint instance given a pair description.

        If the second component is a descriptive string for a crossing endpoint
        (e.g., ``"over ingoing"``), this resolves to the appropriate endpoint.

        Args:
            endpoint_pair: Endpoint instance or pair ``(node, position_or_description)``.

        Returns:
            Endpoint: Resolved endpoint instance.

        Raises:
            ValueError: If description is invalid or node is not a crossing.
        """
        if isinstance(endpoint_pair, Endpoint):
            return endpoint_pair

        # Handle descriptive form at crossings
        if isinstance(endpoint_pair[1], str):
            node, desc = endpoint_pair
            if node not in self.crossings:
                raise ValueError(f"Cannot get a descriptive endpoint from a node that is not a crossing: {node}")
            desc_norm = desc.strip().lower()

            # Accept common shorthands
            if desc_norm in ("oi", "io", "over ingoing", "ingoing over"):
                return self.twin(self.twin((node, 1))) if isinstance(self.nodes[node][1], OutgoingEndpoint) else self.twin(
                    self.twin((node, 3))
                )
            elif desc_norm in ("oo", "over outgoing", "outgoing over"):
                return self.twin(self.twin((node, 1))) if isinstance(self.nodes[node][1], IngoingEndpoint) else self.twin(
                    self.twin((node, 3))
                )
            elif desc_norm in ("ui", "iu", "under ingoing", "ingoing under"):
                return self.twin(self.twin((node, 0))) if isinstance(self.nodes[node][0], OutgoingEndpoint) else self.twin(
                    self.twin((node, 1))
                )
            elif desc_norm in ("uo", "under outgoing", "outgoing under"):
                return self.twin(self.twin((node, 0))) if isinstance(self.nodes[node][0], IngoingEndpoint) else self.twin(
                    self.twin((node, 1))
                )
            else:
                raise ValueError(f"Unknown description {desc} for endpoint {endpoint_pair}")

        # Otherwise, treat as numeric pair (node, position)
        return self.twin(self.twin(endpoint_pair))  # TODO: consider a more direct resolution.

    def remove_endpoint(self, endpoint_for_removal: Endpoint | tuple[Hashable, int]) -> None:
        """Remove a single endpoint and adjust neighbor positions.

        Args:
            endpoint_for_removal: Endpoint instance or pair ``(node, position)``.
        """
        node, pos = endpoint_for_removal
        del self._nodes[node][pos]

        # Adjust positions for adjacent endpoints in the suffix
        for adj_node, adj_pos in self._nodes[node][pos:]:
            adj_node_inst = self._nodes[adj_node]
            if adj_node == node and adj_pos >= pos:
                adj_pos -= 1

            adj_node_inst[adj_pos] = Endpoint(
                adj_node_inst[adj_pos].node,
                adj_node_inst[adj_pos].position - 1,
                **adj_node_inst[adj_pos].attr,
            )

    def remove_endpoints_from(self, endpoints_for_removal: Iterable[Endpoint | tuple[Hashable, int]]) -> None:
        """Remove multiple endpoints safely (order-aware).

        Args:
            endpoints_for_removal: Iterable of endpoint instances or pairs.
        """
        eps = [ep if isinstance(ep, Endpoint) else self.endpoint_from_pair(ep) for ep in endpoints_for_removal]
        eps.sort(key=lambda _: _.position)
        while eps:
            ep = eps.pop()
            self.remove_endpoint(ep)
            # Adjust remaining endpoints on the same node to account for position shift
            for i, _ in enumerate(eps):
                if _.node == ep.node and _.position > ep.position:
                    eps[i] = type(_)(_.node, _.position - 1)  # attributes not needed here

    # Arc operations

    def set_arc(self, arc_for_setting: tuple[Endpoint | tuple[Hashable, int], Endpoint | tuple[Hashable, int]], **attr: Any) -> None:
        """Set an arc (pair of endpoints), setting each endpoint to the other.

        Args:
            arc_for_setting: Tuple ``(v_endpoint, u_endpoint)`` each as Endpoint or pair.
            **attr: Additional attributes to apply to the endpoints.
        """
        v_endpoint, u_endpoint = arc_for_setting
        self.set_endpoint(v_endpoint, u_endpoint, **attr)
        self.set_endpoint(u_endpoint, v_endpoint, **attr)

    def set_arcs_from(
        self,
        arcs_for_adding: Iterable[tuple[Endpoint | tuple[Hashable, int], Endpoint | tuple[Hashable, int]]] | str,
        **attr: Any,
    ) -> None:
        """Set multiple arcs, optionally parsing from a simple string syntax.

        Example string: ``"a1b4,c2d3"``—also creates missing vertices when needed.

        Args:
            arcs_for_adding: Iterable of endpoint pairs or a string in the simple syntax.
            **attr: Additional attributes to apply.
        """
        if isinstance(arcs_for_adding, str):
            from knotpy.utils.parsing import parse_arcs

            arcs_for_adding = parse_arcs(arcs_for_adding)
            extra_vertices = {ep[0] for arc in arcs_for_adding for ep in arc if ep[0] not in self.nodes}
            self.add_vertices_from(extra_vertices)

        for arc in arcs_for_adding:
            self.set_arc(arc, **attr)

    def remove_arc(self, arc_for_removing: tuple[Endpoint | tuple[Hashable, int], Endpoint | tuple[Hashable, int]]) -> None:
        """Remove an arc by removing its two endpoints.

        Args:
            arc_for_removing: Tuple ``(v_endpoint, u_endpoint)``.
        """
        self.remove_endpoints_from(arc_for_removing)

    def remove_arcs_from(
        self, arcs_for_removing: Iterable[tuple[Endpoint | tuple[Hashable, int], Endpoint | tuple[Hashable, int]]]
    ) -> None:
        """Remove multiple arcs.

        Args:
            arcs_for_removing: Iterable of endpoint pairs to remove.
        """
        self.remove_endpoints_from(chain(*arcs_for_removing))

    # Hashing & identity

    def __hash__(self) -> int:
        """Compute a hash for the diagram.

        Notes:
            Hashing of mutable diagrams is risky. Consider hashing only frozen diagrams.

        Returns:
            int: Hash derived from framing and node order.
        """
        return hash(
            (
                self.framing,
                tuple(hash(self._nodes[node]) for node in sorted(self._nodes)),
            )
        )

    # Orientation / attributes

    @staticmethod
    def is_oriented() -> bool:
        """Return whether the diagram is oriented.

        Returns:
            bool: ``False`` for the base ``PlanarDiagram``.
        """
        return False

    @property
    def name(self) -> str:
        """Return the diagram name identifier.

        Returns:
            str: Diagram name (empty if not set).
        """
        return self.attr.get("name", "")

    @property
    def number_of_nodes(self) -> int:
        """Return the number of nodes.

        Returns:
            int: Number of nodes in the diagram.
        """
        return len(self._nodes)

    @property
    def number_of_crossings(self) -> int:
        """Return the number of classical crossings.

        Returns:
            int: Number of crossings.
        """
        return len(self.crossings)

    @property
    def number_of_vertices(self) -> int:
        """Return the number of vertices.

        Returns:
            int: Number of vertices.
        """
        return len(self.vertices)

    @property
    def number_of_virtual_crossings(self) -> int:
        """Return the number of virtual crossings.

        Returns:
            int: Number of virtual crossings.
        """
        return len(self.virtual_crossings)

    @property
    def number_of_endpoints(self) -> int:
        """Return the number of endpoints.

        Returns:
            int: Number of endpoints over all nodes.
        """
        return sum(len(node) for node in self.nodes.values())

    @property
    def number_of_arcs(self) -> int:
        """Return the number of arcs.

        Returns:
            int: Number of arcs (half the number of endpoints).
        """
        return self.number_of_endpoints // 2

    @property
    def framing(self) -> int | None:
        """Return the blackboard framing.

        Returns:
            Optional[int]: Framing number or ``None`` if unframed.
        """
        return self.attr.get("framing", None)

    def is_framed(self) -> bool:
        """Return whether the diagram is framed.

        Returns:
            bool: ``True`` if framed, otherwise ``False``.
        """
        return self.framing is not None

    @name.setter
    def name(self, s: str) -> None:
        """Set the diagram name identifier.

        Args:
            s: New diagram name.
        """
        self.attr["name"] = s

    @framing.setter
    def framing(self, framing: int | None) -> None:
        """Set the blackboard framing.

        Args:
            framing: Framing number or ``None`` to remove framing.

        Raises:
            RuntimeError: If the diagram is frozen.
        """
        if self.is_frozen():
            raise RuntimeError("Cannot set framing of frozen diagram.")
        self.attr["framing"] = framing

    def __str__(self) -> str:
        """Return a human-readable description of the diagram.

        Returns:
            str: Diagram description containing name, nodes, framing, attributes, and frozen state.
        """
        attrib_str = " ".join(
            [f"{key}={value}" for key, value in self.attr.items() if key not in {"name", "framing"}]
        )
        friendly_diag_name = "Oriented diagram" if isinstance(type(self), OrientedPlanarDiagram) else "Diagram"

        return "".join(
            [
                f"{friendly_diag_name} ",
                f"named {self.name} " if self.name else "",
                f"{self.nodes}" if self.nodes else "and no adjacencies",
                f" with framing {self.framing}" if self.framing is not None else "",
                f" ({attrib_str})" if attrib_str else "",
                " (frozen)" if self.is_frozen() else "",
            ]
        )

    def __repr__(self) -> str:
        """Return the ``repr`` string (delegates to ``__str__``).

        Returns:
            str: Representation string.
        """
        return self.__str__()


class OrientedPlanarDiagram(PlanarDiagram):
    """Planar diagram with orientation enabled."""

    @staticmethod
    def is_oriented() -> bool:
        """Return whether the diagram is oriented.

        Returns:
            bool: Always ``True`` for ``OrientedPlanarDiagram``.
        """
        return True


def planar_diagram_from_data(incoming_data: Any, create_using: type[PlanarDiagram] | PlanarDiagram | None) -> PlanarDiagram:
    """Generate a planar diagram from input data.

    If a string is provided, this attempts to parse it using knot-name/PD-table logic.
    If a type is provided, a new instance is created; if an instance is provided, it is populated.

    Args:
        incoming_data: Notation (e.g., name, PD) or a ``PlanarDiagram`` instance; use ``None`` for empty.
        create_using: A diagram subclass/type to construct, or an existing instance to populate.
            If ``None``, a new ``PlanarDiagram`` is created.

    Returns:
        PlanarDiagram: Diagram populated from ``incoming_data``.

    Raises:
        TypeError: If ``create_using`` is neither a valid diagram type nor a diagram instance.
        NotImplementedError: If constructing from a non-planar structure is attempted.
    """
    from knotpy.tables.name import diagram_from_name

    # If a string, try to resolve (knot name, PD notation, …)
    if isinstance(incoming_data, str):
        try:
            incoming_data = diagram_from_name(incoming_data)
        except ValueError:
            pass

    # Normalize target instance
    if isinstance(create_using, type):
        create_using = create_using()
    elif create_using is None:
        create_using = PlanarDiagram()

    if not isinstance(create_using, PlanarDiagram):
        raise TypeError("create_using is not a valid planar diagram type or instance")

    # Populate target
    create_using.clear()
    if isinstance(incoming_data, PlanarDiagram):
        # TODO: if input was a knot name (e.g., '3_1'), data is copied twice (via diagram_from_name and here).

        # Copy attributes
        create_using.attr.update(incoming_data.attr)

        # Copy nodes
        for node in incoming_data.nodes:
            node_instance = incoming_data.nodes[node]
            create_using.add_node(
                node_for_adding=node,
                create_using=type(node_instance),
                degree=len(node_instance),
                **node_instance.attr,
            )

        # Copy endpoints
        for ep in incoming_data.endpoints:
            adj_ep = incoming_data.twin(ep)
            adj_ep_type = type(adj_ep)

            # If target is unoriented, coerce oriented endpoints to plain Endpoint
            if type(create_using) is PlanarDiagram and adj_ep_type is not Endpoint:
                adj_ep_type = Endpoint

            create_using.set_endpoint(
                endpoint_for_setting=ep,
                adjacent_endpoint=(adj_ep.node, adj_ep.position),
                create_using=adj_ep_type,
                **adj_ep.attr,
            )

    elif incoming_data is None:
        # Empty diagram
        pass
    else:
        raise NotImplementedError("constructing planar diagrams from non-planar diagrams not implemented")

    return create_using

#: Union of knot diagram types used across KnotPy.
Diagram = PlanarDiagram | OrientedPlanarDiagram

#: Common collection types of diagrams.
DiagramCollection = list[Diagram] | set[Diagram] | tuple[Diagram, ...]
UnorientedDiagramCollection = list[PlanarDiagram] | set[PlanarDiagram] | tuple[PlanarDiagram, ...]

if __name__ == "__main__":
    pass

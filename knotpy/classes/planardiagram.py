from functools import cached_property
from itertools import chain
from string import ascii_letters

from knotpy.utils.dict_utils import compare_dicts
from knotpy.utils.decorators import total_ordering_from_compare
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node import Node, Crossing, Vertex, VirtualCrossing
from knotpy.classes.views import NodeView, EndpointView, ArcView, FaceView, FilteredNodeView

from knotpy.classes._abstractdiagram import _CrossingDiagram, _VertexDiagram, _VirtualCrossingDiagram

__all__ = ['PlanarDiagram', '_NodeCachedPropertyResetter', 'OrientedPlanarDiagram']
__version__ = '0.1.1'
__author__ = 'Boštjan Gabrovšek'


class _NodeCachedPropertyResetter:
    """
    Data Descriptor for resetting cached properties related to node types in planar diagrams.
    For info on Data Descriptors see https://docs.python.org/3/howto/descriptor.html.

    This class manages cached properties in a `PlanarDiagram` when nodes are modified.
    It ensures that derived node-type views (e.g., crossings, vertices) are reset when
    the `_nodes` attribute is updated.

    :param _node_type_property_names: Mapping of node types to their corresponding cached property names.
    :type _node_type_property_names: dict
    """

    def __init__(self, **_node_type_property_names):
        """
        Initialize the property resetter with node-type-specific cached properties.

        :param _node_type_property_names: Dictionary mapping node types to their cached property names.
        :type _node_type_property_names: dict
        """
        self._node_type_property_names = _node_type_property_names

    def add_property_name(self, **_node_type_property_names):
        """
        Add additional node-type-specific property names to be reset.

        :param _node_type_property_names: Additional mappings of node types to property names.
        :type _node_type_property_names: dict
        """
        self._node_type_property_names.update(_node_type_property_names)


    def __set__(self, obj, value):
        """
        Reset cached properties when `_nodes` is modified.
        The instance variable "node" has been changed, reset all cached properties. The class view instances "nodes",
        "endpoints", and "arcs" are common for all planar diagrams, additional class view instances are stored in
        _node_type_property_names.

        :param obj: The instance of `PlanarDiagram` where the `_nodes` attribute is modified.
        :type obj: PlanarDiagram
        :param value: The new value for `_nodes`.
        :type value: dict
        """

        od = obj.__dict__
        od["_nodes"] = value
        if "nodes" in od:
            del od["nodes"]
        if "endpoints" in od:
            del od["endpoints"]
        if "arcs" in od:
            del od["arcs"]
        if "faces" in od:
            del od["faces"]
        for node_type in self._node_type_property_names:
            if self._node_type_property_names[node_type] in od:
                del od[self._node_type_property_names[node_type]]


@total_ordering_from_compare
class PlanarDiagram(_CrossingDiagram, _VertexDiagram, _VirtualCrossingDiagram):
    """
    A class for storing a planar diagram, representing spatial/embedded/knotted graphs, knots, and related structures.

    It provides fundamental operations for managing nodes (vertices), endpoints, arcs, and faces in a planar diagram.

    **Structure of a PlanarDiagram:**
      - The diagram itself, with optional attributes.
      - **Nodes (vertices, crossings):** Hashable objects that represent singular points in the diagram. Nodes can have
      additional attributes (colors, weights, ...)
      - **Endpoints:** Tuples `(node, node_position)`, representing edges/arcs emanating from nodes. Each endpoint
      points to another `node` at position `node_position`. Endpoints can have additional attributes (colors, weights,
      ...)
      - **Arcs:** Tuples of endpoints representing edges in the diagram (computed on-the-fly from nodes)
      - **Faces (regions):** Represented as sequences of endpoints, forming enclosed areas (computed on-the-fly from
      nodes)

    **Terminology:**
      - **Crossings:** Nodes with degree 4, where odd endpoints (0, 2) are under-endpoints and even endpoints (1, 3)
      are over-endpoints in knot diagrams.
      - **Vertices:** Graph-theoretic nodes (that do not act as crossings).
      - **Virtual Crossings:** Special nodes used in virtual knot theory.

    This class maintains a cached property system to efficiently update derived node views when the diagram changes.
    """

    # Cache views of specific node types (vertices, crossings, virtual crossings)
    _nodes: dict = _NodeCachedPropertyResetter(
        Vertex="vertices",
        Crossing="crossings",
        VirtualCrossing="virtual_crossings",
    )

    def __init__(self,  incoming_diagram_data=None, **attr):
        """
        Initialize a planar diagram.

        If no data is provided, an empty diagram is created. Otherwise, the diagram is initialized using the provided
        data.

        :param incoming_diagram_data: Initial data to construct the diagram (currently not implemented).
        :type incoming_diagram_data: Optional[Any]
        :param attr: Additional attributes such as name, framing, etc.
        """

        super(_CrossingDiagram, self).__init__()

        if incoming_diagram_data is None:
            self._nodes = dict()  # Stores nodes and their adjacency information
            self.attr = dict()  # Stores diagram-level attributes (without a view)
        else:
            planar_diagram_from_data(incoming_data=incoming_diagram_data, create_using=self)

        self.attr.update(attr)

    def clear(self):
        """
        Remove all data from the diagram, resetting it to an empty state.
        """
        self._nodes = dict()
        self.attr = dict()

    def copy(self, copy_using=None, **attr):
        """
        Return a shallow copy of the diagram.

        :param copy_using: The class type of the new diagram (defaults to the same type as `self`).
        Serves for converting e.g. oriented to unoriented diagrams.
        :type copy_using: Optional[type]
        :return: A new instance of the planar diagram with the same structure and attributes (shallow copy).
        :rtype: PlanarDiagram
        """

        copy_using = copy_using or type(self)

        the_copy = planar_diagram_from_data(incoming_data=self, create_using=copy_using)
        the_copy.attr.update(attr)
        return the_copy

    # node-type views
    @cached_property
    def nodes(self):
        """Return a view of the diagram's nodes, providing adjacency information."""
        return NodeView(self._nodes)


    @cached_property
    def endpoints(self):
        """Return a view of the diagram's endpoints."""
        return EndpointView(self._nodes)

    @cached_property
    def arcs(self):
        """Return a view of the diagram's arcs, represented as pairs of endpoints."""
        return ArcView(self._nodes)

    @cached_property
    def faces(self):
        """Return a view of the diagram's faces (regions enclosed by arcs), which are given as tuples of endpoints."""
        return FaceView(self._nodes)

    def __len__(self):
        """Return the number of nodes in the diagram."""
        return len(self._nodes)

    def _compare(self, other, compare_attributes=True):
        """
        Compare this diagram with another diagram.

        Comparison is performed based on structural properties, node count, node
        ordering, and attribute values. The method returns an integer indicating
        whether the current diagram is greater than, less than, or equal to the
        other diagram in terms of these properties.

        Args:
            other (PlanarDiagram): The diagram to compare against.
            compare_attributes (Union[bool, list, set, tuple]): Specifies how the
                comparison of attributes is performed:
                - If `False`, all attributes are ignored during comparison.
                - If `True`, all attributes except the diagram's name are compared.
                - If a collection (list, set, or tuple), only the specified
                  attributes are compared.

        Returns:
            int: Returns `1` if the current diagram is greater than the other
            diagram, `-1` if it is less than, and `0` if the diagrams are equal.
        """

        # compare type
        if type(self) is not type(other):
            return TypeError(f"Cannot compare {type(self)} with {type(other)}.")

        # compare number of nodes
        if (s_nn := len(self._nodes)) != (o_nn := len(other._nodes)):
            return -1 if s_nn < o_nn else 1

        # compare number of endpoints
        if (s_ep := sum(len(self._nodes[node]._inc) for node in self._nodes)) != (o_ep := sum(len(other._nodes[node]._inc) for node in other._nodes)):
            return -1 if s_ep < o_ep else 1

        # compare degree sequence
        deg_seq_self = sorted([len(self._nodes[node]) for node in self._nodes])
        deg_seq_other = sorted([len(self._nodes[node]) for node in self._nodes])
        if deg_seq_self != deg_seq_other:
            return -1 if deg_seq_self < deg_seq_other else 1


        # compare nodes themselves
        self_nodes_sorted = sorted(self._nodes)
        other_nodes_sorted = sorted(other._nodes)

        if self_nodes_sorted != other_nodes_sorted:
            return -1 if self_nodes_sorted < other_nodes_sorted else 1

        for node in self_nodes_sorted:
            if cmp := self._nodes[node]._compare(other._nodes[node], compare_attributes=compare_attributes):
                return cmp

        # self_fr = 0 if self.framing is None else self.framing  # convert None to 0
        # other_fr = 0 if other.framing is None else other.framing  # convert None to 0

        if (self_fr := self.framing or 0) != (other_fr := other.framing or 0):
            return 1 if self_fr > other_fr else -1


        # TODO: exclude "_" keys in nodes and endpoints also
        exclude_keys = ({"name", "framing"} |
                        {a for a in self.attr if isinstance(a, str) and a[0] == "_"} |
                        {a for a in other.attr if isinstance(a, str) and a[0] == "_"})

        if compare_attributes is True:
            return compare_dicts(self.attr, other.attr, exclude_keys=exclude_keys)
        elif type(compare_attributes) in (list, set, tuple):
            return compare_dicts(self.attr, other.attr, exclude_keys=exclude_keys, include_only_keys=compare_attributes)

        return 0


    def __getitem__(self, item):
        """ TODO: get item by description"""
        raise NotImplementedError()

    # node operations

    def add_node(self, node_for_adding, create_using: type, degree=None, **attr):
        """
        Add a node to the diagram.

        :param node_for_adding: A hashable object representing the node.
        :type node_for_adding: Hashable
        :param create_using: The node type (e.g., `Vertex`, `Crossing`).
        :type create_using: type
        :param degree: The degree of the node (optional).
        :type degree: Optional[int]
        :param attr: Additional attributes to store for the node.
        """
        #print(node_for_adding)

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
            raise NotImplementedError("Node type change not implemented")
            # take care of memory leaks

        self._nodes[node].attr.update(attr)

    def add_nodes_from(self, nodes_for_adding, create_using=None, **attr):
        """
        Add or update a list of nodes to the diagram.

        :param nodes_for_adding: A list/set/tuple of hashable objects representing the nodes.
        :type nodes_for_adding: List[Hashable]
        :param create_using: The node type (e.g., `Vertex`, `Crossing`).
        :type create_using: type
        :param attr: Additional attributes to store for the node.
        """
        if isinstance(nodes_for_adding, dict):
            for node, inst in nodes_for_adding.items():
                self.add_node(node_for_adding=node, create_using=type(inst), degree=len(inst), **(inst.attr | attr))
        else:
            for node in nodes_for_adding:
                if "degree" in attr:
                    self.add_node(node_for_adding=node, create_using=create_using, **attr)
                else:
                    self.add_node(node_for_adding=node, create_using=create_using, degree=None, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        self.add_nodes_from(nodes_for_adding=crossings_for_adding, create_using=Crossing, **attr)

    def add_vertex(self, vertex_for_adding, degree=None, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=vertex_for_adding, create_using=Vertex, degree=degree, **attr)


    def permute_node(self, node, permutation):
        """Permute the endpoints of the node of knot k. For example, if p = {0: 0, 1: 2, 2: 3, 3: 1} (or p = [0,2,2,1]),
        and if node has endpoints [a, b, c, d] (ccw) then the new endpoints will be [a, d, b, c].
        :param node: node of which we permute its endpoints
        :param permutation: permutation given as a dict or list/tuple
        :return:
        TODO: are there problems regarding endpoint attributes?
        TODO: check if it works for loops (probably does not)
        """

        # convert list/tuple permutation to dict
        if isinstance(permutation, list) or isinstance(permutation, tuple):
            permutation = dict(enumerate(permutation))
        old_adj_node_data = list(self.nodes[node])  # save old node ccw sequence since it can override
        old_node_data = list(self.endpoints[node])
        for ep, adj_ep in zip(old_node_data, old_adj_node_data):
            self.set_endpoint(
                endpoint_for_setting=adj_ep,
                adjacent_endpoint=(ep.node, permutation[ep.position]),
                create_using=type(ep),
                **ep.attr
            )
            #print(ep,adj_ep)
            self._nodes[ep.node][permutation[ep.position]] = adj_ep

    # def rename_nodes(self, mapping_dict):
    #     # TODO: should this be an outside method?
    #     mapping_dict = identitydict(mapping_dict)
    #     self._nodes = dict()
    #     self._nodes.update((mapping_dict[node], value) for node, value in self._nodes.items())
    #     for node in self._nodes:
    #         for adj_node in self._nodes[node]:
    #             print(adj_node)

    def convert_node(self, node_for_converting, node_type: type):
        """ Convert node type, e.g. from vertex to crossing"""
        node_inst = self._nodes[node_for_converting]
        if type(node_inst) is not node_type:
            self._nodes[node_for_converting] = node_type(
                incoming_node_data=node_inst._inc,
                degree=len(node_inst),
                *node_inst.attr)

    def convert_nodes(self, node_for_converting, node_type: type):
        for node in node_for_converting:
            self.convert_node(node, node_type)

    def remove_node(self, node_for_removing, remove_incident_endpoints=True):
        """Remove the node.
        :param node_for_removing:
        :param remove_incident_endpoints: use with care, if False, it breaks the planar structure
        :return: planar diagram without node
        """
        node = node_for_removing
        if remove_incident_endpoints:
            self.remove_endpoints_from(self._nodes[node])
        del self._nodes[node]
        return self

    def remove_nodes_from(self, nodes_for_removal, remove_incident_endpoints=True):
        for node in nodes_for_removal:
            self.remove_node(node, remove_incident_endpoints)

    def degree(self, node):
        return len(self._nodes[node])

    def relabel_nodes(self, mapping):
        """Relabels the nodes, can be a partial map"""
        # TODO: is this the same as rename_nodes?
        self._nodes = {
            mapping.get(node, node): node_inst
            for node, node_inst in self._nodes.items()
        }
        for ep in self.endpoints:
            ep.node = mapping.get(ep.node, ep.node)

    # endpoint operations

    def set_endpoint(self, endpoint_for_setting, adjacent_endpoint, create_using=Endpoint, **attr):
        """Set the endpoint to the adjacent endpoint and update the endpoint attributes.
        
        :param endpoint_for_setting: Endpoint object or tuple (crossing name, position)
        :param adjacent_endpoint: overwrite the endpoint with adjacent_endpoint (Endpoint object or tuple
            (crossing name, position))
        :param create_using: if the type is not Endpoint (or IngoingEndpoint or OutgoingEndpoint), the class should be
            given, be default Endpoint is assumed if endpoint_for_setting is given as a tuple. If an Endpoint instance is
            given instead of a class, the instance type is used with attributes copied.
        :param attr: additional attributes of the (adjacent) endpoint
        :return: None
        """

        # if create_using is default Endpoint and adjacent endpoint is Oriented Endpoint, convert create using to oriented type
        if (type(adjacent_endpoint) is OutgoingEndpoint or type(adjacent_endpoint) is IngoingEndpoint) and create_using is Endpoint:
            create_using = type(adjacent_endpoint)

        if not isinstance(create_using, type):
            raise TypeError("Creating endpoint with create_using instance not yet supported.")

        if self.is_oriented() and not create_using.is_oriented():
            raise ValueError(f"Cannot add an unoriented endpoint ({create_using.__name__}) to an oriented diagram ({type(self).__name__})")
        if not self.is_oriented() and create_using.is_oriented():
            raise ValueError(f"Cannot add an oriented ({create_using.__name__}) endpoint to an unoriented diagram ({type(self).__name__})")

        node, node_pos = endpoint_for_setting

        # we would like a tuple
        if isinstance(endpoint_for_setting, Endpoint):
            endpoint_for_setting = list(endpoint_for_setting)
        if isinstance(adjacent_endpoint, Endpoint):
            attr = adjacent_endpoint.attr | attr  # join attributes
            adjacent_endpoint = list(adjacent_endpoint)

        adjacent_endpoint = create_using(*adjacent_endpoint, **attr)

        # insert missing positions missing in the node
        for i in range(node_pos + 1 - len(self._nodes[node])):
            self._nodes[node].append(Node)

        self._nodes[node][node_pos] = adjacent_endpoint

    # def insert_endpoint(self, endpoint_for_setting, adjacent_endpoint, create_using=Endpoint, **attr):
    #     """
    #
    #     :param endpoint_for_setting:
    #     :param adjacent_endpoint:
    #     :param create_using:
    #     :param attr:
    #     :return:
    #     """
    #
    #     ep = endpoint_for_setting
    #     if isinstance(ep, Endpoint):
    #         new_ep = type(ep)(ep.node, self.degree(ep.node))
    #         node, old_pos, new_pos = ep.node, ep.position, new_ep.position
    #     else:
    #         new_ep = (ep[0], self.degree(ep[0]))
    #         node, old_pos, new_pos = ep[0], ep[1], new_ep[1]
    #
    #     self.set_endpoint(ep, adjacent_endpoint, create_using=create_using, **attr)
    #     perm = {i: (i if i < old_pos else i + 1) for i in range(self.degree(node) - 1)}
    #     perm[self.degree(node) - 1] = old_pos
    #     self.permute_node(node, perm)



    def twin(self, endpoint) -> Endpoint:
        """Return the opposite endpoint (twin) of an endpoint. Both endpoints form an arc.
        
        :param endpoint: Endpoint instance or pair (node, position)
        :return: twin endpoint instance
        """
        node, position = endpoint
        return self._nodes[node][position]

    def endpoint_from_pair(self, endpoint_pair):
        """Returns the Endpoint instance of the pair (node, position).
        
        :param endpoint_pair: a pair (node, position)
        :return: Endpoint instance
        """

        if isinstance(endpoint_pair, Endpoint):
            return endpoint_pair

        # Is endpoint given by description?
        if isinstance(endpoint_pair[1], str):
            node, desc = endpoint_pair
            if node not in self.crossings:
                raise ValueError(f"Cannot get a descriptive endpoint from a node that is not a crossings: {node}")
            desc = desc.strip().lower()
            if desc in ("oi", "io"", over ingoing","ingoing over"):
                return self.twin(self.twin((node, 1))) if isinstance(self.nodes[node][1], OutgoingEndpoint) else self.twin(self.twin((node, 3)))
            elif desc in ("oo", "over outgoing", "outgoing over"):
                return self.twin(self.twin((node, 1))) if isinstance(self.nodes[node][1], IngoingEndpoint) else self.twin(self.twin((node, 3)))
            elif desc in ("ui", "iu", "under ingoing", "ingoing under"):
                return self.twin(self.twin((node, 0))) if isinstance(self.nodes[node][0], OutgoingEndpoint) else self.twin(self.twin((node, 1)))
            elif desc in ("uo", "uo", "under outgoing", "outgoing under"):
                return self.twin(self.twin((node, 0))) if isinstance(self.nodes[node][0], IngoingEndpoint) else self.twin(self.twin((node, 1)))
            else:
                raise ValueError(f"Unknown description {desc} for endpoint {endpoint_pair}")
        # the endpoint instance is the twin of the twin
        return self.twin(self.twin(endpoint_pair))  # TODO: can this be faster?

    def remove_endpoint(self, endpoint_for_removal):
        _debug = False

        if _debug:
            print("  Removing", endpoint_for_removal, "from", self._nodes)

        node, pos = endpoint_for_removal
        del self._nodes[node][pos]

        # adjust change of position for all adjacent endpoints
        for adj_node, adj_pos in self._nodes[node][pos:]:

            adj_node_inst = self._nodes[adj_node]  # node instance

            # Adjust position if the position has just been removed (this happens in loops and kinks).
            if adj_node == node and adj_pos >= pos:
                adj_pos -= 1

            # if adj_node != node:
            # There is no loop or kink.
            adj_node_inst[adj_pos] = Endpoint(
                adj_node_inst[adj_pos].node,
                adj_node_inst[adj_pos].position - 1,
                **adj_node_inst[adj_pos].attr
            )
            # else:
                # # There is a loop or kink
                # if adj_pos > pos:
                #     adj_node_inst[a]


    def remove_endpoints_from(self, endpoints_for_removal):

        # convert to Endpoint instances if they are tuples
        endpoints_for_removal = [ep if isinstance(ep, Endpoint) else self.endpoint_from_pair(ep) for ep in endpoints_for_removal]

        endpoints_for_removal.sort(key=lambda _: _.position)  # Start removing from the back

        #print("endpoints", endpoints_for_removal)

        while endpoints_for_removal:
            ep = endpoints_for_removal.pop()

            #print("removing endpoint", ep, "remaining:", endpoints_for_removal)

            #print("  ..", self)

            self.remove_endpoint(ep)

            #print(" ...", self)

            # adjust change of position for the rest of the endpoints in the list
            for i, _ in enumerate(endpoints_for_removal):
                if _.node == ep.node and _.position > ep.position:
                    endpoints_for_removal[i] = type(_)(_.node, _.position - 1)  # the attribute is not needed TODO: why not?

        # # convert to Endpoint instances if they are tuples
        # endpoints_for_removal = [ep if isinstance(ep, Endpoint) else self.endpoint_from_pair(ep) for ep in endpoints_for_removal]
        #
        # endpoints = sorted(endpoints_for_removal, key=lambda _: -_.position)  # start removing from the back
        #
        # print("endpoints", endpoints)
        #
        # for i, ep in enumerate(endpoints):
        #     print("endpoints", endpoints)
        #
        #     self.remove_endpoint(ep)
        #     print(" ...", self)
        #
        #     # adjust change of position for the rest of the endpoints in the list
        #     for j in range(i + 1, len(endpoints)):
        #         if endpoints[j].node == ep.node and endpoints[j].position > ep.position:
        #             endpoints[j] = (endpoints[j].node, endpoints[j].position - 1)  # the attribute is not needed


    # arc operations

    def set_arc(self, arc_for_setting, **attr):
        """Set the arc (v_endpoint, u_endpoint), which equals setting the two endpoints adj(u_endpoint) = v_endpoint
        and vice-versa."""
        v_endpoint, u_endpoint = arc_for_setting
        self.set_endpoint(v_endpoint, u_endpoint, **attr)
        self.set_endpoint(u_endpoint, v_endpoint, **attr)

    def set_arcs_from(self, arcs_for_adding, **attr):
        """Set the list of arcs.
        Can also add arcs as a string, e.g. "a0b1,a1b0" in this case also vertices are added if the nodes do not yet exist.
        
        :param arcs_for_adding: a iterable of tuples (v_endpoint, u_endpoint) or a string like "a1b4,c2d3".
        :return: None
        """

        # Parse string if we are adding simple arcs (e.g., "a1b4,c2d3").
        if isinstance(arcs_for_adding, str):
            from knotpy.utils.parsing import parse_arcs
            arcs_for_adding = parse_arcs(arcs_for_adding)
            extra_vertices = set(ep[0] for arc in arcs_for_adding for ep in arc if ep[0] not in self.nodes)
            self.add_vertices_from(extra_vertices)

        for arc in arcs_for_adding:
            self.set_arc(arc, **attr)



    def remove_arc(self, arc_for_removing):
        self.remove_endpoints_from(arc_for_removing)

    def remove_arcs_from(self, arcs_for_removing):
        self.remove_endpoints_from(chain(*arcs_for_removing))

    def __hash__(self):
        """Unsafe hashing"""
        # TODO: sort by hash if keys are not comparable
        # TODO: if knot has attibute "framed = False", then hash excludes the framedness
        # print("hash",
        #       (
        #           self.framing,
        #           tuple(hash(self._nodes[node]) for node in sorted(self._nodes))  # nodes need to be sorted
        #       )
        #
        #       )

        return hash(
            (
                self.framing,
                tuple(hash(self._nodes[node]) for node in sorted(self._nodes))  # nodes need to be sorted
            )
        )

    @staticmethod
    def is_oriented():
        return False

    @property
    def name(self):
        """Name identifier of planar diagram."""
        return self.attr.get("name", "")

    @property
    def number_of_nodes(self):
        return len(self._nodes)

    @property
    def number_of_crossings(self):
        return len(self.crossings)

    @property
    def number_of_vertices(self):
        return len(self.vertices)

    @property
    def number_of_virtual_crossings(self):
        return len(self.virtual_crossings)

    @property
    def number_of_endpoints(self):
        return sum(len(node) for node in self.nodes.values())

    @property
    def number_of_arcs(self):
        return self.number_of_endpoints // 2

    @property
    def framing(self):
        """Blackboard framing number of planar diagram."""
        return self.attr.get("framing", None)

    def is_framed(self):
        return self.framing is not None

    @name.setter
    def name(self, s):
        """Set planar diagram name identifier."""
        # we can rename frozen objects, since the name does not influence the hash/compare
        self.attr["name"] = s

    @framing.setter
    def framing(self, framing):
        """Set (blackboard) framing of planar diagram."""
        if self.is_frozen():
            raise RuntimeError("Cannot set framing of frozen diagram.")
        self.attr["framing"] = framing

    def __str__(self):
        attrib_str = " ".join([f"{key}={value}" for key, value in self.attr.items() if key != "name" and key != "framing"])
        friendly_diag_name = "Oriented diagram" if isinstance(type(self), OrientedPlanarDiagram) else "Diagram"

        return "".join(
            [
                f"{friendly_diag_name} ",
                f"named {self.name} " if self.name else "",
                f"{self.nodes}" if self.nodes else f"and no adjacencies",
                f" with framing {self.framing}" if self.framing is not None else "",
                f" ({attrib_str})" if attrib_str else "",
                f" (frozen)" if self.is_frozen() else ""
            ]
        )

    def __repr__(self):
        return self.__str__()

class OrientedPlanarDiagram(PlanarDiagram):

    @staticmethod
    def is_oriented():
        return True



def planar_diagram_from_data(incoming_data, create_using) -> PlanarDiagram:
    """ Generate a planar diagram, from (incoming) data.
    :param incoming_data: notation or other PlanarDiagram instance
    :param create_using: type or instance
    :return: planar diagram with data
    """
    from knotpy.catalog.knot_tables import diagram_from_name

    if isinstance(incoming_data, str):
        try:
            # TODO: convert to create_using (e.g. oriented)
            k = diagram_from_name(incoming_data)
            return planar_diagram_from_data(k, create_using=create_using)  # copy k into create_using
        except ValueError:
            # knot not found
            pass

    # initiate the diagram with create_using
    if isinstance(create_using, type):
        k = create_using()
    elif isinstance(create_using, PlanarDiagram):
        k = create_using
    else:
        raise TypeError("create_using is not a valid KnotPy planar diagram type or instance")

    k.clear()

    if isinstance(incoming_data, PlanarDiagram):
        # copy data from incoming_data instance

        k.attr.update(incoming_data.attr)

        # copy nodes
        for node in incoming_data.nodes:
            node_instance = incoming_data.nodes[node]
            k.add_node(node_for_adding=node, create_using=type(node_instance),
                       degree=len(node_instance), **node_instance.attr)

        # copy endpoints
        for ep in incoming_data.endpoints:
            adj_ep = incoming_data.twin(ep)
            adj_ep_type = type(adj_ep)

            # create unoriented endpoint if diagram is unoriented
            if type(k) is PlanarDiagram and adj_ep_type is not Endpoint:
                adj_ep_type = Endpoint

            k.set_endpoint(endpoint_for_setting=ep, adjacent_endpoint=(adj_ep.node, adj_ep.position),
                           create_using=adj_ep_type, **adj_ep.attr)

    elif incoming_data is None:
        # create empty diagram
        pass

    else:
        raise NotImplementedError("constructing planar diagrams from non-planar diagrams not implemented")

    return k

if __name__ == "__main__":

    k = PlanarDiagram()
    k.add_vertices_from("bc")
    k.set_arc((("b",0),("c",1)))
    k.set_arc((("b",3),("c",0)))
    k.set_arc((("b",1),("b",2)))
    print(k)

    k.remove_arc((("b",0),("c", 1)))

    print(k)

    exit()

    d = PlanarDiagram()
    d.add_node("a", create_using=Vertex)
    d.add_crossing("olala")
    d._nodes = dict()
    print(d)
    pass
from functools import cached_property
from itertools import chain

from knotpy.utils.dict_utils import compare_dicts
from knotpy.utils.decorators import total_ordering_from_compare
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.node import Node, Crossing, Vertex, Bond, VirtualCrossing, Terminal
from knotpy.classes.views import NodeView, EndpointView, ArcView, FaceView, FilteredNodeView

from knotpy.classes._abstractdiagram import (_NodeDiagram, _CrossingDiagram, _VertexDiagram,
                                             _TerminalDiagram, _BondDiagram, _VirtualCrossingDiagram)

import warnings

__all__ = ['PlanarDiagram', '_NodeCachedPropertyResetter', 'OrientedPlanarDiagram']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _NodeCachedPropertyResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""

    def __init__(self, **_node_type_property_names):
        self._node_type_property_names = _node_type_property_names

    def add_property_name(self, **_node_type_property_names):
        self._node_type_property_names.update(_node_type_property_names)


    def __set__(self, obj, value):
        """The instance variable "node" has been changed, reset all cached properties. The class view instances "nodes",
        "endpoints", and "arcs" are common for all planar diagrams, additional class view instances are stored in
        _node_type_property_names."""

        #print(self._node_type_property_names)
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
class PlanarDiagram(_CrossingDiagram, _VertexDiagram, _TerminalDiagram, _BondDiagram, _VirtualCrossingDiagram):
    """The PlanarDiagram class provides the basic abstract class for all planar objects (planar graph, knots, knotted
    graphs, ...).  It is intended to be used only as the parent class for Knot, PlanarGraph, etc.
        
    A PlanarDiagram class consists of:
    - the diagram class with optional attributes,
    - nodes (vertices), that are any hashable objects with optional attributes,
    - endpoints, that represent part of the edge/arc emanating from the node and is a tuple (node, node_position), with optional attributes

    In addition, we use the following terminology:
    - arcs are tuples of endpoints,
    - regions are the faces of the planar graph and are represented as a sequence of endpoints.
    """

    # cache special node types
    _nodes: dict = _NodeCachedPropertyResetter(
        Vertex="vertices",
        Crossing="crossings",
        Terminal="terminals",
        VirtualCrossing="virtual_crossings",
        Bond="bonds"
    )

    def __init__(self,  incoming_diagram_data=None, **attr):
        """Initialize a planar diagram.
        :param incoming_diagram_data: not implemented
        :param attr: graph attributes (name, framing, ...)
        """

        super(_CrossingDiagram, self).__init__()

        if incoming_diagram_data is None:
            self._nodes = dict()
            self.attr = dict()  # store graph attributes (without a View)
        else:
            planar_diagram_from_data(incoming_data=incoming_diagram_data, create_using=self)

        self.attr.update(attr)

    def clear(self):
        """Remove/clear all diagram data."""
        self._nodes = dict()
        self.attr = dict()

    def copy(self, copy_using=None):
        """
        Return shallow copy of the diagram.
        :param copy_using: the planar diagram type of the new diagram
        :return: shallow copy
        """

        copy_using = copy_using or type(self)

        # print(".... COPY")
        #
        return planar_diagram_from_data(incoming_data=self, create_using=copy_using)

    # node-type views
    @cached_property
    def nodes(self):
        """Node object holding the adjacencies of each node."""
        return NodeView(self._nodes)


    @cached_property
    def endpoints(self):
        """Node object holding the adjacencies of each node."""
        return EndpointView(self._nodes)

    @cached_property
    def arcs(self):
        """Node object holding the adjacencies of each node."""
        return ArcView(self._nodes)

    @cached_property
    def faces(self):
        """Node object holding the adjacencies of each node."""
        return FaceView(self._nodes)

    def __len__(self):
        """Return the number of nodes in the knot."""
        return len(self._nodes)

    def compare(self, other, compare_attributes=True):
        """Compare the diagram with other.
        :param other: planar diagram
        :param compare_attributes: if False, ignore all attributes when comparing, if True, compare all attributes
        (except diagram name), if list, set, or tuple, compare only those attributes.
        :return: 1 if self > other, -1 if self < other, and 0 if self = other.
        """

        # compare type
        if type(self) is not type(other):
            return TypeError(f"Cannot compare {type(self)} with {type(other)}.")

        # compare nodes
        if self.number_of_nodes != other.number_of_nodes:
            return (self.number_of_nodes > other.number_of_nodes) * 2 - 1

        self_nodes_sorted = sorted(self._nodes)
        other_nodes_sorted = sorted(other._nodes)

        if self_nodes_sorted != other_nodes_sorted:
            return (self_nodes_sorted > other_nodes_sorted) * 2 - 1

        # if set(self._nodes) != set(other._nodes):
        #     return (sorted(self._nodes) > sorted(other._nodes)) * 2 - 1

        for node in self_nodes_sorted:
            if cmp := self._nodes[node].compare(other._nodes[node], compare_attributes=compare_attributes):
                return cmp

        # for this_node, that_node in zip(self._nodes.values(), other._nodes.values()):
        #     if cmp := this_node.compare(that_node, compare_attributes=compare_attributes):
        #        return cmp

        if self.framing != other.framing:
            return (self.framing > other.framing) * 2 - 1

        if compare_attributes is True:
            return compare_dicts(self.attr, other.attr, exclude_keys=["name", "framing"])
        elif type(compare_attributes) in (list, set, tuple):
            return compare_dicts(self.attr, other.attr, exclude_keys=["name", "framing"], include_only_keys=compare_attributes)

        return 0


    def __getitem__(self, item):
        """ TODO: get item by description"""

        raise NotImplementedError()

    # node operations

    def add_node(self, node_for_adding, create_using: type, degree=None, **attr):
        """Add a node of type create_using with optional degree and attributes.

        :param node_for_adding: any hashable object
        :param create_using: the node type
        :param degree: optional degree of the node
        :param attr:
        :return: None
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
            raise NotImplementedError("Node type change not implemented")
            # take care of memory leaks

        self._nodes[node].attr.update(attr)

    def add_nodes_from(self, nodes_for_adding, create_using=None, **attr):
        """Add or update a bunch (iterable) of nodes and update attributes.
        
        :param nodes_for_adding: an iterable of nodes, which can be any hashable object. If a dictionary of is given,
            where the values are Node classes,  the newly added nodes will inherit the degree and attributes of nodes in
            the dict.
        :param create_using: if nodes_for_adding does not consist of a dictionary of Node instances, the node type must
            be given in this parameter (e.g. Vertex, Crossing,...)
        :param attr: the nodes attribute will be updated with these values.
        :return: None
        """
        if isinstance(nodes_for_adding, dict):
            for node, inst in nodes_for_adding.items():
                self.add_node(node_for_adding=node, create_using=type(inst), degree=len(inst), **(inst.attr | attr))
        else:
            for node in nodes_for_adding:
                self.add_node(node_for_adding=node, create_using=create_using, degree=None, **attr)

    # def add_crossing(self, crossing_for_adding, **attr):
    #     """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
    #     self.add_node(node_for_adding=crossing_for_adding, create_using=Crossing, degree=4, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        self.add_nodes_from(nodes_for_adding=crossings_for_adding, create_using=Crossing, **attr)

    def add_vertex(self, vertex_for_adding, degree=None, **attr):
        """Add or update a crossing and update the crossing attributes. A crossing can be any hashable object."""
        self.add_node(node_for_adding=vertex_for_adding, create_using=Vertex, degree=degree, **attr)

    def add_crossings_from(self, crossings_for_adding, **attr):
        """Add or update a bunch (iterable) of crossings and update the crossings attributes. Crossings can be any
        hashable objects."""
        self.add_nodes_from(nodes_for_adding=crossings_for_adding, create_using=Crossing, **attr)


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
                create_using=ep,
                **ep.attr
            )
            print(ep,adj_ep)
            self._nodes[ep.node][permutation[ep.position]] = adj_ep

    def rename_nodes(self, mapping_dict):
        # TODO: should this be an outside method?
        mapping_dict = identitydict(mapping_dict)
        self._nodes = dict()
        self._nodes.update((mapping_dict[node], value) for node, value in self._nodes.items())
        for node in self._nodes:
            for adj_node in self._nodes[node]:
                print(adj_node)

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

    def remove_nodes_from(self, nodes_for_removal, remove_incident_endpoints=True):
        for node in nodes_for_removal:
            self.remove_node(node, remove_incident_endpoints)

    def degree(self, node):
        return len(self._nodes[node])

    def relabel_nodes(self, mapping):
        """Relabels the nodes, can be a partial map"""
        # TODO: is this the same as rename_nodes?
        self._nodes = {
            mapping.get(node_key, node_key): node_inst
            for node_key, node_inst in self._nodes.items()
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
        #print(create_using)


        if create_using is not None and not isinstance(create_using, type):
            raise TypeError("Creating endpoint with create_using instance not yet supported.")

        create_using_type = create_using if isinstance(create_using, type) else type(create_using)

        if self.is_oriented() and (create_using_type is not IngoingEndpoint and create_using_type is not OutgoingEndpoint):
            raise ValueError("Cannot add unoriented endpoint to an oriented diagram")

        if not self.is_oriented() and create_using_type is not Endpoint:
            raise ValueError(f"Cannot add oriented endpoint {create_using} to an unoriented diagram")

        node, node_pos = endpoint_for_setting

        # TODO: avoid else
        # adjacent endpoint

        if isinstance(adjacent_endpoint, Endpoint):
            #create_using = create_using or type(adjacent_endpoint)  # todo: why adjacent? should it be default Endpoint?
            if not isinstance(create_using, type):
                create_using = type(create_using)  # todo: make nicer
            adjacent_endpoint = create_using(*adjacent_endpoint, **adjacent_endpoint.attr)
            adjacent_endpoint.attr.update(attr)
        elif isinstance(create_using, Endpoint):
            # if create_using is an instance, create new instance from its class and copy the attributes and override
            # the new attributes
            adjacent_endpoint = type(create_using)(*adjacent_endpoint, **(create_using.attr | attr))

        else:
            create_using = create_using or Endpoint
            adjacent_endpoint = create_using(*adjacent_endpoint, **attr)

        #print("a", self._nodes[node])

        # insert missing positions missing in the node
        for i in range(node_pos + 1 - len(self._nodes[node])):
            self._nodes[node].append(Node)

        #self._nodes[node] += [None] * (node_pos + 1 - len(self._nodes[node]))
        #print("b", self._nodes[node])



        #int(self._nodes)

        #print("set endpoint", "node", node, "pos", node_pos, "adj", adjacent_endpoint)
        #print("node", node,self._nodes[node])
        self._nodes[node][node_pos] = adjacent_endpoint


        #print(self._nodes[node])


    def twin(self, endpoint) -> Endpoint:
        """Return the opposite endpoint (twin) of an endpoint. Both endpoints form an arc.
        
        :param endpoint: Endpoint instance or pair (node, position)
        :return: twin endpoint instance
        """
        node, position = endpoint
        return self._nodes[node][position]

    def get_endpoint_from_pair(self, endpoint_pair):
        """Returns the Endpoint instance of the pair (node, position).
        
        :param endpoint_pair: a pair (node, position)
        :return: Endpoint instance
        """

        # the endpoint instance is the twin of the twin
        return self.twin(self.twin(endpoint_pair))

    def remove_endpoint(self, endpoint_for_removal):
        _debug = False

        if _debug:
            print("  Removing", endpoint_for_removal, "from", self._nodes)

        node, pos = endpoint_for_removal
        del self._nodes[node][pos]

        # adjust change of position for all adjacent endpoints
        for adj_node, adj_pos in self._nodes[node][pos:]:
            i = self._nodes[adj_node]  # node instance
            i[adj_pos] = Endpoint(i[adj_pos].node, i[adj_pos].position - 1, attr=i[adj_pos].attr)

    def remove_endpoints_from(self, endpoints_for_removal):
        endpoints = sorted(endpoints_for_removal, key=lambda _: -_.position)  # start removing from the back

        for i, ep in enumerate(endpoints):

            self.remove_endpoint(ep)

            # adjust change of position for the rest of the endpoints in the list
            for j in range(i + 1, len(endpoints)):
                if endpoints[j].node == ep.node and endpoints[j].position > ep.position:
                    endpoints[j] = (endpoints[j].node, endpoints[j].position - 1)  # the attribute is not needed

    # arc operations

    def set_arc(self, arc_for_setting, **attr):
        """Set the arc (v_endpoint, u_endpoint), which equals setting the two endpoints adj(u_endpoint) = v_endpoint
        and vice-versa."""
        v_endpoint, u_endpoint = arc_for_setting
        self.set_endpoint(v_endpoint, u_endpoint, **attr)
        self.set_endpoint(u_endpoint, v_endpoint, **attr)

    def set_arcs_from(self, arcs_for_adding, **attr):
        """Set the list of arcs.
        
        :param arcs_for_adding: a iterable of tuples (v_endpoint, u_endpoint)
        :return: None
        """
        for arc in arcs_for_adding:
            self.set_arc(arc, **attr)

    def remove_arc(self, arc_for_removing):
        self.remove_endpoints_from(arc_for_removing)

    def remove_arcs_from(self, arcs_for_removing):
        self.remove_endpoints_from(chain(*arcs_for_removing))

    def __hash__(self):
        """Unsafe hashing"""

        def _endpoints_to_tuple(node):
            return tuple((type(ep), ep.node, ep.position, ep.attr["color"]) if "color" in ep.attr else (ep.node, ep.position)
                    for ep in self._nodes[node])

        self_attr = (self.framing, )
        self_nodes = tuple(
            (node, type(self._nodes[node]), _endpoints_to_tuple(node), self._nodes[node].attr["color"])
            if "color" in self._nodes[node].attr else
            (node, type(self._nodes[node]), _endpoints_to_tuple(node))
            for node in self._nodes
        )
        return hash(self_attr + self_nodes)

    @staticmethod
    def is_oriented():
        False


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
    def number_of_bonds(self):
        return len(self.bonds)

    @property
    def number_of_terminals(self):
        return len(self.terminals)

    @property
    def number_of_endpoints(self):
        return sum(len(node) for node in self.nodes.values())

    @property
    def number_of_arcs(self):
        return self.number_of_endpoints // 2

    @property
    def framing(self):
        """Blackboard framing number of planar diagram."""
        return self.attr.get("framing", 0)

    @name.setter
    def name(self, s):
        """Set planar diagram name identifier."""
        self.attr["name"] = s

    @framing.setter
    def framing(self, framing):
        """Set (blackboard) framing of planar diagram."""
        self.attr["framing"] = framing

    def __str__(self):
        # TODO: get node name from descriptor

        attrib_str = ", ".join([f"{key}={value}" for key, value in self.attr.items() if key != "name" and key != "framing"])

        return "".join(
            [
                f"{self.__class__.__name__} ",
                f"named {self.name} " if self.name else "",
                f"with {self.number_of_nodes} nodes, ",
                f"{self.number_of_arcs} arcs, ",
                f"and adjacencies {self.nodes}" if self.nodes else f"and no adjacencies",
                f" with framing {self.framing}",
                f" ({attrib_str})" if attrib_str else ""
            ]
        )


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

    d = PlanarDiagram()
    d.add_node("a", create_using=Vertex)
    d.add_crossing("olala")
    d._nodes = dict()
    print(d)
    pass
"""
The PlanarDiagram class provides the basic abstract class for all planar objects (planar graph, knots, knotted graphs,
...).

A PlanarDiagram class consists of:
  - the diagram class with optional attributes,
  - nodes (vertices), that are any hashable objects with optional attributes,
  - endpoints, that represent part of the edge/arc emanating from the node and is a tuple (node, node_position), with
    optional attributes

In addition, we use the following terminology:
  - arcs are tuples of endpoints,
  - regions are the faces of the planar graph and are represented as a sequence of endpoints.
"""


from functools import cached_property, total_ordering
from abc import ABC, abstractmethod
from copy import deepcopy
from itertools import chain

from knotpy.utils.decorators import total_order_py3
from knotpy.utils.combinatorics import identitydict
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Node
from knotpy.classes.views import NodeView, EndpointView, ArcView

__all__ = ['PlanarDiagram', '_NodeCachedPropertyResetter']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

class _NodeCachedPropertyResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""

    def __init__(self, **_node_type_property_names):
        self._node_type_property_names = _node_type_property_names

    def __set__(self, obj, value):
        """The instance variable "node" has been changed, reset all cached properties. The class view instances "nodes",
        "endpoints", and "arcs" are common for all planar diagrams, additional class view instances are stored in
        _node_type_property_names."""
        od = obj.__dict__
        od["_nodes"] = value
        if "nodes" in od:
            del od["nodes"]
        if "endpoints" in od:
            del od["endpoints"]
        if "arcs" in od:
            del od["arcs"]
        for node_type in self._node_type_property_names:
            if self._node_type_property_names[node_type] in od:
                del od[self._node_type_property_names[node_type]]

@total_order_py3
class PlanarDiagram(ABC):
    """The PlanarDiagram class is intended to be used only as the parent class for Knot, PlanarGraph, etc."""

    _nodes: dict = _NodeCachedPropertyResetter()

    def __init__(self, **attr):
        self._nodes = dict()
        self.attr = dict()  # store graph attributes (without a View)
        self.attr.update(attr)

    def clear(self):
        """Remove/clear all diagram data."""
        self._nodes = dict()
        self.attr = dict()

    def copy(self, copy_using=None):
        copy_using = copy_using or type(self)
        k = copy_using()  # new instance

        k.attr.update(self.attr)  # update knot attributes
        k.add_nodes_from(self._nodes)
        for node in self._nodes:
            for position, ep in enumerate(self._nodes[node]):
                k.set_endpoint((node, position), ep)
        return k

    def __deepcopy__(self, memo):
        """Return a deep copy of self."""
        # TODO: read memo documentation
        new_k = type(self)()
        new_k.attr = deepcopy(self.attr, memo)
        new_k._nodes = deepcopy(self._nodes)
        return new_k

    def __len__(self):
        """Return the number of nodes in the knot."""
        return len(self._nodes)

    def py3_cmp(self, other, compare_attr=False):
        """Compare diagrams. Replaces obsolete __cmp__ method.
        :param other:
        :param compare_attr: do we compare also the node attributes (name, color, ...)
        :return: 1 if self > other, -1 if self < other, and 0 otherwise.
        """

        if type(self).__name__ != type(other).__name__:
            return ((type(self).__name__ > type(other).__name__) << 1) - 1

        if self.number_of_nodes != other.number_of_nodes:
            return self.number_of_nodes > other.number_of_nodes

        for this_node, that_node in zip(self._nodes, other._nodes):
            if cmp := this_node.py3_cmp(that_node, compare_attr=compare_attr):
                return cmp

        if self.framing != other.framing:
            return self.framing > other.framing

        if compare_attr:
            pass



        if type(self).__name__ != type(other).__name__:
            return ((type(self).__name__ > type(other).__name__) << 1) - 1

        if len(self) != len(other):
            return ((len(self) < len(other)) << 1) - 1

        for a, b in zip(self, other):
            if a != b:
                return ((a < b) << 1) - 1

        if compare_attr:
            return cmp_dict(self.attr, other.attr)
        return 0



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

    def __getitem__(self, item):
        if isinstance(item, Endpoint):
            return self._nodes[item.node][item.position]
        else:
            return self._nodes[item]

    # node operations

    def add_node(self, node_for_adding, create_using: type, degree=None, **attr):
        """Add a node of type create_using with optional degree and attributes.
        :param node_for_adding: any hashable object
        :param create_using: the node type
        :param degree: optional degree of the node
        :param attr:
        :return: None
        """
        node = node_for_adding
        #degree = degree or 0



        if node is None:
            raise ValueError(f"None cannot be a {create_using.__name__.lower()}")

        if node not in self._nodes:
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

    # def degree(self, node):
    #     return len(self._nodes[node])

    def rotate_node_ccw(self, node, ccw_shift = 1):
        """Permute the positions of endpoints of the node and take care of adjacent nodes. For example, if we rotate a
        4-valent node by 90 degrees, the positions change from (0, 1, 2, 3) to (3, 0, 1, 2), so the permutation
        should be {0: 3, 1: 0, 2: 1, 3: 2}.
        :param node: the node of which endpoints we permute
        :param ccw_shift: a dict or list object
        :return:
        """
        node_obj = self._nodes[node]

        # take care of adjacent vertices
        for pos, (adj_node, adj_pos) in enumerate(an):
            self._adj[adj_node][adj_pos] = (node, p.get(pos, pos))

        # permute the node
        self._adj[node] = [an[p.get(i, i)] for i in range(len(an))]

        # take care of endpoint attributes
        self._endpoint_attr.update({(node, p[pos]): self._endpoint_attr[(node, pos)] for pos in p})

    def rename_nodes(self, mapping_dict):
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
        self._nodes = {
            mapping.get(node_key, node_key): node_inst
            for node_key, node_inst in self._nodes.items()
        }
        for ep in self.endpoints:
            ep.node = mapping.get(ep.node, ep.node)

    # endpoint operations

    def set_endpoint(self, endpoint_for_setting, adjacent_endpoint, create_using=None, **attr):
        """Set the endpoint to the adjacent endpoint and update the endpoint attributes.
        :param endpoint_for_setting: Endpoint object or tuple (crossing name, position)
        :param adjacent_endpoint: overwrite the endpoint with adjacent_endpoint (Endpoint object or tuple
        (crossing name, position))
        :param create_using: if the type is not Endpoint (or IngoingEndpoint or OutgoingEndpoint), the class should be
        given, be default Endpoint is assumed if endpoint_for_setting is given as a tuple. If an Endpoint instance is
        given instead of a class, the instance type is used with attributes copied.
        :param attr: additional attributes of the endpoint are added
        :return: None
        """

        # endpoint for setting
        node, node_pos = endpoint_for_setting


        #print(type(adjacent_endpoint), isinstance(adjacent_endpoint, Endpoint))

        # adjacent endpoint
        if isinstance(adjacent_endpoint, Endpoint):
            create_using = create_using or type(adjacent_endpoint)
            adjacent_endpoint = create_using(*adjacent_endpoint, **adjacent_endpoint.attr)
            adjacent_endpoint.attr.update(attr)
        elif isinstance(create_using, Endpoint):
            # if create_using is an instance, create new instance from its class and copy the attributes and override
            # the new attributes
            adjacent_endpoint = type(create_using)(*adjacent_endpoint, **(create_using.attr | attr))

            pass
        else:
            create_using = create_using or Endpoint
            adjacent_endpoint = create_using(*adjacent_endpoint, **attr)

        #print("a", self._nodes[node])

        for i in range(node_pos + 1 - len(self._nodes[node])):
            self._nodes[node].append(Node)

        #self._nodes[node] += [None] * (node_pos + 1 - len(self._nodes[node]))
        #print("b", self._nodes[node])



        #int(self._nodes)

        #print("set endpoint", "node", node, "pos", node_pos, "adj", adjacent_endpoint)
        #print("node", node,self._nodes[node])
        self._nodes[node][node_pos] = adjacent_endpoint


        #print(self._nodes[node])

    def get_endpoint(self, node, position):  # TODO: should this be private?
        """Return the endpoint Endpoint(node, position)"""
        adj_endpoint = self._nodes[node][position]
        return self[adj_endpoint]  # return the adjacent endpoint of the adjacent endpoint

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

    def set_arc(self, arc_for_setting , **attr):
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

    @abstractmethod
    def is_oriented(self):
        pass

    @abstractmethod
    def is_knotted(self):
        pass

    @staticmethod
    @abstractmethod
    def to_unoriented_class(self):
        pass

    #@staticmethod
    @abstractmethod
    def to_oriented_class(self):
        pass

    @property
    def name(self):
        """Name identifier of planar diagram."""
        return self.attr.get("name", "")

    @property
    def number_of_nodes(self):
        return len(self._nodes)

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
        return "".join(
            [
                f"{self.__class__.__name__} ",
                f"named {self.name} " if self.name else "",
                f"with {self.number_of_nodes} nodes, ",
                f"{self.number_of_arcs} arcs, ",
                f"and adjacencies {self.nodes}" if self.nodes else f"and no adjacencies",
                f" with framing {self.framing}"
            ]
        )

def _tests():


    pass

if __name__ == "__main__":
    _tests()
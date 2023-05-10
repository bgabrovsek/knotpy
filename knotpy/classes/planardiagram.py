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

from knotpy.classes.endpoint import Endpoint, OrientedEndpoint
from knotpy.classes.views import NodeView, EndpointView, ArcView

__all__ = ['PlanarDiagram', '_NodeCachedPropertyResetter']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _NodeCachedPropertyResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""

    def __init__(self, **_node_type_property_names):
        self._node_type_property_names = _node_type_property_names

    def __set__(self, obj, value):
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

    def __deepcopy__(self, memo):
        """Return a deep copy of self."""
        # TODO: read memo documentation
        new_k = self.__class__()
        new_k.attr = deepcopy(self.attr, memo)
        new_k._nodes = deepcopy(self._nodes)
        return new_k

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

    def degree(self, node):
        return len(self._nodes[node])


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

    def remove_node(self, node_for_removing, remove_incident_arcs=True):
        if remove_incident_arcs:
            self._remove_arcs_from(self.incident_arcs(node_for_removing))
        del self._node_attr[node_for_removing]
        del self._adj[node_for_removing]

    def remove_nodes_from(self, nodes_for_removal, remove_incident_arcs=True):
        for v in nodes_for_removal:
            self._remove_node(v, remove_incident_arcs)



    # endpoint operations

    def set_endpoint(self, endpoint_for_setting, adjacent_endpoint, **attr):
        """Set the endpoint to the adjacent endpoint and update the endpoint attributes.
        :param endpoint_for_setting: Endpoint object or tuple (crossing name, position)
        :param adjacent_endpoint: overwrite the endpoint with adjacent_endpoint (Endpoint object or tuple
        (crossing name, position))
        :param attr: additional attributes of the endpoint
        :return: None
        """
        node, node_pos = (endpoint_for_setting.node, endpoint_for_setting.position) \
            if isinstance(endpoint_for_setting, Endpoint) else endpoint_for_setting

        if not isinstance(adjacent_endpoint, Endpoint):
            adjacent_endpoint = OrientedEndpoint(*adjacent_endpoint) \
                if self.is_oriented() else Endpoint(*adjacent_endpoint)

        adjacent_endpoint.attr.update(**attr)

        self._nodes[node][node_pos] = adjacent_endpoint

    def get_endpoint(self, node, position):  # TODO: should this be private?
        """Return the endpoint Endpoint(node, position)"""
        adj_endpoint = self._nodes[node][position]
        return self[adj_endpoint]  # return the adjacent endpoint of the adjacent endpoint

    def remove_endpoint(self, endpoint_for_removal):
        _debug = False

        if _debug:
            print("  Removing", endpoint_for_removal, "from", self._nodes)

        node, pos = endpoint_for_removal
        del self.nodes[node][pos]

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
                f"and adjacencies {self.nodes}" if self.nodes else f"and no adjacencies"
            ]
        )

def _tests():


    pass

if __name__ == "__main__":
    _tests()
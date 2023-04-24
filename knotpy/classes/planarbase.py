#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PlanarDiagram class.

TODO:
make cached property, so we can call:
nodes, adj,...
compare operations,...
canonical ...
"""


from functools import cached_property, total_ordering
from copy import copy, deepcopy

from knotpy.utils import lexicographical_minimal_cyclic_rotation_shift
from knotpy.classes.views import AttributeView, AdjacencyView

__all__ = ['PlanarBase']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _PlanarBaseCachedPropertyAdjResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od: del od["adj"]

class _PlanarBaseCachedPropertyNodeAttributeResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node_attr"] = value
        if "nodes" in od: del od["nodes"]

class _PlanarBaseCachedPropertyEndpointAttributeResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_endpoint_attr"] = value
        if "endpoints" in od: del od["endpoints"]


@total_ordering
class PlanarBase:
    """
    Planar (diagram) base class. This class is intended to be used only as the parent class for PlanarDiagram, etc.
    It includes common methods used by all planar structures (planar graph diagrams, knot diagrams,...).
    Classes such as PlanarDiagram also include methods such as _insert_arc_between_nodes(), which should not be used
    for classes that represent e.g. knot diagrams. Therefore, data parent PlanarBase class is implemented.
    """

    _adj = _PlanarBaseCachedPropertyAdjResetter()
    _node_attr = _PlanarBaseCachedPropertyNodeAttributeResetter()
    _endpoint_attr = _PlanarBaseCachedPropertyEndpointAttributeResetter()

    adj_outer_factory = dict
    adj_inner_factory = list
    graph_attr_factory = dict
    node_attr_outer_factory = dict
    node_attr_inner_factory = dict
    endpoint_attr_outer_factory = dict
    endpoint_attr_inner_factory = dict
    region_outer_factory = list  # could also be set


    def __init__(self, incoming_planar_data=None, **attr):
        """Initialize with ..., or planar diagram attributes (name, ...)"""

        self.attr = self.graph_attr_factory()  # store graph attributes (without data View)
        self._node_attr = self.node_attr_outer_factory()  # dictionary of node attributes
        self._endpoint_attr = self.endpoint_attr_outer_factory()  # dictionary of endpoint attributes
        self._adj = self.adj_outer_factory()  # dictionary of lists of endpoints in CCW order

        # no data
        if incoming_planar_data is not None:
            raise ValueError("PlanarBase class should not be called with planar initialization data.")

        self.attr.update(attr)

    def __deepcopy__(self, memo):
        """
        :return: returns data deep copy of self (the planar base diagram)
        TODO: read memo documentation
        """
        new_g = self.__class__()
        new_g._adj = deepcopy(self._adj, memo)
        new_g.attr = deepcopy(self.attr, memo)
        new_g._node_attr = deepcopy(self._node_attr, memo)
        new_g._endpoint_attr = deepcopy(self._endpoint_attr, memo)
        return new_g

    # cached properties

    @cached_property
    def adj(self):
        """Graph adjacency object holding the neighbors of each node.
        """
        return AdjacencyView(self._adj)
        pass

    @cached_property
    def nodes(self):
        return AttributeView(self._node_attr)

    @cached_property
    def endpoints(self):
        return AttributeView(self._endpoint_attr)

    # node operations

    def add_node(self, node_for_adding, degree=None, **attr):
        """
        Adds data single node 'node_for_adding' and updates the node attributes.
        :param node_for_adding: the node, that can be any hashable object, except None
        :param attr: keyword arguments, optional
        :param degree: reserve entries for endpoints
        :return: none
        """

        node = node_for_adding

        if node is None:
            raise ValueError("None cannot be data node.")

        if node not in self._node_attr:
            self._node_attr[node] = self.node_attr_inner_factory()
            self._adj[node] = self.adj_inner_factory() if degree is None else self.adj_inner_factory([None] * degree)
        elif degree is not None:
            if degree < len(self._adj[node]):
                raise ValueError("Cannot change the degree node to data lower value.")
            elif degree > len(self._adj[node]):
                self._adj[node] += [None] * (degree - len(self._adj[node]))  # assumes adj_inner_factory is list


        self._node_attr[node].update(attr)  # add attributes to node

    def add_nodes(self, nodes_for_adding, degrees=None):
        """Adds data list (iterable) of nodes to the graph.
        :param nodes_for_adding: iterable of nodes
        :param degrees: reserve entries for endpoints
        :return: none
        """
        if degrees is not None and len(nodes_for_adding) != len(degrees):
            raise ValueError("The number of nodes should match the number of degrees.")

        if degrees is None:
            for node in nodes_for_adding:
                self.add_node(node)
        else:
            for node, degree in zip(nodes_for_adding, degrees):
                self.add_node(node, degree)

    def _insert_arc_between_nodes(self, node_a, node_b, position_a, position_b, multiplicity):
        """Inserts an arc (or parallel arcs) between node_a and node_b.
        Shifts all endpoint indices .
        For example, if node_a has endpoints ((f, pos_f), (f, pos_f),...) and position_a=1 and multiplicity=2,
        the method shifts the endpoints to ((data, pos_a), (node_b, position_b-1 CHECK),..., (b, pos_b),...
        The method takes care of repositioning the adjacent endpoints of the two nodes.
        :param node_a:
        :param node_b:
        :param position_a:
        :param position_b:
        :param multiplicity:
        :return:
        """
        raise NotImplemented()

    def _insert_endpoints_to_node(self, node, position, endpoints):
        """Inserts endpoints to node. Shifts all endpoint indices by len(endpoints).
        For example, if node n has endpoints ((data, pos_a), (b, pos_b),...) calling the method with position=1,
        shifts the endpoints to ((data, pos_a), (endpoints[0]), (endpoints[1]),..., (b, pos_b),...
        The method takes care of repositioning the adjacent endpoints of the node.
        Also, we must be careful that the endpoints list is consistent with the global graph structure.
        :param node: existing node to modify
        :param position: the position (index) of inserting new endpoints to node
        :param endpoints: data list of new endpoints of node in CCW order
        :return:
        """
        # call add_node_in_region...

        shift = len(endpoints)

        # shift the existing endpoint attributes of node
        for pos in range(position, self.degree(node))[::-1]:
            self._endpoint_attr[(node, pos + shift)] = self._endpoint_attr[(node, pos)]

        # remove the newly created endpoint attributes
        for pos in range(position, position + shift):
            self._endpoint_attr[(node, pos)] = self.node_attr_inner_factory()  # TODO: attributes of new endpoints

        # insert the new endpoints in node adjacency list
        self._adj[node] = self._adj[node][:position] + endpoints + self._adj[node][position:]

        # change end adjacencies of adjacent nodes of node
        for adj_v, adj_v_pos in self._adj[node][position + shift:]:
            assert node == self._adj[adj_v][adj_v_pos][0]  # TODO: remove this, it's only for checking
            self._adj[adj_v][adj_v_pos] = (node, self._adj[adj_v][adj_v_pos][1] + shift)

    def rename_nodes(self, node_reindex_dict=None):
        """Renames the vertices according to dictionary reindex_dict. If no dictionary provided, the function will
        reindex using natural numbers, 0, 1,...,n.
        :param node_reindex_dict:
        :return: reindexed graph if return_new_graph is True, self otherwise
        """

        if node_reindex_dict is None:
            node_reindex_dict = dict(zip(self._adj, range(len(self))))

        # assume factories are dicts, TODO: take factory classes
        self._node_attr = {node_reindex_dict[v]: self._node_attr[v] for v in self._node_attr}
        self._endpoint_attr = {(node_reindex_dict[ep[0]], ep[1]): self._endpoint_attr[ep] for ep in self._endpoint_attr}
        self._adj = {node_reindex_dict[v]: [(node_reindex_dict[u], pos) for u, pos in self._adj[v]] for v in self._adj}


    # endpoint operations

    def _add_single_endpoint(self, endpoint, adjacent_endpoint, **attr):
        """

        :param endpoint: tuple
        :param adjacent_endpoint: tuple
        :param attr:
        :return:
        """

        v, v_pos = endpoint

        if v not in self._node_attr:
            self.add_node(v)

        if v_pos >= len(self._adj[v]):  # make space is position is larger than node degree
            self._adj[v] += [None] * (v_pos - len(self._adj[v]) + 1)  # assuming adj_inner_factory is data list
        self._adj[v][v_pos] = adjacent_endpoint

        if endpoint not in self._endpoint_attr:
            self._endpoint_attr[endpoint] = self.endpoint_attr_inner_factory()

        self._endpoint_attr[endpoint].update(attr)

    # arc operations

    def add_arc(self, u_endpoint, v_endpoint, **attr):
        """
        :param u_endpoint:
        :param v_endpoint:
        :param attr:
        :return:
        """
        _debug = False
        if _debug:
            print("Adding edge with endpoints", u_endpoint, v_endpoint)
        self._add_single_endpoint(tuple(u_endpoint), tuple(v_endpoint), **attr)
        self._add_single_endpoint(tuple(v_endpoint), tuple(u_endpoint), **attr)

    def add_arcs(self, endpoint_pairs_for_adding):
        """
        :param endpoint_pairs_for_adding:
        :return:
        """
        for u_ep, v_ep in endpoint_pairs_for_adding:
            self.add_arc(u_ep, v_ep)

    def arcs(self) -> list:
        """Returns data list of arcs, each arc is data tuple (endpoint, adjacent endpoint).
        TODO: if diagram is oriented, return the endpoints in oriented order.
        TODO: implement as an iterator."""
        arcs = []
        for ep0 in self._endpoint_attr:
            ep1 = self._adj[ep0[0]][ep0[1]]
            if ep0 < ep1:
                arcs.append((ep0, ep1))
        return arcs

    def incident_arcs(self, node):
        return [((node, pos), ep) for pos, ep in enumerate(self._adj[node])]

    # components


    # various


    def clear(self):
        """Remove all data from planar diagram.
        """
        self.attr.clear()
        self._node_attr.clear()
        self._endpoint_attr.clear()
        self._adj.clear()

    # degree methods

    def degree(self, v=None):
        # implement as data view, if needed
        if v is None:
            return {v: len(self._adj[v]) for v in self._adj}
        return len(self._adj[v])


    # region operations

    def regions(self):
        """
        Returns regions (planar graph faces) of data planar graph.
        First it puts all endpoints (vertex, position) to data set, then selects an unused and  travels along the edges
        until no endpoints are left.
        :return: data set of n-tuples, each n-tuple consists of the endpoints of the region.
        """
        # TODO: change this to data cached property

        unused_endpoints = set(self._endpoint_attr)  # TODO: use view?
        regions = self.region_outer_factory()
        v, v_pos, region = None, None, []  # not needed
        ep = None

        while unused_endpoints:
            if ep is None:  # get new endpoint if cycle is finished or main loop has started
                v, v_pos = ep = next(iter(unused_endpoints))
                region = []
            unused_endpoints.remove(ep)
            region.append(ep)  # add ep to current area
            v, v_pos = ep = self._adj[v][v_pos]  # get adjacent endpoint TODO: use view
            v_pos = (v_pos - 1) % len(self._adj[v])  # rotate CW (to get the region in CCW order)
            ep = (v, v_pos)
            if ep not in unused_endpoints:
                ep = None
                regions.append(tuple(region))  # .add() for set

        return regions


    def _canonically_rotate_node(self, node):
        # TODO: if structure is not an undirected graph (not yet implemented), this method might be different.

        shift = lexicographical_minimal_cyclic_rotation_shift(self._adj[node])

        # take care of adjacent vertices
        for pos, (adj_node, adj_pos) in enumerate(self._adj[node]):
            self._adj[adj_node][adj_pos] = (node, (pos - shift) % len(self._adj[node]))
        # rotate the node
        self._adj[node] = self._adj[node][shift:] + self._adj[node][:shift]

    def __len__(self):
        return len(self._node_attr)

    def __eq__(self, other):
        """We assert data total order on planar graphs. We also consider node and endpoint attributes.
        From the graph attributes, we only consider the framing."""
        # lexicographical ordering
        return (
            self.nodes == other.nodes and
            self.adj == other.adj and
            self.endpoints == other.endpoints and
            self.framing == other.framing
        )

    def __lt__(self, other):
        if (cmp := self.nodes.py3_cmp(other.nodes)) != 0: return cmp < 0
        if (cmp := self.adj.py3_cmp(other.adj)) != 0: return cmp < 0
        if (cmp := self.endpoints.py3_cmp(other.endpoints)) != 0: return cmp < 0
        if (cmp := self.framing - other.framing) != 0: return cmp < 0


    def __hash__(self):
        """The hash function takes the hash of the tuple of tuples representing the (condensed) EM notation."""
        return hash(
            tuple(adj_ep for node in range(self.number_of_nodes) for adj_ep in self._adj[node]
            )
        )


    # non-cached properties

    @property
    def name(self):
        """String identifier of planar diagram."""
        return self.attr.get("name", "")
    @property
    def number_of_nodes(self):
        return len(self._node_attr)
    @property
    def number_of_arcs(self):
        return len(self._endpoint_attr) // 2
    @property
    def number_of_endpoints(self):
        return len(self._endpoint_attr)
    @property
    def framing(self):
        """(Blackboard) framing number of planar diagram."""
        return self.attr.get("framing", 0)

    @name.setter
    def name(self, s):
        """Set planar diagram name.
        """
        self.attr["name"] = s

    @framing.setter
    def framing(self, n):
        """Set (blackboard) framing of planar diagram."""
        self.attr["framing"] = n

    # printing

    def __repr__(self):
        return str(to_em_notation(self)).replace(" ","")


    def __str__(self):

        #print("N", self._node_attr)
        #print("A", self._adj)
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with {self.number_of_nodes} nodes, {self.number_of_arcs} arcs,",
                f" and adjacencies " + str(self.adj) if len(self.adj) else f" and no adjacencies"
            ]
        )


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
import knotpy as kp
from knotpy import convert
from queue import Queue
from copy import copy, deepcopy
from knotpy.combinatorics import minimal_cyclic_rotation

from knotpy.views import AttributeView, AdjacencyView

__all__ = ['PlanarGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _PlanarGraphCachedPropertyAdjResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od: del od["adj"]

class _PlanarGraphCachedPropertyNodeAttributeResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node_attr"] = value
        if "nodes" in od: del od["nodes"]

class _PlanarGraphCachedPropertyEndpointAttributeResetter:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_endpoint_attr"] = value
        if "endpoints" in od: del od["endpoints"]


@total_ordering
class PlanarGraph:
    """
    Class for a undirected planar multi graph diagram.
    """

    _adj = _PlanarGraphCachedPropertyAdjResetter()
    _node_attr = _PlanarGraphCachedPropertyNodeAttributeResetter()
    _endpoint_attr = _PlanarGraphCachedPropertyEndpointAttributeResetter()

    adj_outer_factory = dict
    adj_inner_factory = list
    graph_attr_factory = dict
    node_attr_outer_factory = dict
    node_attr_inner_factory = dict
    endpoint_attr_outer_factory = dict
    endpoint_attr_inner_factory = dict


    def __init__(self, incoming_planargraph_data=None, **attr):
        """Initialize with ..., or planar diagram attributes (name, ...)"""

        self._graph_attr = self.graph_attr_factory()  # store graph attributes (without a View)
        self._node_attr = self.node_attr_outer_factory()  # dictionary of node attributes
        self._endpoint_attr = self.endpoint_attr_outer_factory()  # dictionary of endpoint attributes
        self._adj = self.adj_outer_factory()  # dictionary of lists of endpoints in CCW order

        if incoming_planargraph_data is not None:
            convert.to_pg(incoming_planargraph_data, create_using=self)

        self._graph_attr.update(attr)

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

    def add_node(self, node_for_adding, degree=None, **attr):
        """
        Adds a single node 'node_for_adding' and updates the node attributes.
        :param node_for_adding: the node, that can be any hashable object, except None
        :param attr: keyword arguments, optional
        :param degree: reserve entries for endpoints
        :return: none
        """

        node = node_for_adding

        if node is None:
            raise ValueError("None cannot be a node.")

        if node not in self._node_attr:
            self._node_attr[node] = self.node_attr_inner_factory()
            self._adj[node] = self.adj_inner_factory() if degree is None else self.adj_inner_factory([None] * degree)
        elif degree is not None:
            if degree < len(self._adj[node]):
                raise ValueError("Cannot change the degree node to a lower value.")
            elif degree > len(self._adj[node]):
                self._adj[node] += [None] * (degree - len(self._adj[node]))  # assumes adj_inner_factory is list


        self._node_attr[node].update(attr)  # add attributes to node

    def add_nodes(self, nodes_for_adding, degrees=None):
        """Adds a list (iterable) of nodes to the graph.
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
            for node, degree in zip(nodes_for_adding):
                self.add_node(node, degree)

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
            self._adj[v] += [None] * (v_pos - len(self._adj[v]) + 1)  # assuming adj_inner_factory is a list
        self._adj[v][v_pos] = adjacent_endpoint

        if endpoint not in self._endpoint_attr:
            self._endpoint_attr[endpoint] = self.endpoint_attr_inner_factory()

        self._endpoint_attr[endpoint].update(attr)


    def add_arc(self, u_endpoint, v_endpoint, **attr):
        """
        :param u_endpoint:
        :param v_endpoint:
        :param attr:
        :return:
        """
        self._add_single_endpoint(tuple(u_endpoint), tuple(v_endpoint), **attr)
        self._add_single_endpoint(tuple(v_endpoint), tuple(u_endpoint), **attr)

    def add_arcs(self, endpoint_pairs_for_adding):
        """
        :param endpoint_pairs_for_adding:
        :return:
        """
        for u_ep, v_ep in endpoint_pairs_for_adding:
            self.add_arc(u_ep, v_ep)

    def clear(self):
        """Remove all data from planar diagram.
        """
        self._graph_attr.clear()
        self._node_attr.clear()
        self._endpoint_attr.clear()
        self._adj.clear()


    def degree(self, v=None):
        # implement as a view, if needed
        if v is None:
            return {v: len(self._adj[v]) for v in self._adj}
        return len(self._adj[v])

    def degree_sequence(self):
        return sorted(len(self._adj[v]) for v in self._adj)

    def regions(self):
        # TODO: change this to a cached property

        unused_endpoints = set(self._endpoint_attr)  # TODO: use view?
        regions = set()
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
                regions.add(tuple(region))

        return regions

    def reindex_nodes(self, node_reindex_dict=None):
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


    def canonical(self, in_place=True):
        """Puts itself in unique canonical form.
        The diagram start with an endpoint on of a minimal degree vertex, it continues to an adjacent endpoints and
        distributes the ordering from there on using breadth first search using CCW order of visited nodes.
        At the moment, it is only implemented if the graph is connected.
        TODO: In case of degree 2 vertices the canonical form might not be unique.
        :param in_place:
        :return: None
        """

        _debug = False

        minimal_degree = min(self.degree_sequence())
        nodes_with_minimal_degree = [v for v in self._node_attr if self.degree(v) == minimal_degree]
        # TO-DO: optimize by viewing also 2nd degree (number of neighbour's neighbours)

        # endpoints of minimal nodes
        starting_endpoints = [(v, pos) for v in nodes_with_minimal_degree for pos in range(minimal_degree)]

        minimal_graph = None

        if _debug: print("starting endpoints",starting_endpoints)

        for ep_start in starting_endpoints:
            if _debug: print("starting with", ep_start)


            node_reindex_dict = dict()  # also holds as a "visited node" set
            endpoint_queue = Queue()
            endpoint_queue.put(ep_start)

            while not endpoint_queue.empty():
                v, pos = ep = endpoint_queue.get()
                if _debug: print("popping endpoint", ep)
                if v not in node_reindex_dict:  # new node visited
                    node_reindex_dict[v] = len(node_reindex_dict)  # rename the node to next available integer
                    v_deg = self.degree(v)
                    # put all adjacent endpoints in queue in ccw order
                    for relative_pos in range(1, v_deg):
                        endpoint_queue.put((v, (pos + relative_pos) % v_deg))

                # go to the adjacent endpoint and add it to the queue
                adj_v, adj_pos = adj_ep = self._adj[v][pos]
                if adj_v not in node_reindex_dict:
                    endpoint_queue.put(adj_ep)

            if _debug: print(node_reindex_dict)
            if len(node_reindex_dict) != len(self):
                raise ValueError("Cannot put a non-connected graph into canonical form.")

            new_graph = copy(self)
            new_graph.reindex_nodes(node_reindex_dict)

            for v in new_graph._adj:
                new_graph._canonically_rotate_node(v)

            if minimal_graph is None or new_graph < minimal_graph:
                minimal_graph = new_graph

        if in_place:
            # copy all data from minimal_graph
            self._node_attr = minimal_graph._node_attr
            self._endpoint_attr = minimal_graph._endpoint_attr
            self._adj = minimal_graph._adj
        else:
            return minimal_graph

    def _canonically_rotate_node(self, node):
        # TODO: if structure is not an undirected graph (not yet implemented), this method might be different.

        self._adj[node] = minimal_cyclic_rotation(self._adj[node])


    def __len__(self):
        return len(self._node_attr)

    def __eq__(self, other):
        """We assert a total order on planar graphs. We also consider node and endpoint attributes.
        From the graph attributes, we only consider the framing."""
        # lexicographical ordering
        return (
            self.nodes == other.nodes and
            self.adj == other.adj and
            self.endpoints == other.endpoints and
            self.framing == other.framing
        )

    def __le__(self, other):
        return not (
            self.nodes >= other.nodes or
            self.adj >= other.adj or
            self.endpoints >= other.endpoints or
            self.framing >= other.framing
        )

    @property
    def name(self):
        """String identifier of planar diagram."""
        return self._graph_attr.get("name", "")

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
        return self._graph_attr.get("framing", 0)

    @name.setter
    def name(self, s):
        """Set planar diagram name.
        """
        self._graph_attr["name"] = s

    @framing.setter
    def framing(self, n):
        """Set (blackboard) framing of planar diagram."""
        self._graph_attr["framing"] = n

    def __repr__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with nodes {str(self._node_attr)},",
                f" adjacencies {str(self._adj)}"
            ]
        )

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with nodes {str(tuple(self._adj))},",
                f" adjacencies " + str(self.adj)
            ]
        )




if __name__ == '__main__':
    g = PlanarGraph(name="Myname", color="peri", framing=3)

    g.add_nodes("ABC")
    g.add_node("A",color=3)
    g.add_arcs([
        [("A", 0), ("B", 0)],
        [("B", 1), ("C", 0)],
        [("A", 1), ("C", 1)]
    ])

    print(g)
    g.reindex_nodes()
    print(g)
    g.canonical()
    #print(g)
    print("Regions:", g.regions())

    for v in g.nodes:
        print(v, g.nodes[v])

    print(tuple(g.nodes))

    print()

    f = PlanarGraph()
    #f.add_nodes("abcd")
    f.add_node(0)
    f.add_node(1)
    f.add_arc((1,0),(0,0))
    print(f)
    f.canonical()

    print("can",f)

    #print(g.canonical())

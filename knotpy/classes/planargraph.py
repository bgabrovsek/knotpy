#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PlanarDiagram class.
"""

"""
TODO:
make cached property, so we can call:
nodes, adj,...
compare operations,...
canonical ...

"""

__all__ = ['PlanarGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

#from functools import cached_property
import knotpy
import knotpy as kp
from knotpy import convert
import queue


class _CachedPropertyResetterAdj:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html
    """

    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od:
            del od["adj"]


class _CachedPropertyResetterNode:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html
    """
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node"] = value
        if "nodes" in od:
            del od["nodes"]


class PlanarGraph:
    """
    Class for a undirected planar multi graph diagram.
    """


    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()


    adj_outer_factory = dict
    adj_inner_factory = list  # could also be dict {0:ep0, 1:ep1,...}

    graph_attr_factory = dict
    node_attr_outer_factory = dict
    node_attr_inner_factory = dict
    endpoint_attr_outer_factory = dict
    endpoint_attr_inner_factory = dict


    def __init__(self, incoming_planargraph_data=None, **attr):
        """Initialize with ..., or planar diagram attributes (name, ...)"""

        #self._inc = dict()  # list of incident arcs in CCW order
        #self._node = dict()  # dictionary of nodes
        #self._arc = dict()  # dictionary of arcs

        self._attr = self.graph_attr_factory()  # store graph attributes
        self._node_attr = self.node_attr_outer_factory()  # dictionary of node attributes
        self._endpoint_attr = self.endpoint_attr_outer_factory()  # dictionary of endpoint attributes
        self._adj = self.adj_outer_factory()  # dictionary of lists of endpoints in CCW order

        if incoming_planargraph_data is not None:
            convert.to_pg(incoming_planargraph_data, create_using=self)

        self._attr.update(attr)
        pass

    def add_node(self, node_for_adding, **attr):
        """
        Adds a single node 'node_for_adding' and updates the node attributes.
        :param node_for_adding: the node, that can be any hashable object, except None
        :param attr: keyword arguments, optional
        :return: none
        """

        node = node_for_adding

        if node not in self._node_attr:
            if node is None:
                raise ValueError("None cannot be a node.")
            self._node_attr[node] = self.node_attr_inner_factory()
            self._adj[node] = self.adj_inner_factory()

        self._node_attr[node].update(attr)  # add attributes to node

    def add_nodes(self, nodes_for_adding):
        """Adds a list (iterable) of nodes to the graph.
        :param nodes_for_adding: iterable of nodes
        :return: none
        """
        for node in nodes_for_adding:
            self.add_node(node)

    def add_single_endpoint(self, endpoint, adjacent_endpoint, **attr):
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

        self.add_single_endpoint(tuple(u_endpoint), tuple(v_endpoint), **attr)
        self.add_single_endpoint(tuple(v_endpoint), tuple(u_endpoint), **attr)

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

        self._attr.clear()
        self._node_attr.clear()
        self._endpoint_attr.clear()
        self._adj.clear()

    def degree(self, v = None):
        # TODO: implement as view
        if v is None:
            return {v: self.degree(v) for v in self._node_attr}
        return len(self._adj[v])

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

    def canonical(self):
        """Puts planar diagram in unique canonical form.
        The diagram start with an endpoint on of a maximal degree vertex,
        it continues to an adjacent endpoints and distributes the ordering from there on iteratively.
        """

        minimal_degree = min(kp.degree_sequence(self))
        nodes_with_minimal_degree = [v for v in self._node_attr if self.degree(v) == minimal_degree]  # TODO: use node property
        # TODO: optimize by viewing also 2nd degree (number of neighbour neighbours)

        starting_endpoints = [(v, pos) for v in nodes_with_minimal_degree for pos in range(minimal_degree)]

        for ep_start in starting_endpoints:

            v, pos = ep_start

            vertex_reindex_dict = {v: 0}

            endpoints_fifo = queue.Queue
            endpoints_fifo.put(ep_start)

            while endpoints_fifo:
                pass



        #minimal_graph = None


        """
        # start at a crossing of maximal degree
        max_deg = max(self.degree())
        max_deg_vertices = [vertex for vertex in range(len(self)) if self.degree(vertex) == max_deg]

        # possible starting endpoints (vertices and edge positions)
        starting_endpoints = [(vertex, pos) for pos in range(max_deg) for vertex in max_deg_vertices]
        if _debug: print("start ep", starting_endpoints)

        adj_ep_dict = self.endpoint_dict()

        for endpoint_start in starting_endpoints:  # start at a endpoint

            new_graph = PlanarGraph(tuple())

            edge_start = self[endpoint_start]
            if _debug: print("ep", endpoint_start, "edge", edge_start)

            edge_renum = {edge_start: 0}  # keeps track new of edge names

            used_vertices = set()  # here we store vertices to which we have already travelled
            used_arcs = set()  # TODO: use faster structure?
            
            #available endpoints is a list of (i, endpoint), which are endpoints next on stack to process,
            #the first integer is just for sorting, so that we always select the smallest next arc due to
            #current enumeration.

            available_endpoint = [(-1, endpoint_start),
                                  (0, adj_ep_dict[endpoint_start])]  # do we need the adjacent one, probably yes.
            # TODO: it would be faster if available_endpoint would be implemented by a BST or, even better, FIFO queue?
            # TODO: probably dict would be better than list, since first index is unique?

            new_edge_number = 1
            new_graph_not_minimal, new_graph_is_minimal = False, False

            while available_endpoint:

                if _debug: print(available_endpoint)

                # get minimal endpoint
                ep = min(available_endpoint)  # ignore zero index
                available_endpoint.remove(ep)
                ep = ep[1]  # remove 1st int

                used_arcs.add(self[ep])
                vertex, pos = ep
                if vertex not in used_vertices:
                    used_vertices.add(vertex)
                    deg = self.degree(vertex)
                    for p in range(deg):  # start enumerating adjacent edges

                        old_inc_edge = self[vertex][(pos + p) % deg]

                        if old_inc_edge not in edge_renum:
                            edge_renum[old_inc_edge] = new_edge_number
                            adj_ep = adj_ep_dict[(vertex, (pos + p) % deg)]
                            available_endpoint.append((new_edge_number, adj_ep))
                            new_edge_number += 1

                    new_graph.append(min_cyclic_rotation(tuple(edge_renum[e] for e in self[vertex])))

                    if minimal_graph is None:
                        new_graph_is_minimal = True  # if no minimal graph, this one is minimal

                    if minimal_graph is not None and new_graph[-1] < minimal_graph[len(new_graph) - 1]:
                        new_graph_is_minimal = True

                    if not new_graph_is_minimal and minimal_graph is not None and new_graph[-1] > minimal_graph[
                        len(new_graph) - 1]:
                        new_graph_not_minimal = True
                        break

                # take care also of other adjacent node

                if len(new_graph) == len(self):
                    break

            # add remaining nodes to the knot
            if not new_graph_not_minimal and len(self) > len(new_graph):
                additional_nodes = []  # nodes to add to the original graph
                for vertex, edges in enumerate(self):
                    if vertex not in used_vertices:
                        if all(e in edge_renum for e in edges):  # continue only if all arcs already enumerated
                            additional_nodes.nodes.append(min_cyclic_rotation((edge_renum[e] for e in edges)))
                        else:
                            new_graph_not_minimal = True
                            print("new know has additional crossings", self, new_graph)
                            break

                additional_nodes.sort()
                new_graph.nodes += additional_nodes

                if (not new_graph_not_minimal) and (minimal_graph is None or new_graph < minimal_graph):
                    minimal_graph = new_graph  # if we get a minimal knot after adding new nodes, change it

            if not new_graph_not_minimal and len(self) > len(new_graph):
                print("CANONICAL SHOULD HAVE MORE CROSSINGS.")

            if (minimal_graph is None or not new_graph_not_minimal) and (len(self) == len(new_graph)):
                if minimal_graph is not None and minimal_graph < new_graph:
                    print(self, minimal_graph, "<", new_graph)
                    raise ValueError("Canonical graph greater than minimal knot.")
                minimal_graph = new_graph

        if minimal_graph is None: raise ValueError("Canonical graph of", self, "is None.")
        if len(minimal_graph) != len(self): raise ValueError("Canonical graph not of same length than original knot.")

        minimal_graph_copy = PlanarGraph(minimal_graph)

        return minimal_graph_copy
        """
    def __len__(self):
        return len(self._node_attr)

    def __eq__(self, other):
        # also compares node and arc attributes,
        # except the planar diagram name
        if set(self._node_attr) != set(self._node):
            pass

    @property
    def name(self):
        """String identifier of planar diagram.
        """
        return self._attr.get("name", "")

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
        """(Blackboard) framing number of planar diagram.
        """
        return self._attr.get("framing", 0)

    @name.setter
    def name(self, s):
        """Set planar diagram name.
        """
        self._attr["name"] = s

    @framing.setter
    def framing(self, n):
        """Set (blackboard) framing of planar diagram."""
        self._attr["framing"] = n

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
                f" with nodes {str(self._node_attr)},",
                f" adjacencies {str(self._adj)}"
            ]
        )


if __name__ == '__main__':
    g = PlanarGraph(name="Myname", color="peri", framing=3)

    g.add_nodes("ABC")
    g.add_arcs([
        [("A", 0), ("B", 0)],
        [("B", 1), ("C", 0)],
        [("C", 2), ("C", 1)]
    ])
#    g.add_node('C', color="blue")
 #   g.add_arc((0,0),(1,0))
  #  g.add_arc((1,1),('C',0))
 #   g.add_arc(('C',2), ('C',1), describe="loop")


    print(g)

    print(g.regions())

    print(g.canonical())

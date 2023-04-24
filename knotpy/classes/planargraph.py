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

from collections import Counter
from itertools import chain

from knotpy.classes.planarbase import PlanarBase



__all__ = ['PlanarGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class PlanarGraph(PlanarBase):

    def __init__(self, incoming_planargraph_data=None, **attr):

        super().__init__(incoming_planar_data=None, **attr)

        if incoming_planargraph_data is not None:
            raise NotImplementedError()
            #convert.to_planardiagram(incoming_planargraph_data, create_using=self)

    def add_node_in_region(self, node_for_adding, region, connect_at_endpoints=tuple(), **attr):
        """Adds data node into the (center of the) region and connect the node to the other nodes in the region.
        :param node_for_adding: name of the node
        :param region:
        :param connect_at_endpoints: an iterable of nodes to connect, also data dictionary can be given,
        the keys are nodes and the values are multiplicities (how many parallel edges to the node)
        :param attr: node attribute
        :return: None
        TODO: find data way to add attributes to the newly created endpoints.
        TODO: what to do with region attribute?
        TODO: do we need the region parameter?
        """
        _debug = False

        node = node_for_adding

        if node in self._node_attr:
            raise ValueError("Cannot add node", node, "since it already exists.")

        multiplicity = Counter(connect_at_endpoints)
        if _debug:
            print("Adding node", node,
                  "to graph", self,
                  "to region", region,
                  "with multiplicity:", multiplicity)

        self.add_node(node, degree=sum(multiplicity.values()), **attr)

        cur_node_pos = 0  # current node position

        ep_seq_ordered = [(ep, multiplicity[ep]) for ep in region if multiplicity[ep] > 0]

        for i, (ep, mult) in enumerate(ep_seq_ordered):
            adj_v, adj_v_pos = ep
            if _debug: print("EP", ep)
            # if (mult := multiplicity[ep]) > 0:
            if _debug: print("adj", adj_v, "with mult", mult)
            # insert node_for_adding to v adjacency list of adj_v
            self._insert_endpoints_to_node(
                adj_v,
                adj_v_pos + 1,
                [(node, cur_node_pos + i) for i in range(mult)[::-1]]
            )

            # adjust endpoints in ep sequence (in case we are adding arcs to the same endpoint)
            for j in range(i + 1, len(ep_seq_ordered)):
                if ep_seq_ordered[j][0][0] == adj_v and ep_seq_ordered[j][0][1] > adj_v_pos:
                    ep_seq_ordered[j] = (
                    (ep_seq_ordered[j][0][0], ep_seq_ordered[j][0][1] + mult), ep_seq_ordered[j][1])

            if _debug: print("step1", self._adj)
            if _debug: print("adj_pos", adj_v, adj_v_pos, mult)

            # add adj_v to the adjacencies of node_for_adding
            # self._adj[node][cur_node_pos:cur_node_pos + mult] = [(adj_v, adj_v_pos + mult - i) for i in range(mult)]
            for i in range(mult):
                self._add_single_endpoint((node, cur_node_pos + i), (adj_v, adj_v_pos + mult - i))
            if _debug: print("step2", self._adj)
            cur_node_pos += mult

    def remove_node(self, node):
        self.remove_arcs(self.incident_arcs(node))
        del self._node_attr[node]
        del self._adj[node]

    def remove_nodes(self, nodes):
        for v in nodes:
            self.remove_node(v)

    def remove_arc(self, arc):
        self.remove_arcs([arc])

    def _remove_single_endpoint(self, ep):
        _debug = False

        if _debug:
            print("  Removing", ep, "from", self._adj)

        v, v_pos = ep
        del self._adj[v][v_pos]
        # adjust change of position for all adjacent endpoints
        for adj_v, adj_v_pos in self._adj[v][v_pos:]:
            self._adj[adj_v][adj_v_pos] = (self._adj[adj_v][adj_v_pos][0], self._adj[adj_v][adj_v_pos][1] - 1)
        # adjust change of position in attributes
        #del self._endpoint_attr[ep]
        if _debug: print(" range", v_pos + 1, len(self._adj[v]))
        for i in range(v_pos + 1, len(self._adj[v])):
            self._endpoint_attr[(v, i-1)] = self._endpoint_attr[(v, i)]
        if len(self._adj[v]) > 0:
            del self._endpoint_attr[(v, len(self._adj[v])-1)]

    def remove_arcs(self, arcs):

        _debug = False

        if _debug:
            print()
            print("self", self, "arcs", arcs)

        endpoints = list(chain(*arcs))
        if _debug: print(endpoints)
        for i, ep in enumerate(endpoints):

            if _debug: print(ep,"in", self._adj)

            self._remove_single_endpoint(ep)

            v, v_pos = ep

            if _debug:
                print(i,ep,v,v_pos, endpoints)

            # adjust change of position for the rest of the endpoints in the list
            for j in range(i + 1, len(endpoints)):
                if endpoints[j][0] == v and endpoints[j][1] > v_pos:
                    if _debug: print("replacing", endpoints[j], "with", (endpoints[j][0], endpoints[j][1] - 1))
                    endpoints[j] = (endpoints[j][0], endpoints[j][1] - 1)


if __name__ == '__main__':
    """g = house_graph()
    print(g)
    print(g.number_of_connected_components())
    g.remove_arcs([((0,0),(1,0)),((1,1),(2,0)),((4,0),(3,2))])
    print(g)
    print(g.number_of_connected_components())"""

    g = PlanarGraph()
    g.add_node(0, degree=2)
    g.add_node(1, degree=3)
    g.add_node(2, degree=2)
    g.add_node(3, degree=3)
    g.add_node(4, degree=2)
    g.add_arc((0, 0), (1, 0))
    g.add_arc((1, 1), (2, 0))
    g.add_arc((2, 1), (3, 1))
    g.add_arc((3, 2), (4, 0))
    g.add_arc((4, 1), (0, 1))
    g.add_arc((1, 2), (3, 0))

    print(g)

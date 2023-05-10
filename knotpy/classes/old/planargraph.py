#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import Counter

from knotpy.classes.planardiagram import PlanarDiagram



__all__ = ['PlanarGraph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class PlanarGraph(PlanarDiagram):

    def __init__(self, incoming_planargraph_data=None, **attr):

        super().__init__(incoming_planar_data=None, **attr)

        if incoming_planargraph_data is not None:
            raise NotImplementedError()
            #convert.to_planardiagram(incoming_planargraph_data, create_using=self)

    def add_node(self, node_for_adding, degree=None, **attr):
        super()._add_node(node_for_adding=node_for_adding, degree=degree, **attr)

    def add_nodes_from(self, nodes_for_adding, degrees=None, **attr):
        super()._add_nodes_from(nodes_for_adding=nodes_for_adding, degrees=degrees, **attr)

    def set_arc(self, arc_for_setting , **attr):
        super()._set_arc(arc_for_setting=arc_for_setting, **attr)

    def set_arcs_from(self, arcs_for_adding, **attr):
        super()._set_arcs_from(arcs_for_adding=arcs_for_adding, **attr)



    # node operations



    def add_node_in_region(self, node_for_adding, region, connect_at_endpoints=tuple(), **attr):
        """Adds a node into the (center of the) region and connect the node to the other nodes in the region.
        :param node_for_adding: name of the node
        :param region:
        :param connect_at_endpoints: an iterable of nodes to connect, also a dictionary can be given,
        the keys are nodes and the values are multiplicities (how many parallel edges to the node)
        :param attr: node attribute
        :return: None
        TODO: find a way to add attributes to the newly created endpoints.
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

        self._add_node(node, degree=sum(multiplicity.values()), **attr)

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
                self._set_endpoint((node, cur_node_pos + i), (adj_v, adj_v_pos + mult - i))
            if _debug: print("step2", self._adj)
            cur_node_pos += mult


    def is_oriented(self):
        """Returns True if graph is directed, False otherwise."""
        return False



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
    g.set_arc(((0, 0), (1, 0)))
    g.set_arc(((1, 1), (2, 0)))
    g.set_arc(((2, 1), (3, 1)))
    g.set_arc(((3, 2), (4, 0)))
    g.set_arc(((4, 1), (0, 1)))
    g.set_arc(((1, 2), (3, 0)))


    print(g)

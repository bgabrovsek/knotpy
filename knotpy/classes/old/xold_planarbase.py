"""
The PlanarDiagram class provides a basic structure for all planar objects (planar graph, knots, knotted graphs,...).
Classes such as PlanarDiagram also include methods such as insert_arc_between_nodes(), which should not be used for
classes that represent e.g. knot diagrams. Therefore, this parent PlanarDiagram class is implemented.

A PlanarDiagram class consists of:
  - nodes (vertices), that are any hashable objects,
  - endpoints, that represent part of the edge/arc emanating from the node and is a tuple (node, node_position).
  - attributes, which are represented as dictionaries (keyed values) and are assigned to the planar graph itself,
    nodes, and endpoints.

In addition, we use the following terminology:
  - arcs are tuples of endpoints,
  - regions are the faces of the planar graph and are represented as a sequence of endpoints.
"""


from functools import cached_property, total_ordering
from itertools import chain
from copy import deepcopy

from knotpy.utils import lexicographical_minimal_cyclic_rotation_shift
from knotpy.classes.old.views import AttributeView, AdjacencyView

__all__ = ['PlanarBase']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


class _PlanarBaseCachedPropertyAdjResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od: del od["adj"]

class _PlanarBaseCachedPropertyNodeAttributeResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node_attr"] = value
        if "nodes" in od: del od["nodes"]

class _PlanarBaseCachedPropertyEndpointAttributeResetter:
    """For info on Data Descriptors see: https://docs.python.org/3/howto/descriptor.html"""
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_endpoint_attr"] = value
        if "endpoints" in od: del od["endpoints"]


@total_ordering
class PlanarBase:
    """
    Planar (diagram) base class. This class is intended to be used only as the parent class for PlanarDiagram, etc.
    It includes common methods used by all planar structures (planar graph diagrams, knot diagrams,...).
    """

    _adj = _PlanarBaseCachedPropertyAdjResetter()
    _node_attr = _PlanarBaseCachedPropertyNodeAttributeResetter()
    _endpoint_attr = _PlanarBaseCachedPropertyEndpointAttributeResetter()

    graph_attr_factory = dict
    node_attr_outer_factory = dict
    node_attr_inner_factory = dict
    adj_outer_factory = dict
    adj_inner_factory = list
    endpoint_attr_outer_factory = dict
    endpoint_attr_inner_factory = dict

    def __init__(self, incoming_planar_data=None, **attr):
        """Initialize a base graph
        :param incoming_planar_data:
        :param attr:
        """
        """Initialize with ..., or planar diagram attributes (name, ...)"""

        self.attr = self.graph_attr_factory()  # store graph attributes (without a View)
        self._node_attr = self.node_attr_outer_factory()  # dictionary of node attributes
        self._endpoint_attr = self.endpoint_attr_outer_factory()  # dictionary of endpoint attributes
        self._adj = self.adj_outer_factory()  # dictionary of lists of endpoints in CCW order

        # no data
        if incoming_planar_data is not None:
            raise ValueError("PlanarDiagram class should not be called with planar initialization data.")

        self.attr.update(attr)

    def __deepcopy__(self, memo):
        """Return a deep copy of self."""
        # TODO: read memo documentation
        new_g = self.__class__()
        new_g._adj = deepcopy(self._adj, memo)
        new_g.attr = deepcopy(self.attr, memo)
        new_g._node_attr = deepcopy(self._node_attr, memo)
        new_g._endpoint_attr = deepcopy(self._endpoint_attr, memo)
        return new_g

    # cached properties

    @cached_property
    def adj(self):
        """Graph adjacency object holding the neighbors of each node."""
        return AdjacencyView(self._adj)
        pass

    @cached_property
    def nodes(self):
        """Graph node object holding the attributes of each node."""
        return AttributeView(self._node_attr)

    @cached_property
    def endpoints(self):
        """Graph endpoint object holding the attributes of endpoint."""
        return AttributeView(self._endpoint_attr)

    # set, insert and remove operations

    # node operations

    def _add_node(self, node_for_adding, degree=None, **attr):
        """Add a single node 'node_for_adding' and update the node attributes.
        :param node_for_adding: the node, that can be any hashable object, except None
        :param attr: keyword arguments, optional
        :param degree: reserve entries for endpoints
        :return: None
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

    def _add_nodes_from(self, nodes_for_adding, degrees=None, **args):
        """Add a bunch (iterable) of nodes.
        :param nodes_for_adding: iterable of nodes
        :param degrees: reserve entries for endpoints
        :return: None
        """
        if degrees is not None and len(nodes_for_adding) != len(degrees):
            raise ValueError("The number of nodes should match the number of degrees.")

        if degrees is None:
            for node in nodes_for_adding:
                self._add_node(node, **args)
        else:
            for node, degree in zip(nodes_for_adding, degrees):
                self._add_node(node, degree, **args)

    def _remove_node(self, node_for_removing, remove_incident_arcs=True):
        if remove_incident_arcs:
            self._remove_arcs_from(self.incident_arcs(node_for_removing))
        del self._node_attr[node_for_removing]
        del self._adj[node_for_removing]

    def _remove_nodes_from(self, nodes_for_removal, remove_incident_arcs=True):
        for v in nodes_for_removal:
            self._remove_node(v, remove_incident_arcs)

    # endpoint operations

    def _set_endpoint(self, endpoint_for_setting, adjacent_endpoint, **attr):
        """Set the endpoint (v, v_pos) to value the value of adjacent_endpoint and adds the attributes.
        If v_pos < degree(v), overwrite the adjacent endpoint, otherwise expand the table of adjacent endpoints with
        "None" (so that degree(v) = v_pos+1) and overwrite the last None element in the table.
        :param endpoint: tuple representing the endpoint to modify
        :param adjacent_endpoint: overwrite the endpoint with adjacent_endpoint
        :param attr: additional attributes of the endpoint
        :return: None
        """

        v, v_pos = endpoint_for_setting

        if v not in self._node_attr:
            self._add_node(v)

        # make space is position is larger than node degree
        if v_pos >= len(self._adj[v]):
            self._adj[v] += [None] * (v_pos - len(self._adj[v]) + 1)  # assume adj_inner_factory is a list
        self._adj[v][v_pos] = adjacent_endpoint

        if endpoint_for_setting not in self._endpoint_attr:
            self._endpoint_attr[endpoint_for_setting] = self.endpoint_attr_inner_factory()

        self._endpoint_attr[endpoint_for_setting].update(attr)

    def _insert_endpoints_to_node(self, node_for_inserting, position, endpoints):
        """Insert endpoints to node. Shifts all endpoint indices by len(endpoints).
        For example, if node n has endpoints ((a, pos_a), (b, pos_b),...) calling the method with position=1,
        shifts the endpoints to ((a, pos_a), (endpoints[0]), (endpoints[1]),..., (b, pos_b),...
        The method takes care of repositioning the adjacent endpoints of the node.
        Also, we must be careful that the endpoints list is consistent with the global graph structure.
        :param node_for_inserting: existing node to modify
        :param position: the position (index) of inserting new endpoints to node
        :param endpoints: a list of new endpoints of node in CCW order
        :return:
        """

        shift = len(endpoints)
        node = node_for_inserting

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

        # TODO: use self._permute_node_positions

    def _remove_endpoint(self, endpoint_for_removal):
        _debug = False

        if _debug:
            print("  Removing", endpoint_for_removal, "from", self._adj)

        v, v_pos = endpoint_for_removal
        del self._adj[v][v_pos]
        #TODO: use self._permute_node_positions
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

    # arc operations

    def _set_arc(self, arc_for_setting , **attr):
        """Set the arc (v_endpoint, u_endpoint), which equals setting the two endpoints
        adj(u_endpoint) = v_endpoint and vice-versa."""
        v_endpoint, u_endpoint = arc_for_setting
        self._set_endpoint(tuple(v_endpoint), tuple(u_endpoint), **attr)
        self._set_endpoint(tuple(u_endpoint), tuple(v_endpoint), **attr)

    def _set_arcs_from(self, arcs_for_adding, **attr):
        """Set the list of arcs.
        :param arcs_for_adding: a sequence of tuples (v_endpoint, u_endpoint)
        :return: None
        """
        for arc in arcs_for_adding:
            self._set_arc(arc, **attr)

    def _remove_arc(self, arc_for_removing):
        self._remove_arcs_from([arc_for_removing])

    def _remove_arcs_from(self, arcs_for_removing):

        _debug = False

        if _debug:
            print("self", self, "arcs", arcs_for_removing)

        endpoints = list(chain(*arcs_for_removing))
        if _debug: print(endpoints)
        for i, ep in enumerate(endpoints):

            if _debug: print(ep, "in", self._adj)

            self._remove_endpoint(ep)

            v, v_pos = ep

            if _debug:
                print(i, ep, v, v_pos, endpoints)

            # adjust change of position for the rest of the endpoints in the list
            for j in range(i + 1, len(endpoints)):
                if endpoints[j][0] == v and endpoints[j][1] > v_pos:
                    if _debug: print("replacing", endpoints[j], "with", (endpoints[j][0], endpoints[j][1] - 1))
                    endpoints[j] = (endpoints[j][0], endpoints[j][1] - 1)


    def rename_nodes(self, node_reindex_dict=None):
        """Rename the nodes according to dictionary reindex_dict. If no dictionary provided, the function will
        rename the nodes using natural numbers, 0, 1,...,n.
        :param node_reindex_dict:
        :return: None
        """

        if node_reindex_dict is None:
            node_reindex_dict = dict(zip(sorted(self._adj), range(len(self))))

        # assume factories are dicts, TODO: take factory classes
        self._node_attr = {node_reindex_dict[v]: self._node_attr[v] for v in self._node_attr}
        self._endpoint_attr = {(node_reindex_dict[ep[0]], ep[1]): self._endpoint_attr[ep] for ep in self._endpoint_attr}
        self._adj = {node_reindex_dict[v]: [(node_reindex_dict[u], pos) for u, pos in self._adj[v]] for v in self._adj}

    # constructed entities from primary entities (_node, _adj,...)

    def arc_iterator(self):
        """Iterates over all arcs (pairs of endpoints)."""
        for ep0 in self._endpoint_attr:
            ep1 = self._adj[ep0[0]][ep0[1]]
            if ep0 < ep1:
                yield ep0, ep1

    def arcs(self) -> list:
        """Returns the list of arcs, each arc is a tuple (endpoint, adjacent endpoint)."""
        return [arc for arc in self.arc_iterator()]

    def incident_arcs(self, node) -> list:
        return [((node, pos), ep) for pos, ep in enumerate(self._adj[node])]

    def regions(self):
        """
        Return regions (planar graph faces) of a planar graph.
        First it puts all endpoints (vertex, position) to a set, then selects an unused and  travels along the edges
        until no endpoints are left.
        :return: a set of n-tuples, each n-tuple consists of the endpoints of the region.
        """
        # TODO: change this to a cached property

        unused_endpoints = set(self._endpoint_attr)  # TODO: use view?
        regions = list()
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
        # implement as a view, if needed
        if v is None:
            return {v: len(self._adj[v]) for v in self._adj}
        return len(self._adj[v])

    # canonical modifiers

    def _permute_node_positions(self, node, permutation=None, ccw_shift=None):
        """Permute or rotate the positions of node and take care of adjacent nodes. For example, if we rotate a 4-valent
        node by 90 degrees, ccw_shift = 1 and the positions change from (0, 1, 2, 3) to (3, 0, 1, 2), so the permutation
        should be {0: 3, 1: 0, 2: 1, 3: 2}, alternatively, we can provide ccw_shift=1.
        Should be used with case, since it does not take care of removing access endpoint attributes when permuting node
        positions when adding or removing a new arc or edge.
        :param node:
        :param permutation:
        :param ccw_shift:
        :return:
        """
        # TODO: make faster

        if (permutation is None) == (ccw_shift is None):  # xnor
            raise ValueError("Either a permutation or ccw shift must be given.")

        an = self._adj[node]
        p = permutation if ccw_shift is None else {i: (i - ccw_shift) % len(an) for i in range(len(an))}

        # take care of adjacent vertices
        for pos, (adj_node, adj_pos) in enumerate(an):
            self._adj[adj_node][adj_pos] = (node, p.get(pos, pos))

        # permute the node
        self._adj[node] = [an[p.get(i, i)] for i in range(len(an))]

        # take care of endpoint attributes
        self._endpoint_attr.update({(node, p[pos]): self._endpoint_attr[(node, pos)] for pos in p})

    def _canonically_rotate_node(self, node):
        """
        :param node:
        :return:
        """
        shift = lexicographical_minimal_cyclic_rotation_shift(self._adj[node])
        self._permute_node_positions(node, ccw_shift=-shift)  # TODO: test
    # overrides

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

    def is_oriented(self):
        """Returns True if graph is directed, False if not, None if indetermined."""
        return None

    def is_directed(self):
        """Returns True if graph is directed, False otherwise."""
        return self.is_oriented()


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
        return str(self.adj).replace(" ","")


    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with {self.number_of_nodes} nodes, {self.number_of_arcs} arcs,",
                f" and adjacencies " + str(self.adj) if len(self.adj) else f" and no adjacencies"
            ]
        )


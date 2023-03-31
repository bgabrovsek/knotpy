from crossing import *
from equivalence import *
from combinatorics import *
from copy import deepcopy
from random import sample, shuffle
from queue import Queue
from collections import defaultdict

DEFAULT_ARC_COLOR = 0

class Knotted():
    """
    A class of an oriented spatial (knotted, embedded) graphs
    """

    #######################
    # BASIC CLASS METHODS #
    #######################

    def __init__(self, nodes=None, framing=0, unknots=0, name='', coloring = None):
        """
        Spatial graph initialization.
        :param nodes: list of nodes (e.g. [crossing_1, crossing_2, vertex_3, vertex_4,...]
        :param framing: integer representing the framing sum
        :param unknots: number of disconnected unknot components
        :param name: optional knot name, can be anything
        :param coloring: dictionary arc -> color
        """
        """Initialize"""
        if coloring == None:
            raise ValueError("Knot initialized without coloring.")
            coloring = None

        self.framing, self.unknots, self.name, self.coloring = framing, unknots, name, coloring
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

        self.clean_coloring()

    def copy(self):
        """Returns a (deep) copy of self"""
        return deepcopy(self)

    def copy_to_self(self, K):
        self.framing, self.unknots, self.name, self.coloring = K.framing, K.unknots, K.name, K.arc_color
        self.nodes = K.nodes

    def __len__(self):
        """ returns number of nodes """
        return len(self.nodes)

    def __delitem__(self, key):
        """removes either node key or node at index key"""
        if isinstance(key, NodePrototypeClass):
            self.nodes = [node for node in self.nodes if node is not key]
        else:
            del self.nodes[key]

        self.clean_coloring()

    def __getitem__(self, item):
        return self.nodes[item]

    def hash(self):
        t = tuple(node.hash() for node in self.nodes)
        return hash(t)

    ##############
    # COMPARISON #
    ##############

    def __lt__(self, other):

        if (len(self), self.framing, self.unknots) < (len(other), other.framing, other.unknots): return True
        if (len(self), self.framing, self.unknots) > (len(other), other.framing, other.unknots): return False

        if self.color_tuple() < other.color_tuple(): return True
        if self.color_tuple() > other.color_tuple(): return False

        for self_node, other_node in zip(self.nodes, other.nodes):
            if self_node < other_node: return True
            if self_node > other_node: return False

        return False

    def __eq__(self, other):
        if (len(self), self.framing, self.unknots) != (len(other), other.framing, other.unknots):
            return False

        if self.color_tuple() != other.color_tuple(): return False

        for self_node, other_node in zip(self.nodes, other.nodes):
            if self_node != other_node: return False

        return True

    def __le__(self, other):
        return self < other or self == other

    #########
    # NODES #
    #########

    def filter_nodes(self, condition=lambda c: True):
        """
        return sublist of nodes
        :param condition: filter function on nodes
        :return: list of nodes with condition true
        """
        return [node for node in self.nodes if condition(node)]


    def filter_nodes_index(self, condition=lambda c: True):
        """
        return sublist of indices of nodes
        :param condition: filter function on nodes
        :return: list of indices nodes with condition true
        """
        return [i for i, node in enumerate(self.nodes) if condition(node)]


    def split_nodes(self, criteria=lambda c: len(c)):
        """
        splits nodes by criteria, default is by length
        :param criteria: criteria function property of a node
        :return: dictionary {A: nodes with criteria A, B: nodes with criteria B,...}
        """
        return {c: [node for node in self.nodes if criteria(node) == c] \
                for c in set(criteria(node) for node in self.nodes)}

    def permute_nodes(self, p):
        """
        permutes the nodes,e.g. [A,B,C,D] permuted by [3,1,2,4] returns [C,A,B,D]
        :param p: permutation list
        """
        self.nodes = [self[i] for i in p]

    def remove_node(self, *nodes):
        """
        just remove the nodes, without considering consequences
        :param noded: single or multiple argument of nodes
        """
        self.nodes = [node for node in self.nodes if node not in nodes]
        self.clean_coloring()

    def append_node(self, coloring, *nodes):
        """
        appends nodes to current list of nodes
        :param coloring: new (additional coloring function)
        :param nodes: single or multiple argument nodes
        """
        for node in nodes:
            self.nodes.append(node)
        self.coloring = merge_dictionaries(self.coloring, coloring)

    def pop_nodes(self, n):
        """
        pops last n nodes
        :param n: number of nodes to be removed
        :return: returns the removed nodes
        """
        ret, self.nodes = self.nodes[-n:], self.nodes[:-n]
        return ret

    def degrees(self):
        """
        :return: set of degrees of vertices
        """
        return set(len(node) for node in self.nodes)


    def count_deg(self, degree):
        """
        :param degree: node degree
        :return: return number of nodes of degree gerdee
        """
        return sum(1 for node in self.nodes if len(node) == degree)


    def terminus_nodeQ(self, node, pos):
        """
        is node an endpoint?
        :param pos: position of arc inside node
        :return: True/False
        """
        #print(XQ(node),node,pos)
        #print(self)
        #print(self.coloring)
        #print(self.coloring[node[pos]])
        #print([self.coloring[arc] for arc in node.arcs].count(self.coloring[node[pos]]))
        # no endpoint if we're at a crossing or we have two same-colored arcs in node
        return (not XQ(node)) and [self.coloring[arc] for arc in node.arcs].count(self.coloring[node[pos]]) != 2





    def pop_bond_arc(self):
        """ pop a bond w/o crossings"""
        nds = self.filter_nodes(VQ)
        shuffle(nds)
        for node in nds:
            arc = (set(node.arcs) & self.colored_arcs()).pop() # pop an arc from the node that has color
            (cr0, pos0), (cr1, pos1) = self.D(arc)
            if cr0[pos0] == cr1[pos1]: # does the arc have crossings?
                return arc, cr0.color[pos0]

        return None

    def parallel_bond_arcQ(self, arc):
        """ is the bond parallel? """
        (cr0, pos0), (cr1, pos1) = self.D(arc)

        if not self.coloring[arc]:
            raise ValueError("Cannot determine parallelity of uncolored arc.")
        if cr0[pos0] != cr1[pos1]:
            raise ValueError("Parallelity of a bon-bond arc not implemented.")
        if XQ(cr0) or XQ(cr1):
            raise ValueError("Cannot determine parallelity of non-isolated bond")

        return cr0.inQ(cr0.CCW(pos0)) != cr1.inQ(cr1.CCW(pos1))

    def remove_bivalent_nodes(self):
        """ removes all bivalent vertices"""
        arc_eqiv = equivalence() # arcs as equivalent classes
        biv_nodes = self.filter_nodes(BQ)
        arc_count = defaultdict(lambda: 0) # count how many times arc appears in bivalent nodes

        for node in biv_nodes:
            in_arc, out_arc = node.arcs
            arc_count[in_arc] += 1
            arc_count[out_arc] += 1
            arc_eqiv[in_arc] = out_arc

        # count closed loops formed by bivalent nodes
        for eq_class in arc_eqiv:
            if all(arc_count[arc] == 2 for arc in eq_class):
                self.unknots += 1

        renum = {x: eq_class[0] for eq_class in arc_eqiv for x in eq_class}
        self.nodes = [node for node in self.nodes if not BQ(node)]
        self.renumerate_arcs(renum)
        self.clean_coloring()


    def mirror(self):
        # mirrors self
        for node in self.nodes:
            if XQ(node):
                node.mirror()

    #########
    # COLOR #
    #########

    def color_tuple(self):
        """
        :return: puts coloring info in a tuple
        """
        if len(self.coloring) == 0: return tuple()
        return tuple((None, self.coloring[arc])[arc in self.coloring] for arc in range(max(self.coloring) + 1))


    def clean_coloring(self):
        """ Removes arcs not in use"""
        new_coloring = dict()
        for arc in self.arcs():
            new_coloring[arc] = self.coloring[arc]
        self.coloring = new_coloring

    def merge_colorings(self, new_colors):
        """ appends new arc coloring to existing one """
        for arc in new_colors:
            if arc in self.coloring and new_colors[arc] != self.coloring[arc]:
                raise ValueError("New node color mismatch.")

    def colored_arcs(self):
        """ return a set of arcs that have color """
        return {arc for arc in self.coloring if self.coloring[arc]}

    def color_set(self):
        """
        return all existing colors as a set
        """
        return set(self.coloring.values())
        # return {self.coloring[arc] for arc in self.color}

    def coloredQ(self):
        return len(self.color_set()) > 1

    def color(self, arc):
        return self.coloring[arc]

    def color_dict(self, arc_subset=None):
        """ return a dictionary color -> set of arcs """
        return {color: {arc for arc in self.coloring
                        if (self.coloring[arc] == color) and ((arc_subset is None) or (arc in arc_subset))}
                for color in self.color_set()}

    def renumerate_colors(self, perm):
        """ renumerate coloring dictionary if arcs are renumerated"""
        # e.g. perm = [0:2, 1:0, 2:1] renumerates arc 0 -> 2, arc 1 -> 0, arc 2 -> 1"""
        old_coloring = dict(self.coloring)
        for old_arc in perm:
            self.coloring[perm[old_arc]] = old_coloring[old_arc]



    ########
    # ARCS #
    ########

    def arcs(self, color = None):
        """Returns a set of all arcs (of color color)"""
        if color is None:
            return union(*(node.arcs for node in self.nodes))
        else:
            return {arc for arc in self.coloring if self.coloring[arc] == color}

    def sorted_arcs(self):
        """Returns a list of all arcs, sorted"""
        return sorted(self.arcs())

    def updated(self):
        """ not implemented, update is called if knot has changed."""
        pass


    def D(self, arc, ignore_orientation = False):
        """
        Return the two endpoints of an arc from start to end (if orientation not ignored)
        :param arc: arc in question
        :param ignore_orientation: if True arc order does not matter (e.g. used for orientation-broken knots)
        :return: (start node, position of arc), (end node, position of arc)
        """
        # TODO: make faster, since this function is called very often

        #print("D",arc,ignore_orientation)

        node_pos = [(node, pos) for node in self.nodes for pos in node if node[pos] == arc]
        if not ignore_orientation and node_pos[0][0].inQ(node_pos[0][1]):  # if 1st node ingoing then reverse
            node_pos.reverse()

        # just a check everything is OK (remove for release version)
        if not ignore_orientation and node_pos[0][0].inQ(node_pos[0][1]) == node_pos[1][0].inQ(node_pos[1][1]) or len(node_pos) != 2:
            raise ValueError("More than two adjacent nodes or orientation mismatch.")

        return tuple(node_pos)

    def adjacent_node(self, node, pos):
        """
        search for adjacent node
        :param node: current node
        :param pos: position of arc in current node
        :return: adjacent pair (node, position)
        """
        nps = self.D(node[pos], ignore_orientation=True)
        return nps[1 - nps.index((node, pos))]  # return the pair that is not the one from the argument

    def adjacent_pos(self, node, pos):
        """
        returns the adjacent arc if the arc is not and endpoint
        :param node: the node in question
        :param pos: position of arc in node
        :return: adjacent arc of node node
        """
        if XQ(node):
            return (pos + 2) % 4  # if node is crossing

        # get the positions with the same color as arc node[pos]
        pos_same_color = [p for p in node if self.coloring[node[p]] == self.coloring[node[pos]] and pos != p]

        if len(pos_same_color) != 1:
            raise ValueError("More than two arcs from node with same color.")

        return pos_same_color[0]


    def middleQ(self, arc):
        """is arc connected by two Crossings?"""
        (cr0, pos0), (cr1, pos1) = self.D(arc)
        return not (XQ(cr0) ^ XQ(cr1))

    def alternatingQ(self, arc):
        """returns True if arc is alternating (false if not middle arc)"""
        (cr0, pos0), (cr1, pos1) = self.D(arc)
        if not XQ(cr0) or not XQ(cr1): return False # should an exception be made?
        return cr0.overQ(pos0) ^ cr1.overQ(pos1)

    def non_alternatingQ(self, arc):
        """returns False if arc is alternating (false if not middle arc)"""
        (cr0, pos0), (cr1, pos1) = self.D(arc)
        if not XQ(cr0) or not XQ(cr1): return False # should an exception be made?
        return cr0.overQ(pos0) == cr1.overQ(pos1)

    def bondQ(self, arc):
        """Is arc a short bond?"""
        if not self.coloring[arc]:
            return False
        (cr0, pos0), (cr1, pos1) = self.D(arc)
        # return not (VQ(cr0) ^ VQ(cr1)) WHY?!?
        return VQ(cr0) and VQ(cr1)

    def bondedQ(self):
        """ is the knot bondless"""
        return not all(XQ(node) for node in self.nodes)


    def loopQ(self, arc):
        """Is arc a loop?"""
        (cr0, pos0), (cr1, pos1) = self.D(arc)
        #print(arc, cr0, cr1)
        return cr0 == cr1

    def D_index(self, arc):
        """same as D, except returns an index of the node, not the node itself, tiny bit slower"""
        node_pos = [(None,None),(None,None)]
        for node_ind, node in enumerate(self.nodes):
            for pos in node: # loop through positions
                if node[pos] == arc:
                    #print("  ", node_ind, pos, node.inQ(pos))
                    node_pos[node.inQ(pos)] = node_ind, pos
        return tuple(node_pos)


    def adjacent_arcs(self, arc, distance = 1):
        """ returns arcs of distance """
        arcs = set()
        if distance == 1:
            (c0,p0), (c1, p1) = self.D(arc)
            for p in c0:
                if p != p0:
                    arcs.add(c0[p])
            for p in c1:
                if p != p1:
                    arcs.add(c1[p])
        else:

            for a in self.adjacent_arcs(arc, distance-1):
                arcs = arcs | self.adjacent_arcs(a, 1)

        return arcs


    def hash_arc_adjacency(self, distance=1):
        if distance == 1:
            return tuple(len(self.adjacent_arcs(a, 1)) for a in self.sorted_arcs())
        else:
            return tuple(tuple(len(self.adjacent_arcs(a, d)) for d in range(1,distance+1)) for a in self.sorted_arcs())


    def next_arc_forward(self, arc):
        """returns the next arc in orientation"""

        #print("next",arc)

        # check if we are in an endpoint
        if self.terminusQ(arc):  # This check is slow and unnecessary (remove after debugging)
            raise ValueError("Cannot move beyond an endpoint.")

        # continue along arc
        node1, pos1 = self.D(arc)[1]  # get end node index

        if XQ(node1) or VQ(node1):
            return node1[node1.move_forward(pos1)]
        else:
            raise TypeError("Unknown node type.")

    def previous_arc_backward(self, arc):
        """returns the next arc in orientation"""

        # check if we are in an endpoint
        if self.terminusQ(arc, reverse=True):  # This check is slow and unnecessary (remove after debugging)
            raise ValueError("Cannot move before a startpoint.")

        # continue along arc backward
        node0, pos0 = self.D(arc)[0]  # get end node index

        if XQ(node0) or VQ(node0):
            return node0[node0.move_backward(pos0)]
        else:
            raise TypeError("Unknown node type.")


    def terminusQ(self, arc, reverse = False):
        """ is the endpoint of arc a terminal point in the graph? if reverse = True, check if the arc start is a start point in a graph"""
        node, pos = self.D(arc)[0 if reverse else 1]  # get end node index
        #print(node_ind1, pos1)
        return VQ(node) and len(self.color_dict(node.arcs)[self.coloring[arc]]) == 1


    def split_arc(self, arc):
        """ Split arc by bivalent vertex, ---- => --B--
        Returns the new node"""
        new_arc = max(self.arcs()) + 1
        crossing_in, pos_in = self.D(arc)[1]
        crossing_in.renumerate_arc_by_position(pos_in, new_arc)
        B_node = Bivalent(in_arc=arc, out_arc=new_arc)
        self.nodes.append(B_node, {new_arc:self.coloring[arc]})  # new arc color same as old arc
        return B_node


    def reverse_arc(self, arc):
        """reverse arc without considering consequences"""
        if isinstance(arc, list) or isinstance(arc, tuple):
            for a in arc:
                self.reverse_arc(a)
        else:
            (c0,p0), (c1,p1) = self.D(arc)
            if not (VQ(c0) and VQ(c1)): raise ValueError("Cannot reverse crossing arc.")
            c0.reverse_arc(p0)
            c1.reverse_arc(p1)


    ##############
    # COMPONENTS #
    ##############


    def components(self):
        """Returns a list of components, i.e. list of arcs in each connected component.
        The criteria for two arcs to lie in the same component is that they are the same color and share a vertex."""

        arc_equiv = equivalence() # components are stored as equivalence classes

        for node in self.nodes:
            if XQ(node): # is current node a crossing?
                # arcs on opposite sides are in the same class
                arc_equiv[node.arcs[0]] = node.arcs[2]
                arc_equiv[node.arcs[1]] = node.arcs[3]
            elif VQ(node):
                # arcs of the same color are in the same class
                for arcs in self.color_dict(arc_subset=node.arcs): #node.color_dict().values():
                    arc_equiv += arcs # arcs belong to same eqiv. class
            else:
                raise TypeError("Unsupported node type.")

        return arc_equiv.get_classes() + [[] for x in range(self.unknots)]


    def split_components(self):
        """Similar to components, except that we split closed components (knots) and open components (bands)"""
        all_components = self.components()
        open_components = []
        for v in self.filter_nodes(VQ):
            terminal_arcs = v.terminal_arcs()
            open_components += [c for c in all_components if set(terminal_arcs) & set(c)]
        closed_components = [c for c in all_components if c not in open_components]

        if len(closed_components) + len(open_components) != len(all_components):
            raise ValueError("Cannot separate closed and open components.")
        return closed_components, open_components


    def path(self, arc):
        """same-color path that follows an arc,
        if arc lies on a knot, returns the ordered sequence of arcs along the knot component starting from arc,
        if arc lies on a bond, returns the ordered sequence arcs on that bond"""
        next_arc, arc_path = arc, [arc]
        number_of_arcs = len(self.arcs())
        while True:
            #print(arc_path)
            if self.terminusQ(next_arc):
                break

            next_arc = self.next_arc_forward(next_arc)
            if next_arc == arc:
                break

            arc_path.append(next_arc)

            if len(arc_path) > number_of_arcs:
                raise ValueError("Arc path error" + str(self))

        return arc_path

    def connected_components(self, return_equivalence_class = False):
        """Returns list of arcs of connected components"""
        arc_equiv = equivalence()  # components are stored as equivalence classes
        for node in self.nodes:
            if XQ(node):  # is current node a crossing?
                arc_equiv[node.arcs[0]] = node.arcs[2]
                arc_equiv[node.arcs[1]] = node.arcs[3]
            elif VQ(node):
                for arc in node.arcs[1:]: arc_equiv[node.arcs[0]] = arc  # all arcs are connected
            else:
                raise TypeError("Unsupported node type.")
        if return_equivalence_class:
            return arc_equiv
        return arc_equiv.get_classes() + [[] for u in range(self.unknots)]


    def disjoin(self):
        # expand knot into its disjoint sum components
        # does not make a copy od the nodes, since they are used one per component

        if len(self) == 0:
            return [Knotted(unknots=1, framing=self.framing, coloring=dict(self.coloring))] \
                   + [Knotted(unknots=1, framing=0, coloring=dict(self.coloring)) for i in range(self.unknots-1)]

        eq_component_arcs = self.connected_components(return_equivalence_class=True) # equivalence class structure of arcs on the same component

        if len(eq_component_arcs) == 1:

            if len(self):
                unknots, self.unknots = self.unknots, 0
                return [self] + [Knotted(unknots=1, framing=0, coloring=dict(self.coloring)) for i in range(unknots)]
            else:
                # this should not occur
                return  [Knotted(unknots=1, framing=self.framing, coloring=dict(self.coloring))] \
                        + [Knotted(unknots=1, framing=0,coloring=dict(self.coloring)) for i in range(self.unknots-1)]


        # join components that are interlocked by two different crossing types (over and under)
        for (arcs0, arcs1) in combinations(eq_component_arcs, 2):
            common_nodes = [node for node in self.nodes if
                            (not set(node.arcs).issubset(set(arcs0))) and \
                            (not set(node.arcs).issubset(set(arcs1))) and \
                            (set(node.arcs).issubset(set(arcs0) | set(arcs1)))]

            common_over_arcs = {arc for node in common_nodes for arc in node.over_arc_set()}
            common_under_arcs = {arc for node in common_nodes for arc in node.under_arc_set()}

            if common_over_arcs.issubset(set(arcs0)) and common_under_arcs.issubset(set(arcs1)) or \
                common_over_arcs.issubset(set(arcs1)) and common_under_arcs.issubset(set(arcs0)):
                pass
            else:
                eq_component_arcs[arcs0[0]] = arcs1[0]

        if len(eq_component_arcs) == 1:
            if len(self):
                unknots, self.unknots = self.unknots, 0
                return [self] + [Knotted(unknots=1, framing=0, coloring=dict(self.coloring)) for i in range(unknots)]
            else:
                # this should not occur
                return [Knotted(unknots=1, framing=self.framing, coloring=dict(self.coloring))] \
                       + [Knotted(unknots=1, framing=0, coloring=dict(self.coloring)) for i in
                                                                     range(self.unknots - 1)]



        # split link into a list of knots (or links)
        components = []
        for arcs in eq_component_arcs:

            K = Knotted()

            for node in self.nodes:

                if set(node.arcs).issubset(set(arcs)):
                    K.nodes.append(node)  # node is fully contained inside component
                elif set(node.arcs) & set(arcs):  # node is partially contained inside component
                    arc_in, = node.in_arc_set() & set(arcs)
                    arc_out, = node.out_arc_set() & set(arcs)
                    K.nodes.append(Bivalent(in_arc=arc_in, out_arc=arc_out))

            K.remove_bivalent_nodes()

            if K.nodes != [] and K.unknots > 0:
                raise ValueError("Did not expect nodes with extra components. Need to implement.")
            if K.unknots > 1:
                raise ValueError("Did not expect multiple unknots. Need to implement splitting.")

            components.append(K)

            # TODO: check if new components have unknots and other components


        #print(self, len(components),components)
        components[0].framing = self.framing # add framing to the 1st component

        components += [Knotted(unknots=1, coloring=dict(self.coloring)) for i in range(self.unknots)]

        return components


    def connected_sumQ(self):
        """ ss the knot a connected sum?"""
        areas = self.areas()
        area_sets = [{a for a, b in area} for area in areas]
        for a, b in combinations(area_sets,2):
            if len(a & b) >= 2:
                return True
        return False


    def over_paths(self):
        """ returns list of over-paths"""
        paths = []

        for node in self.filter_nodes(XQ):
            path = [node[2]]
            while True:
                cr, pos = self.D(path[-1])[1]
                if cr.underQ(pos): break # quit if undercrossing
                path.append(cr[cr.move_forward(pos)]) # append next arc
            paths.append(path)
        return paths

    #########
    # AREAS #
    #########


    def areas(self):
        """Returns areas of the knot diagram.
        An area is a sequence of tuples (arc, bool), where bool is True if arc oriented CCW."""
        areas = equivalence()

        for node in self.nodes:
            for position in node:
                right_position = (position+1) % len(node)  # TODO: implement mode_right on all crossing types
                areas[2*node[position] + int(node.outQ(position))] = 2*node[right_position] + int(node.inQ(right_position))

        return [[(n//2, bool(n%2)) for n in c] for c in areas.get_classes()]


    def CCW_areas(self):
        """ similar to areas, except that the arcs are ordered CCW wrt area, slower than areas()"""
        #print("CCW",self)
        new_areas = []
        for area in self.areas():
            #print("area", area)
            arc0, dir0 = min(area)
            arc, dir = arc0, dir0
            new_area = []
            while True:
                new_area.append((arc,dir))
                #print(self,arc, self.D(arc))
                c, p = self.D(arc)[dir]
                arc, dir = c[c.CW(p)], c.outQ(c.CW(p))
                if arc == arc0 and dir == dir0: break

            new_areas.append(new_area)
        return new_areas

    def bridgeQ(self):
        """ does the knot have a bridge?"""
        for area in self.areas():
            arcs = [a for a, side in area]
            if len(arcs) != len(set(arcs)):
                return True

        return False

    def bridge_crossingQ(self):
        for area in self.areas():
            arcs = set([a for a, side in area])
            for node in self.nodes:
                if node.arc_set().issubset(arcs):
                    return True
        return False


    ##################
    # CANONICAL FORM #
    ##################


    def orientations(self):
        """ for a link, return list of all possible orientations"""

        knots = []

        #print("ORIENT.",self)

        for comps in powerset(self.components()):
            K = self.copy()

            #print("    O", K)

            #print("   ", comps)
            for arc in union(*comps):  #loop through arcs to reverse
                (node0_, pos0), (node1_, pos1) = self.D(arc)
                node0 = K[self.nodes.index(node0_)]
                node1 = K[self.nodes.index(node1_)]
                #print("   rev", node1, pos1, "arc",arc)
                node1.reverse_arc(pos1)
                #print("   -->", node1, pos1, "arc",arc)

                if VQ(node0) and node0.terminusQ(pos0):
                    node0.reverse_arc(pos0)
                    #print("   rev", node0, pos0, "arc", arc,"terminus")
            #print("  result", K)
            knots.append(K)
        return knots


    def renumerate_arcs(self, perm):
        """Renumerate arcs by permutation given by a dictionary,
        e.g. perm = [0:2, 1:0, 2:1] renumerates arc 0 -> 2, arc 1 -> 0, arc 2 -> 1"""
        for node in self.nodes:
            node.renumerate_arcs(perm)
        self.renumerate_colors(perm)

    def sort(self):
        """ puts crossings in canonical form and sorts the crossings"""
        # TODO: COLOR include here ?
        for node in self.nodes:
            node.canonical()

        self.nodes = sorted(self.nodes)


    def simple_canonical(self):
        """
        puts self nodes in canonical fomr
        """
        for node in self.nodes:
            node.canonical()
        self.nodes.sort()

    def canonical(self):
        """
        puts knot in canonical form using breadth-first search
        does not work for two or more components
        :return: knot in canonical form (leaves self unchanged)
        """

        if not len(self): return self.copy()

        minimal_knot = self.copy()  # current minimal knot

        # select starting arcs as ingoing underarcs of negative crossings (or positive if no negative)
        for X in [XmQ, XpQ]:
            starting_arcs = [node[0] for node in self.filter_nodes(X)]
            if starting_arcs: break

        if not starting_arcs: starting_arcs = self.arcs()  # if there are no crossings, any arc can be starting

        for start_arc in starting_arcs:
            arcs_fifo = [start_arc]  # here are arcs that are not yet enumerated
            arc_renumerate  = dict()  # here are arcs that have been enumerated

            while arcs_fifo:
                arc = arcs_fifo.pop()  # get new arc to process
                arc_renumerate[arc] = len(arc_renumerate)  # enumerate current arc with next available value
                for (node, pos) in self.D(arc):  # loop through both arc endpoint nodes
                    for offset in range(1, len(node)):  # loop through other arcs from node in CCW direction
                        if node[(pos + offset) % len(node)] not in arc_renumerate and node[(pos + offset) % len(node)] not in arcs_fifo:
                            arcs_fifo.insert(0, node[(pos + offset) % len(node)])  # place in line to be processed

            # renumeration complete
            K = self.copy()
            K.renumerate_arcs(arc_renumerate)
            K.nodes.sort()

            if K < minimal_knot:
                minimal_knot = K

        return K




    def OLD_canonical(self):
        """
        Puts knot in canonical form (i.e. a unique diagram)
        :return: returns the canonical form of the knot, leaves self unchanged
        """

        minimal_knot = None  # current minimal knot

        if not len(self):
            return self.copy()  # empty knot is already canonical

        # select starting arcs as ingoing underarcs of negative crossings (or positive if no negative)
        for X in [XmQ, XpQ]:
            starting_arcs = [node[0] for node in self.filter_nodes(X)]
            if starting_arcs: break

        if not starting_arcs: starting_arcs = self.arcs()  # if there are no crossings, any arc can be starting

        # main loop through possible starting arcs

        for start_arc in starting_arcs:

            available_arcs = {(0, start_arc)}  # list of arcs available to scan, start only with start_arc
            new_arc = 1   # the number of the current arc
            new_knot = Knotted([], framing=0, unknots=0, coloring=dict())  # this is the new knot we are building
            used_node_indices = set()  #
            arc_renum = {start_arc: 0}  # initialize the arc renumeration dictionary
            new_knot_not_minimal = False # we do not know yet
            new_knot_is_minimal = False
            used_arcs = set()

            #print()
            #print("[START] at arc", start_arc, "with knot", new_knot)
            #print()

            while available_arcs:  # main loop, travelling along the arc

                arc_pair = min(available_arcs)  # pop minimal arc from set
                #print("[NEW]",new_knot)
                #print("[WHILE] arc", arc_pair[1],"in",arc_pair,"from available arcs",available_arcs)
                available_arcs.remove(arc_pair)
                arc = arc_pair[1]  # select current (old) arc

                used_arcs.add(arc)
                (c0_index, p0), (c1_index, p1) = self.D_index(arc)  # get arc endpoints
                #print("[INDICES] of arc",arc,"are",c0_index, c1_index,"in", self)

                # select unused arc endpoint or terminal endpoint if both are available
                c0, c1 = self.nodes[c0_index], self.nodes[c1_index]

                if c1_index in used_node_indices and c0_index not in used_node_indices:
                    cr, pos, cr_index = c0, p0, c0_index
                elif c1_index not in used_node_indices and c0_index in used_node_indices:
                    cr, pos, cr_index = c1, p1, c1_index
                else:
                    cr, pos, cr_index = (c0, p0, c0_index) if len(c0) > len(c1) else (c1, p1, c1_index)

                #print("[NODE]",cr,"while used nodes are", str(used_node_indices)+".",["Node is new.","Node is NOT new."][cr_index in used_node_indices], new_knot)

                if cr_index not in used_node_indices:  # new crossing, add it to knot

                    used_node_indices.add(cr_index)

                    #print("[RENUM]", arc_renum, "->", end=" ")
                    for p in cr:  # loop through positions
                        old_arc = cr[(p + pos) % len(cr)]
                        if old_arc not in arc_renum:  # if arc at crossing not already renumerated, stick in a new arc
                            arc_renum[old_arc] = new_arc
                            available_arcs.add((new_arc, old_arc))
                            new_arc += 1

                    #print(arc_renum)

                    new_node = deepcopy(cr)  # copy node
                    new_node.renumerate_arcs(arc_renum)
                    new_node.canonical()
                    new_knot.nodes.append(new_node)
                    #print("[NODE]",new_node,"(new node).")

                    if minimal_knot is None: new_knot_is_minimal = True  # if we don't have minimal knot, then this one is automatically the smallest

                    if minimal_knot is not None and new_knot.nodes[-1] < minimal_knot[len(new_knot.nodes)-1]:
                        new_knot_is_minimal = True # since the 1st crossing is smaller, the knot is minimal

                    """print("KNOT", self)
                    print("MIN ", minimal_knot)
                    print("NEW ", new_knot)
                    print("is min=", new_knot_is_minimal)
                    if minimal_knot is not None:
                        print("last new < last min", new_knot.nodes[-1] < minimal_knot[len(new_knot.nodes)-1])
                        print("last new > last min", new_knot.nodes[-1] > minimal_knot[len(new_knot.nodes)-1])
                    """

                    if not new_knot_is_minimal and \
                            minimal_knot is not None and \
                            new_knot.nodes[-1] > minimal_knot[len(new_knot.nodes)-1]: # can the new knot be minimal?
                        #print("Knot is bigger and we will not continue.")
                        new_knot_not_minimal = True # if not, break the loop
                        break # break the main loop




                    else: #print("Knot is not bigger.")
                        #print("no break")
                        pass
                else:
                    # we came across a node which we have already considered
                    pass

                if len(new_knot) == len(self):
                    break

            # no more available arcs

            # but are there available crossings? i.e. graphs with open ends?
            if not new_knot_not_minimal and len(self) > len(new_knot):
                additional_nodes = [] # nodes to add to the original knot
                for cr_index in range(len(self)): # loop through unused crossings
                    if cr_index not in used_node_indices:
                        cr = self[cr_index]
                        if all(a in arc_renum for a in cr.arc_set()): # continue only if all arcs already enumearted
                            new_node = deepcopy(cr)
                            new_node.renumerate_arcs(arc_renum)
                            new_node.canonical()
                            additional_nodes.append(new_node)
                        else:
                            new_knot_not_minimal = True
                            break

                additional_nodes.sort()
                new_knot.nodes += additional_nodes
                if (not new_knot_not_minimal) and (minimal_knot is None or new_knot < minimal_knot):
                    minimal_knot = new_knot # if we get a minimal knot after adding new nodes, change it


            if (minimal_knot is None or not new_knot_not_minimal) and (len(self) == len(new_knot)):
                if minimal_knot is not None and minimal_knot < new_knot:
                    print("        Self:", self)
                    print("Minimal knot:", minimal_knot)
                    print("New knot    :", new_knot)
                    print(minimal_knot.nodes[0] < new_knot.nodes[0])
                    raise ValueError("Canonical knot greater than minimal knot.")
                minimal_knot = new_knot

            if len(self) < len(new_knot): raise ValueError("Canonical knot larger than original knot.")

        if minimal_knot is None: raise ValueError("Canonical knot of", self, "is None.")
        if len(minimal_knot) != len(self): raise ValueError("Canonical knot nof of same length than original knot.")


        return minimal_knot


    def canonical_unoriented(self):
        knot_orientations = self.orientations() # get all knot orientations

        #print(self)
        #for k in knot_orientations:
        #    print("  ",k)
        #    KK = k.canonical()

        knot_orientations_canonical = [K.canonical() for K in knot_orientations]
        return min(knot_orientations_canonical)


    def self_canonical(self):
        """ make self canonical """
        K = self.canonical()
        self.copy_to_self(K)

    def self_canonical_unoriented(self):
        """ make self canonical """
        name = self.name
        K = self.canonical_unoriented()
        self.copy_to_self(K)
        self.name = name

    def fix_orientation(self):
        """
        fix (bonded) knot orientation, of arcs are incoherently oriented
        """

        #print("FIX", self)

        available_arcs = list(self.arcs())  # arcs still needed to be fixed/checked
        arc, pos, along_direction = None, None, None  # current arc


        #print("AVAILABLE ARCS:", available_arcs)
        # preferred start arcs are the ones on odd vertices, since there is no canonical way for an arc to pass through
        preferred_arcs = [(arc, node, pos) for arc in available_arcs for node, pos in self.D(arc, True)
                          if len(node) % 2 == 1]

        #print("PREFFERED:",  preferred_arcs)

        while available_arcs:  # loop until there are arcs left

            if arc is None:  # choose new arc to travel along

                while preferred_arcs:
                    arc, node, pos = preferred_arcs.pop()
                    if arc in available_arcs:
                        break
                    arc = None

                if arc is None:
                    arc = available_arcs[-1]
                    node, pos = self.D(arc, ignore_orientation=True)[0]  # random-side get node and position of arc

                along_direction = node.outQ(pos)  # are we travelling along or opposite of arc direction?

            available_arcs.remove(arc)

            #print("ARC:", arc,pos,along_direction,node, "REMAINING:",available_arcs)


            if along_direction ^ node.outQ(pos):  # fix orientation of arc in node
                pos = node.reverse(pos)
                #print("   reverse node", node)

            # jump to the other end of arc
            node, pos = self.adjacent_node(node, pos)
            #print("   new node", node,pos)

            if along_direction ^ node.inQ(pos):  # fix the orientation of the other node of arc
                pos = node.reverse_arc(pos)
                #print("   Reverse node", node)

            if self.terminus_nodeQ(node, pos):  # end path if we hit a terminus
                arc = None
                #print("       TERMINUS")
                continue

            # continue through node
            pos = self.adjacent_pos(node, pos)
            arc = node[pos]

            #print("   adjacent", arc, pos, node)

            # if the arc has already been processed, don't continue along the cycle
            if arc not in available_arcs:
                arc = None



    ##############
    ## PRINTING ##
    ##############

    def export(self):
        return "Knotted([" \
               + ", ".join([node.export() for node in self.nodes]) + "]" \
               + ", coloring=" + str(tuple(self.coloring[arc] for arc in range(max(self.coloring)+1))) \
               + ", name='" + str(self.name) + "')"

    def __repr__(self):
        if len(self.nodes) == 0:
            return "Knot: unknot" if self.unknots == 1 else ("Knot: Unlink (" + str(self.unknots) + " components)")
        unknot_string = (" + " + "O" * self.unknots) if self.unknots else ""
        return 'Knot' + (' ' + str(self.name) if self.name else '') + ': ' + ', '.join(
            repr(n) for n in self.nodes) + unknot_string


def __init__(self, nodes=None, framing=0, unknots=0, name='', coloring=None):

    def print(self):
        if len(self.nodes) == 0:
            return "Knot: unknot" if self.unknots == 1 else ("Knot: Unlink (" + str(self.unknots) + " components)")

        return 'Knot' + (' '+self.name if self.name else '') + ': ' + ', '.join(repr(n) for n in self.nodes) + unknot_string


    def __repr__(self):

        return self.export()
        #return self.simple_export()
                #return self.simple_export()
        if len(self.nodes) == 0:
            return "Knot: unknot" if self.unknots == 1 else ("Knot: Unlink (" + str(self.unknots) + " components)")
        unknot_string = (" + " + "O" * self.unknots) if self.unknots else ""
        return 'Knot' + (' '+self.name if self.name else '') + ': ' + ', '.join(repr(n) for n in self.nodes) + unknot_string

    def export_OLD(self):
        #for n in self.nodes:
        #    print(n.export())
        return "Knotted([" + ", ".join([node.export() for node in self.nodes]) + "]"+ ", name='" + str(self.name) + "')"

    def simple_export(self):
        return "[[" + " ".join([node.simple_export() for node in self.nodes]) + "".join([" U" for x in range(self.unknots)]) + "]]"

def check_knotted(k):
    """ check if basic properties of a knotted graph are satisfied (knot is realizable)"""

    # Check if each arc has exactly one output and one input
    try:
        arcs = {a:[0,0] for a in k.arcs()}
        for node in k:
            for pos in node:
                if node.outQ(pos):
                    arcs[node[pos]][0] += 1
                if node.inQ(pos):
                    arcs[node[pos]][1] += 1
        for a in arcs:
            if arcs[a] != [1,1]:
                return False
    except:
        return False
    return True

def crossings_in_area(K, area):
    crossings = []
    for arc, side in area:
        (cr0, pos0), (cr1, pos1) = K.D(arc)
        if cr0 not in crossings: crossings.append(cr0)
        if cr1 not in crossings: crossings.append(cr0)
    return crossings

"""
knot = Knotted(nodes = [
    Crossing([0,6,1,7], -1), #0
    Crossing([7,1,8,2], -1), #1
    Crossing([2,14,3,13], +1), #2
    Crossing([12,4,13,3], +1), #3
    Crossing([4,9,5,0], -1), #4
    Vertex([5,10,6], [True, False, False],  [0,1,0]), #5
    Crossing([10,9,11,8], +1), #6
    Vertex([14,11,12], [True, True, False], [0,1,0]) #7
])

tref_with_band = Knotted(nodes = [
    Crossing([3,0,4,7],1),
    Crossing([0,5,1,4],1),
    Crossing([5,2,6,1],1),
    Vertex([2,3,8],ins=[2,8],colors=[0,0,1]),
    Vertex([6,8,7],ins=[6],colors=[0,1,0])
])

link1 = Knotted(nodes = [
    Crossing([0,6,1,7], -1), #0
    Crossing([7,1,8,2], -1), #1
    Crossing([2,14,3,13], +1), #2
    Crossing([12,4,13,3], +1), #3
    Crossing([4,9,5,0], -1), #4
    Vertex([5,10,6], [0,1,0], ins= [5]), #5
    Crossing([10,9,11,8], +1), #6
    Vertex([14,11,12], [0,1,0], ins=[14,11]) #7
])


tref_band_2 = Knotted(nodes = [
    Crossing([4,9,5,0], -1),
    Crossing([0,5,1,6], -1),
    Crossing([7,3,8,4],-1),
    Vertex([9,8,10], colors = [0,0,1], ins=[8,10]),
    Vertex([2,10,3], colors = [0,1,0], ins = [2]),
    Vertex([1,2,11], colors = [0,0,1], ins = [1]),
    Vertex([7,6,11], colors = [0,0,1], ins = [6,11])
])


"""

def export_knots(KNOTS, filename, enum=False):

    if enum:
        for i, k in enumerate(KNOTS):
            k.name = str(i)

    print("[EXPORTING]", len(KNOTS), "knots.")
    file = open(filename, 'w')

    for k in KNOTS:
        file.write(k.export() + "\n")

    print("[DONE]")

    file.close()




def load_knots(filename, max_loaded_knots = None, sort_by_name = False):

    knots, count = [], 0
    with open(filename) as f:
        for line in f:
            if "Knotted" in line:
                k = eval(line)
                knots.append(k)
                count += 1
                if max_loaded_knots is not None and count >= max_loaded_knots:
                    break

    print("Loaded", len(knots), "knots.")
    if sort_by_name:
        print("Sorting knots.")
        knots.sort(key = lambda k: k.name)
    return knots

def colorize_bonds_by_minimal_distance(K):
    #print("\n", K)
    # puts colors on bonds according to self-distance
    closed_components, open_components = K.split_components()
    for bond_component in open_components:
        endpoint_cr_pos = [] # store the bond endpoints in this list
        for arc in bond_component:
            (cr0, pos0), (cr1, pos1) = K.D(arc)
            if VQ(cr0):
                endpoint_cr_pos.append((cr0, pos0))
            if VQ(cr1):
                endpoint_cr_pos.append((cr1, pos1))

        #print("enpt", endpoint_cr_pos)
        # find self-distance for given bond
        dist = []
        # find outgoing arc from cr0
        (cr0, pos0), (cr1, pos1) = endpoint_cr_pos
        for cr, pos_bond, cr_alt in [(cr0, pos0, cr1), (cr1, pos1, cr0)]:

            #print("cr",cr)
            pos = ((pos_bond+1) % len(cr)) if cr.outQ((pos_bond+1) % len(cr)) else ((pos_bond+2) % len(cr))



            if not cr.outQ(pos): raise ValueError("Error outgoing.", cr, pos)
            arc = cr[pos]
            count_vertices = 0
            # travel along arc until cr_alt met
            #print("  ",cr, pos, arc)
            while cr != cr_alt:
                #print("    ",arc)
                # get to new node
                arc = K.next_arc_forward(arc)
                cr, pos = K.D(arc)[0]
                if VQ(cr): count_vertices += 1
            dist.append(count_vertices)

        # recolor
        cr0.color[pos0] = min(dist)
        cr1.color[pos1] = min(dist)

        #print(bond_component, endpoint_cr_pos, dist)






def unknotQ(K):
    return len(K) == 0 and K.unknots == 1

"""
print(knot )
print("CANONICAL",knot.canonical())

print(tref_with_band )
print("CANONICAL",tref_with_band.canonical())

print(link1)
print("CANONICAL",link1.canonical())

print(tref_band_2)
print("CANONICAL",tref_band_2.canonical())
"""

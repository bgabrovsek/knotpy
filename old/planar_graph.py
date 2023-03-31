from combinatorics import *
from itertools import product
from knotted import *

class CircularList(list):
    def __getitem__(self, index):
        if isinstance(index, slice):
            return super().__getitem__(index)
        else:
            return super().__getitem__(index % len(self))

    def hash(self):
        return hash(tuple(self))

class PlanarGraph():

    def __init__(self, nodes, name=None):
        """Initialize"""
        #print(hash)
        self.nodes = [CircularList(a) for a in nodes]
        self.name = name

    def __len__(self):
        """ returns number of nodes """
        return len(self.nodes)

    def __iter__(self):
        return self.nodes.__iter__()

    def __getitem__(self, index):
        return self.nodes[index]

    def __eq__(self, other):
        return self.nodes == other.nodes

    def __lt__(self, other):
        for i in range(min(len(self),len(other))):
            if self.nodes[i] < other.nodes[i]:
                return True
            if self.nodes[i] > other.nodes[i]:
                return False
        return False


    def degree(self, index = None):
        if index is None:
            return [len(node) for node in self.nodes]
        else:
            return len(self.nodes[index])

    def arcs(self):
        return union(*self.nodes)

    def D(self, index0, pos0):
        """ only works for simple grpahs"""
        arc = self[index0][pos0]
        for index in range(len(self)):
            if index != index0 and arc in self[index]:
                return index, self[index].index(arc)

    def D_node(self, node0, pos0):
        """ only works for simple grpahs"""
        arc = node0[pos0]
        for node in self:
            if node != node0 and arc in node:
                return node, node.index(arc)

    def CCW_areas(self):
        #print(self)
        areas = []
        dots = {(index, pos) for index in range(len(self)) for pos in range(len(self[index]))} # dots are local areas between arcs at node
        #print(dots)
        while dots:
            # start a new area
            index0, pos0 = next(iter(dots)) # get element from set
            index, pos = index0, pos0
            area = []
            while True:
                index, pos = self.D(index, pos)
                pos = (pos-1) % len(self[index])
                dots.remove((index,pos))
                area.append((index,pos))
                if (index, pos) == (index0, pos0): break
            areas.append(area)
        return areas

    def canonical(self):

        #print("[CANONICAL]", self)

        minimal_graph = None

        max_deg = max(self.degree())
        max_deg_nodes = [node for node in self.nodes if len(node) == max_deg] # start at max deg crossing

        # possible starting arcs
        starting_dots = ( (node, pos) for pos in range(max_deg) for node in max_deg_nodes)

        for start_dot in starting_dots: # start at a dot
            start_node, start_pos = start_dot
            start_arc = start_node[start_pos]
            new_graph = PlanarGraph(tuple())
            new_arc = 1
            arc_renum = {start_arc: 0}
            used_nodes = [] # TODO: make faster/hashable and turn into set
            new_graph_not_minimal = False
            new_graph_is_minimal = False
            used_arcs = [] # used old arcs
            #available_arcs = {(0, start_arc)} # (new_arc, old_arc)

            #available_dots = [(0, start_dot), (0, self.D_node(start_node, start_pos))] # new arc, dot, TODO: make faster/hashable and turn into set
            available_dots = [(0, start_dot), (0, self.D_node(start_node, start_pos))]
            first_time = True

            #print(" start", available_dots)



            while available_dots:
                minadot = available_dots[0] if first_time else min(available_dots)
                first_time = False
                available_dots.remove(minadot)
                node, pos = minadot[1]

                used_arcs.append(node[pos])


                if node not in used_nodes:
                    used_nodes.append(node)

                    for p in range(len(node)): # start renumerating arcs
                        #print(node,isinstance(node,CircularList),pos, p)
                        old_arc = node[pos + p]
                        if old_arc not in arc_renum:
                            arc_renum[old_arc] = new_arc
                            available_dots.append((new_arc,self.D_node(node, pos +p)))
                            new_arc += 1

                    #print("node",node,"renum",arc_renum)

                    #add the new node to graph
                    #print("  appending", list(arc_renum[a] for a in node), min_cyclic_rotation((arc_renum[a] for a in node)))
                    new_graph.nodes.append(min_cyclic_rotation(CircularList(arc_renum[a] for a in node)))

                    if minimal_graph is None: new_graph_is_minimal = True # if no minimal graph, this one is minimal

                    if minimal_graph is not None and new_graph.nodes[-1] < minimal_graph[len(new_graph.nodes)-1]:
                        new_graph_is_minimal = True


                    if not new_graph_is_minimal and minimal_graph is not None and new_graph.nodes[-1] > minimal_graph[len(new_graph.nodes)-1]:
                        new_graph_not_minimal = True
                        break

                # take care also of other adjacent node


                if len(new_graph) == len(self): break


            # add remaining nodes to the knot
            if not new_graph_not_minimal and len(self) > len(new_graph):
                additional_nodes = []  # nodes to add to the original graph
                for node in self:
                    if node not in used_nodes:
                        if all(a in arc_renum for a in node): # continue only if all arcs already enumearted
                            additional_nodes.nodes.append(min_cyclic_rotation((arc_renum[a] for a in node)))
                        else:
                            new_graph_not_minimal = True
                            print("new know has addional crossings", self, new_graph)
                            break

                additional_nodes.sort()
                new_graph.nodes += additional_nodes

                if (not new_graph_not_minimal) and (minimal_graph is None or new_graph < minimal_graph):
                    minimal_graph = new_graph  # if we get a minimal knot after adding new nodes, change it


            #print("new",new_graph)
            if not new_graph_not_minimal and len(self) > len(new_graph):
                print("CANONICAL SHOULD HAVE MORE CROSSINGS.")

            if (minimal_graph is None or not new_graph_not_minimal) and (len(self) == len(new_graph)):
                if minimal_graph is not None and minimal_graph < new_graph:
                    print(self, minimal_graph,"<", new_graph)
                    raise ValueError("Canonical graph greater than minimal knot.")
                minimal_graph = new_graph

        if minimal_graph is None: raise ValueError("Canonical graph of", self, "is None.")
        if len(minimal_graph) != len(self): raise ValueError("Canonical graph not of same length than original knot.")

        minimal_graph_copy = PlanarGraph(minimal_graph.nodes)

        return minimal_graph_copy

    def to_knot(self, under_b_list):
        """
        converts the graph to a spatial knot
        :param under_b_list: list of under/orver crossings (list of booleans)
        :return: the spatial knot
        """
        # make empty knot
        K = Knotted(nodes=[], coloring=dict(), name=self.name)
        used_arcs = set()
        o_index = 0 # counts the index of only 4-valent nodes

        for node in self:  # main loop, loop through graph vertices

            if len(node) == 4:  # do we have a crossing?
                if under_b_list[o_index]:  # first arc is an undercrossing?
                    new_node = Crossing(arcs=list(node), sign=+1)  # undercrossing
                else:
                    new_node = Crossing(arcs=node[-1:]+node[0:-1], sign=-1)  # overcrossing

                o_index += 1
                used_arcs |= set(node)
            else:
                new_node = Vertex(arcs=list(node), ingoingB=[a in used_arcs for a in node])
                used_arcs |= set(node)
            K.nodes.append(new_node)

        # coloring
        K.coloring = {arc: 0 for arc in sorted(K.arcs())}

        #print("Knot ", K)
        #K.fix_orientation()
        #print(" Fix ", K)
        #K.canonical()
        #print(" Can ", K)

        return K

    def bondedQ(self):
        """ checks if a graph satisfies the conitions to be a bonded graph"""
        if min(self.degree()) < 3: return False
        if sum(d == 3 for d in self.degree()) % 2 != 0: return False
        return True

    def hash(self): # turn graph into hash
        t = tuple((hash(tuple(node)) if isinstance(node,list) else node.hash()) for node in self.nodes)
        return hash(t)

    def __repr__(self):
        s = "PlanarGraph((" + ",".join([str(tuple(node)) for node in self.nodes]).replace(" ", "") + ",)"\
            + [","+str(self.name), ""][self.name is None]+")"
        return s
#g = PlanarGraph([0,1,2],[2,1,0])
#print(g.CCW_areas())


#P = PlanarGraph(((0,),(0,1),(1,2,3),(4,2),(3,4)))
#K = P.canonical()
#print(P)
#print(K)
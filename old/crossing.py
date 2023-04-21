from combinatorics import *
from copy import deepcopy
"""
Node - generic crossing or vertex
Crossing - 4-valent node with under/over and in/out information
Vertex - n-valent node with color and in/out information and without under/over information
"""

def NodeTypeID(node):
    if isinstance(node, Crossing): return 0
    if isinstance(node, Vertex): return 1
    if isinstance(node, Bivalent): return 2
    if isinstance(node, Endpoint): return 3
    raise ValueError("Unknown node type.")

class NodePrototypeClass:

    """
    Basic class for crossings and vertices
    """

    def __init__(self):
        """Initialize"""
        self.arcs = []

    def __getitem__(self, position):
        """Access item [pos]"""
        return self.arcs[position] # get arc

    def __setitem__(self, postition, arc):
        """Set item [pos] = arc number"""
        self.arcs[postition] = arc  # set arc

    def __len__(self):
        """Number of arcs"""
        return len(self.arcs)

    def copy(self):
        return deepcopy(self)

    def index(self, arc):
        for pos in range(len(self)):
            if arc == self.arcs[pos]:
                return pos
        return None

    def hash(self):
        t = tuple(a for a in self.arcs)
        return hash(t)

    def __iter__(self):
        """Iterate through arc positions: 0,1,...,len(self)"""
        return iter(range(len(self)))

    def arc_set(self):
        return set(self.arcs)

    def positions(self, arc):
        """returns data set of indices of arc"""
        return {i for i in self if self[i] == arc}

    def CCW(self, position, count = 1):
        """Returns next position in counterclockwise direction (count times)"""
        return (position+count) % len(self)

    def CW(self, position, count = 1):
        """Returns next position in clockwise direction (count times)"""
        return (position-count) % len(self)

    def multiplicity(self, arc):
        """Returns the number of times arc repeats in the crossing (e.g. for detecting loops)"""
        return self.arcs.count(arc)

    def renumerate_arc_by_position(self, position, new_arc_number):
        self.arcs[position] = new_arc_number

    def renumerate_arcs(self, perm):
        """Renumerates arcs by permutation perm, .g. perm = {0:7,1:8,2:6} renumerates arc 0 -> 7, arc 1 -> 8, arc 2 -> 6"""
        # UPDATE: also renumerates partial renumerations
        for ind, arc in enumerate(self.arcs):
            self.arcs[ind] = perm[arc] if arc in perm else arc



    ##### COMPARISON #####

    def canonical(self):
        """ Put the crossing into cannonical form. """
        raise ValueError("Cannot put prototype class in canonical form.")
        pass

    def data(self):
        """Returns tuple of crossing data for comparison purposes"""
        raise ValueError("Cannot convert prototype class to compare data")
        #return (len(self),self.arcs,)

    # TODO: make comparison faster w/o data() call
    def __eq__(self, other):
        if NodeTypeID(self) != NodeTypeID(other): return False
        return self.data() == other.data()

    def __le__(self, other):
        if NodeTypeID(self) < NodeTypeID(other): return True
        if NodeTypeID(self) > NodeTypeID(other): return False
        return self.data() <= other.data()

    def __lt__(self, other):
        #print("lt")
        if NodeTypeID(self) < NodeTypeID(other): return True
        if NodeTypeID(self) > NodeTypeID(other): return False
        #print(self.data()," VS " ,other.data(), self.data() < other.data())
        return self.data() < other.data()

    def __ne__(self, other):
        if NodeTypeID(self) != NodeTypeID(other): return True
        return not (self.data() == other.data())

    def __ge__(self, other):
        if NodeTypeID(self) > NodeTypeID(other): return True
        if NodeTypeID(self) < NodeTypeID(other): return False
        return not (self.data() < other.data())

    def __gt__(self, other):
        if NodeTypeID(self) > NodeTypeID(other): return True
        if NodeTypeID(self) < NodeTypeID(other): return False
        return not (self.data() <= other.data())

##### Crossing Class #####

class Crossing(NodePrototypeClass):
    """Represents data positive (right handed) crossing between the edges [i,j,k,l] starting from the incoming lower
    strand i and going counter clockwise through j, k and l. The upper strand is therefore oriented from l to j
    regardless of the ordering of {j,l}.
    Represents data negative (left handed) crossing between the edges [i,j,k,l] starting from the incoming lower strand i
    and going counter clockwise through j, k and l. The upper strand is therefore oriented from j to l regardless of
    the ordering of {j,l}.
              0                   1
              |                   |
    +:   1 <----- 3     -:   2 <--|-- 0
              |                   |
              V                   V
              2                   3
    """

    def __init__(self, arcs, sign):
        """Initialization"""
        self.arcs = arcs if isinstance(arcs, list) else list(arcs)
        self.sign = sign

    def inQ(self, position):
        """Returns True if the arc at position is an ingoing arc"""
        return position == 0 or position == (1 if self.sign < 0 else 3)

    def outQ(self, position):
        """Returns True if the arc at position is an ingoing arc"""
        return not self.inQ(position)

    def overQ(self, position):
        """Returns True if the arc at position is an over arc"""
        return bool(position % 2)

    def over_arc_set(self):
        return {self.arcs[1], self.arcs[3]}

    def under_arc_set(self):
        return {self.arcs[0], self.arcs[2]}

    def in_arc_set(self):
        return {self.arcs[0], self.arcs[3]} if self.sign > 0 else {self.arcs[0], self.arcs[1]}

    def out_arc_set(self):
        return {self.arcs[1], self.arcs[2]} if self.sign > 0 else {self.arcs[2], self.arcs[3]}

    def underQ(self, position):
        """Returns True if the arc at position is an over arc"""
        return not bool(position%2)

    def mirror(self):
        """Mirrors the crossing"""
        self.arcs = [self.arcs[3],self.arcs[0],self.arcs[1],self.arcs[2]] if self.sign > 0 else [self.arcs[1],self.arcs[2],self.arcs[3],self.arcs[0]]
        self.sign *= -1

    def reverse_arc(self, pos = None):
        """
        reverses the arc at position if given, else reverses whole crossing (both arcs)
        :param pos: optional arc position
        :return: new position if position given
        """
        #print("reversing",self, "at",pos)
        """ reverse arc at position, without considering consequences, returns new position of arc. if no argument is given, reverses both arcs"""
        if pos is None:
            self.arcs = [self.arcs[2],self.arcs[3],self.arcs[0],self.arcs[1]]
        else:
            self.sign *= -1
            if self.underQ(pos):
                self.arcs = [self.arcs[2], self.arcs[3], self.arcs[0], self.arcs[1]]
                return (2, 1, 0, 3)[pos]
            return pos

    def tuple(self):
        return self.arcs[0], self.arcs[1], self.arcs[2], self.arcs[3], self.sign

    # MOVING
    def move_forward(self, position): return (position+2)%4
    def move_backward(self, position): return (position+2)%4
    #def move_back(self, position): return (position+2)%4

    #def CCW(self, position): return (position+1)%4
    #def move_right(self, position): return (position+1)%4
    #def DW(self, position): return (position+3)%4
    #def move_left(self, position): return (position+3)%4

    def canonical(self): # no such thing
        return

    def data(self):
        """Returns tuple of crossing data for comparison purposes"""
        return (len(self), self.sign, self.arcs,)

    def __repr__(self):
        return 'X' + ('p' if self.sign > 0 else 'm')+ '(' + ','.join([str(a) for a in self.arcs]) + ')'

    def export(self):
        s = "Crossing(["
        s += ",".join([str(a) for a in self.arcs])
        s += "], " + str(self.sign) + ")"
        return s

    def simple_export(self):
        s = "+" if self.sign > 0 else "-"
        s += ",".join([str(a) for a in self.arcs])
        return s

        #return "Crossing([" + ",".join([str(data) for data in self.arcs]) + "]," + str(self.sign) + ")"

##### Bivalent Vertex Class #####
class Bivalent(NodePrototypeClass):
    """ represents data bivalent vertex, arcs = [in_arc, out_arc]"""

    def __init__(self, in_arc, out_arc):
        self.arcs = [in_arc, out_arc]

    def inQ(self, position):
        """Returns True if arc position is pointing inward"""
        return position == 0

    def outQ(self, position):
        """Returns True if arc position is pointing outward"""
        return position != 0

    def export(self):
        return 'Bivalent(' + str(self.arcs[0]) + ", " + str(self.arcs[1]) + ")"

    def __repr__(self):

        return 'B(' + str(self.arcs[0]) + "->" + str(self.arcs[1]) + ")"

    pass

##### Rigid Vertex Class #####

class Vertex(NodePrototypeClass):
    """Represents data rigid graph vertex. Arcs are listed in CCW orientation. Colors represent data list of colors of arcs.
    ins/outs are lists of in/out arcs (can only provide one)
    Example: data bivalent vertex with two ingoing arcs 0 and 1 colored by A and B ([0]--A-->.<--B--[1]) would have
    arcs = [0,1], colors = [A, B], ins = [0,1]
    TODO: ins/outs only works if all arcs are different, does not work for loops for loops !!!!
    """

    def __init__(self, arcs, ingoingB=None, ins=None):
        """
        Initialization of data graph
        :param arcs: list of arcs
        :param ingoingB: list of boolans [b_arc_0, b_arc_1,...], True if arc is ingoing
        :param ins: alternatively ingoing arcs can be given by data list of in arcs, ins [0,2] = ingoingB [T,F,T,F,F,...]
        """
        self.arcs = arcs  # list of arcs
        self.ingoingB = ingoingB  # list of booleans for each position

        if ins is not None:
            self.ingoingB = [self.arcs[arc] in ins for arc in range(len(arcs))]

    def tuple(self):
        return tuple(self.arcs)


    def insert_arc(self, arc, pos, ingoing, color = None, multiplicity = 1):
        """ inserts the arc to vertex"""
        #print("   insert", arc, " ",pos)
        for i in range(multiplicity):
            self.arcs.insert(pos, arc+i)
            self.ingoingB.insert(pos,ingoing)
            #if self.color is not None:
            #    self.color.insert(pos, color if color is not None else 0)

    # comparison
    def data(self):
        return (len(self), self.arcs, self.ingoingB)

    # properties
    def inQ(self, position):
        """Returns True if the arc at position is an ingoing arc"""
        return self.ingoingB[position]

    def outQ(self, position):
        """Returns True if the arc at position is an ingoing arc"""
        return not self.ingoingB[position]

    def in_arc_set(self):
        return {self.arcs[pos] for pos in self if self.inQ(pos)}

    def out_arc_set(self):
        return {self.arcs[pos] for pos in self if self.outQ(pos)}

    def OLD_uncolored_arc_set(self):
        return {self.arcs[pos] for pos in self if self.color[pos] == 0}

    def OLD_colored_arc_set(self):
        return {self.arcs[pos] for pos in self if self.color[pos] != 0}

    def degree(self):
        """Returns the degree of the vertex"""
        return len(self.arcs)

    def OLD_all_colors(self):
        """ Returns the set of arc colors"""
        return set(self.color)

  #  def reverse_arc(self, position):
   #     self.ingoingB[position] = not self.ingoingB[position]

    def OLD_color_dict(self):
        """ returns data dictionary of colors {color1: arcs1, color2:arcs2,...}, TODO: make faster w/ one loop"""
        return {c:[a for ind, a in enumerate(self.arcs) if self.color[ind] == c] for c in self.all_colors()}

    def OLD_terminal_arcs(self):
        """ Returns arcs from data bond that terminate at the vertex"""
        return [self.arcs[pos] for pos in range(len(self)) if self.ingoingB[pos] and self.terminusQ(pos)]

    def initial_arcs(self):
        """ Returns arcs from data bond that start at the vertex"""
        return [self.arcs[pos] for pos in range(len(self)) if not self.ingoingB[pos] and self.terminusQ(pos)]

    # MOVING
    def OLD_move_forward(self, position, coherent_direction=True):
        """ same as move_along_color (for compatibility with sibling Crossing class)"""
        return self.move_along_color(position, coherent_direction)

#    def move_forward(self, position):
 #       """ same as move_along_color (for compatibility with sibling Crossing class)"""
  #      return self.move_along_color(position)

    def OLD_move_along_color(self, position, coherent_direction=True):
        """ from the position arc, move to the (first, CCW) adjacent arc that is of the same color"""
        N = len(self)
        for pos in range(position+1,position+1+N-1):
            if self.color[pos % N] == self.color[position % N]:

                if (self.ingoingB[pos % N] == self.ingoingB[position % N]) and (coherent_direction):
                    raise ValueError("Moving along arc in contradicting orientations")

                return pos % N

        raise KeyError("Cannot move along the arc (position = "+str(position)+").")

    def OLD_terminusQ(self, position, coherent_direction = True):
        """Is position an endpoint of data bond (no adjacent arcs with same color)"""
        for pos in range(len(self)):
            if (pos != position) and \
                    (self.color[pos] == self.color[position]) and \
                    ((self.ingoingB[pos] != self.ingoingB[position]) or (not coherent_direction)):
                return False # found data forward arc

        return True # no forward arc


    def OLD_reverse(self, pos = None):
        """ reverse arc at position, without considering consequences, returns new position of arc. if no argument is given, reverses all arcs"""
        print("OBSOLETE REVERSE USED.")
        if pos is None:
            self.ingoingB = [not i for i in self.ingoingB]
        else:
            N = len(self)
            self.ingoingB[pos] = not self.ingoingB[pos] # reverse
            for p in range(pos + 1, pos + 1 + N - 1): # reverse first CCW arc in same color
                if self.color[p % N] == self.color[pos % N]:
                    self.ingoingB[p % N] = not self.ingoingB[pos]; #not self.ingoingB[p % N]
                    return pos
            return pos


    # TODO: do not keep both methods
    def reverse_arc(self, position):
        """
        reverses data single arc
        :param position: position of the arc in node
        :return: new position (is the same as orignal one)
        """
        self.ingoingB[position] = not self.ingoingB[position]
        return position

    def canonical(self):
            shift = min_cyclic_rotation(self.arcs, return_index = True)
          #  print("->",self.arcs, shift)
            self.arcs = self.arcs[shift:] + self.arcs[:shift]
            self.ingoingB = self.ingoingB[shift:] + self.ingoingB[:shift]
            #if self.color is not None:
            #    self.color = self.color[shift:] + self.color[:shift]


    def __repr__(self):
        """
        :return: user-friendly string representation of data crossing
        """

        return 'V(' + ','.join(
            [str(self.arcs[i]) + '·⭰'[self.ingoingB[i]]
             for i in range(len(self))])+")"

    def export(self):
        s = "Vertex(["
        s += ",".join([str(a) for a in self.arcs])
        s += "],["
        s +=  ",".join(["01"[b] for b in self.ingoingB]) + "]"
        s += ")"
        return s


#class Point(NodePrototypeClass):
 #   """ A point is an unoriented vertex (used for planar unoriented graphs)"""

  #  def __init__(self, arcs):
   #     self.arcs = arcs


##### Endpoinr Vertex Class used for Kauffman T-states or Knotoids #####

class Endpoint(NodePrototypeClass):

    def __init__(self, arc, ingoing, color = None):
        """Initialization"""
        self.arc = arc  # list of arcs
        self.color = color # list of colors for each position, None if operating with uncolored structure
        self.ingoing = ingoing  # list of bools for each position

    def legQ(self): return not self.ingoing
    def headQ(self): return self.ingoing

    def __repr__(self):
        if self.legQ():
            return "Leg(" + str(arc) + ","+str(color) + ")"
        else:
            return "Head(" + str(arc) + "," + str(color) + ")"

    def export(self):
        return "Endpoint("+str(self.arc)+","+str(self.ingoing) + "," + str(self.color) + ")"


# Filter functions


def XQ(node): return isinstance(node, Crossing) # crossing?
def XpQ(node): return isinstance(node, Crossing) and node.sign > 0 # positive crossing?
def XmQ(node): return isinstance(node, Crossing) and node.sign < 0 # positive crossing?
#def BQ(cr): return isinstance(cr, Bivalent) # bivalent?
def VQ(node): return isinstance(node, Vertex) # vertex?
def BQ(node): return isinstance(node, Bivalent) # vertex?
#def QQ(cr): return isinstance(cr, Vertex) and not cr.trivalentQ() # quadrivalent singular?
#def TQ(cr): return isinstance(cr, Vertex) and cr.trivalentQ() # trivalent singular?
#def TQO(cr): return isinstance(cr, Vertex) and cr.trivalentQ() and cr.degree() == -1 # trivalent singular out band?


def TETRAVALENTQ(node): return len(node) == 4
def TRIVALENTQ(node): return len(node) == 3



def V(arcs, color, ingoing):

    return Vertex(
        arcs = arcs,
        ingoingB = [a in ingoing for a in arcs],
        colors = [(1 if a == color else 0) for a in arcs]
    )

def Cp(*arcs):
    return Crossing(list(arcs),1)

def Cm(*arcs):
    return Crossing(list(arcs),-1)



"""
c = CrossingPrototypeClass()
c.arcs = [7,7,3,3]
for x in c:
    print(x)

print(set(c), c.position(0))"""

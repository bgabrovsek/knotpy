from knotted import *
from itertools import product, combinations
from random import choice

DEBUG_REIDEMEISTER = 0
REIDEMEISTER_PRINT = False


# HELP FUNCTIONS

def cross_arcs(K, arc0, arc1, sign, over):
    """ takes arc0 and arc1, and crosses them (creates a crossing and two additional arcs)
    given the crossing sign and if arc0 is over arc1"""

    #print("CROSS ARC", arc0, arc1, sign, over)

    biv0 = K.split_arc(arc0)
    biv1 = K.split_arc(arc1)
    K.pop_nodes(2)

    if sign > 0 and over:
        K.append_node( Crossing([biv1[0],biv0[1],biv1[1],biv0[0]], sign) )
    elif sign > 0 and not over:
        K.append_node(Crossing([biv0[0], biv1[1], biv0[1], biv1[0]], sign))
    elif sign < 0 and over:
        K.append_node(Crossing([biv1[0], biv0[0], biv1[1], biv0[1]], sign))
    elif sign < 0 and not over:
        K.append_node(Crossing([biv1[0], biv0[0], biv1[1], biv0[1]], sign))
    else:
        raise ValueError("Problem splitting arc by crossing")

    return biv0, biv1

def area_nodes(K, area):
    area_arcs = set(arc for arc, dir in area)
    return [node for node in K.nodes if set(node.arcs) & area_arcs]


# REIDEMEISTER MOVES

# REIDEMEISTER MOVE 1

def R1_unkink(K, arc):
    if REIDEMEISTER_PRINT: print("  R1 unkink on arc", arc, K)

    if DEBUG_REIDEMEISTER: print("[R1 UNKINK]", K, arc)

    (crs0,pos0), (crs1,pos1) = K.D(arc)
    other_pos0, other_pos1 = {0,1,2,3} - {pos0, pos1} # get the positions of the other two arcs of the crossing
    if crs0 != crs1: raise ValueError("R1 kink fail")

    if crs0.inQ(other_pos0) and crs0.outQ(other_pos1):
        K.append_node(Bivalent(crs0[other_pos0], crs0[other_pos1]))
    elif crs0.outQ(other_pos0) and crs0.inQ(other_pos1):
        K.append_node(Bivalent(crs0[other_pos1], crs0[other_pos0]))
    else:
        raise ValueError("R1 unkink fail (in/out)")

    del K[crs0] # TODO: does this work? why not use K.remove_nodes()
    K.remove_bivalent_nodes()
    if DEBUG_REIDEMEISTER: print("[RESULT]", K, arc)

def R1_kink(K, arc, side = None, sign = None):
    """side = 1 (right side) or -1 (left side)"""
    # TODO: realize using cross_arcs()


    if side is None: side = choice((-1,1))
    if sign is None: sign = choice((-1,1))

    if REIDEMEISTER_PRINT: print("  R1 kink on arc", arc, "side", side, "sign",  sign, K)


    if DEBUG_REIDEMEISTER: print("[R1 kink]:",K, arc, side, sign)

    K.split_arc(arc)
    b_node = K.nodes.pop() # TODO: do not access nodes directly
    new_arc = max(K.arcs())+1
    if side > 0 and sign > 0:
        K.nodes.append(Crossing([new_arc, new_arc, b_node[1], b_node[0]], +1))
    elif side > 0 and sign < 0:
        K.nodes.append(Crossing([b_node[0], new_arc, new_arc, b_node[1]], -1))
    elif side < 0 and sign > 0:
        K.nodes.append(Crossing([b_node[0], b_node[1], new_arc, new_arc], +1))
    elif side < 0 and sign < 0:
        K.nodes.append(Crossing([new_arc, b_node[0], b_node[1], new_arc], -1))
    else:
        raise ValueError("R1 kink impossible.")

    if DEBUG_REIDEMEISTER: print("[RESULT]:",K)


# REIDEMEISTER MOVE 2

def R2_poke(K, pair_arc_sides, over=None):
    """ Performs a R2 poke, input are pairs of (arc, side bool), where side = True if CCW and side = false if arc CW"""
    # TODO: realize R2 poke using cross_arcs()

    arc_side0, arc_side1 = pair_arc_sides
    if over is None: over = choice((False,True))

    if REIDEMEISTER_PRINT: print("  R2 poke on arcs", pair_arc_sides,  {False: "under", True:"over"}[over], K)


    arc0, side0 = arc_side0
    arc1, side1 = arc_side1

    if DEBUG_REIDEMEISTER: print("[R2 POKE]", K, "arc0",arc_side0, "arc1", arc_side1, "over" if over else "under")

    # spilt the arcs
    if (side0 ^ side1) and not side0: arc0, side0, arc1, side1 = arc1, side1, arc0, side0 # swap, so that arc0 is CCW
    biv0 = K.split_arc(arc0)
    if DEBUG_REIDEMEISTER: print("split", K)
    biv1 = K.split_arc(biv0[1])
    if DEBUG_REIDEMEISTER: print("split", K)
    biv2 = K.split_arc(arc1)
    if DEBUG_REIDEMEISTER: print("split", K)
    biv3 = K.split_arc(biv2[1])
    if DEBUG_REIDEMEISTER: print("split", K)

    if DEBUG_REIDEMEISTER: print("poke", K)
    #extra_nodes = K.nodes[-4:]
    K.nodes = K.nodes[:-4]  # remove last 4 bivalent nodes

    if DEBUG_REIDEMEISTER: print("poke", K)

    if side0 and not side1:
        # CASE CCW/CW
        K.append_node(Crossing([biv2[0],biv0[0],biv2[1],biv0[1]],-1))
        K.append_node(Crossing([biv2[1],biv1[1],biv3[1],biv0[1]],+1))
    elif side0 and side1:
        # CASE CCW/CCW
        K.append_node(Crossing([biv2[1],biv0[1],biv3[1],biv0[0]],+1))
        K.append_node(Crossing([biv2[0],biv0[1],biv2[1],biv1[1]],-1))
    elif not side0 and not side1:
        # CASE CW/CW
        K.append_node(Crossing([biv2[0],biv1[1],biv2[1],biv0[1]],+1))
        K.append_node(Crossing([biv2[1],biv0[0],biv3[1],biv0[1]],-1))
    else:
        raise ValueError("Unexpected error while R2 poking")

    if not over:
        if DEBUG_REIDEMEISTER: print("Mirroring.", K)
        K.nodes[-1].mirror()
        K.nodes[-2].mirror()

    if DEBUG_REIDEMEISTER: print("[RESULT]", K)

    #print(K)


def R2_unpoke(K, area):
    """ unpokes arcs in area"""
    if DEBUG_REIDEMEISTER: print("[R2 UNPOKE]", K, area)
    if REIDEMEISTER_PRINT: print("  R2 unpoke on area", area, K)



    (arc_a, ccw_a), (arc_b, ccw_b) = area
    arc_a_0, arc_a_1 = K.previous_arc_backward(arc_a), K.next_arc_forward(arc_a)
    arc_b_0, arc_b_1 = K.previous_arc_backward(arc_b), K.next_arc_forward(arc_b)
    K.nodes = [node for node in K.nodes if not ({arc_a, arc_b} & set(node.arcs))]
    K.nodes.append(Bivalent(in_arc=arc_a_0, out_arc=arc_a_1))
    K.nodes.append(Bivalent(in_arc=arc_b_0, out_arc=arc_b_1))
    K.remove_bivalent_nodes()
    if DEBUG_REIDEMEISTER: print("[RESULT]", K)

# REIDEMEISTER MOVE 3

def R3_move(K, area):
    # 1. let the arcs area be a, b, c
    # 2. let the adjacent arcs be a', a''; b', b'', c', c'' in CCW direction
    # 3. we need to replace

    if DEBUG_REIDEMEISTER: print("[R3]", K, area)
    if REIDEMEISTER_PRINT: print("  R3 move on area", area)

    arcs = [a for a,s in area]
    deltas = [K.D(a) for a in arcs]

    for i, (a, ((c0,p0), (c1,p1))) in enumerate(zip(arcs, deltas)):
        #c0[(p0 + 2) % 4] = c0[p0]  # move mid arc to side
        #c1[(p1 + 2) % 4] = c1[p1]  # move mid arc to side
        #c0[p0] = c1[(p1 + 2) % 4]  # move side arc to other side arc
        #c1[p1] = c0[(p0 + 2) % 4]  # move side arc to other side arc
        c0[(p0 + 2) % 4], c1[(p1 + 2) % 4], c0[p0], c1[p1] =  c0[p0], c1[p1]  , c1[(p1 + 2) % 4],  c0[(p0 + 2) % 4]
    if DEBUG_REIDEMEISTER: print("[RESULT]", K)


# REIDEMEISTER MOVE 4

"""
def R4_poke_alt(K, arc):
    
    # find the adjacent crossings
    (cr0, pos0), (cr1, pos1) = K.D(arc)
    ((cr, pos_cr), (vx, pos_vx)) = ((cr0, pos0), (cr1, pos1)) if XQ(cr0) else ((cr1, pos1), (cr0, pos0)) # split the crossing and the vertex

    # get the lateral arc, left arc if arc is north of vertex
    lateral_arc_pos = (pos_cr-1)%4
    start_lateral_arc = cr[lateral_arc_pos] # 4 since normal crossing
    lateral_in = cr.inQ(lateral_arc_pos) # is lateral arc is ingoing relative to CCW (oriented lefto to right if arc is north
    lateral_over = cr.overQ(lateral_arc_pos) # is the lateral arc an overarc
    lateral_arc = start_lateral_arc

    # loop through the remaining of the arcs emanating from the crossings
    for i in range(len(vx)-1):
        pos = (pos_vx+1+i) % len(vx) # shift the index
        a, a_in = vx[pos], vx.inQ(pos)
        biv_lat, biv_ = cross_arcs(K, lateral_arc, a, sign = 1 if ((lateral_in ^ a_in) ^ lateral_over) else -1, over=lateral_over)
        lateral_arc = biv_lat[1 if lateral_in else 0]

    #print("OTHER-SIDE", cr[cr.move_forward(lateral_arc_pos)])
    #print("THIS SIDE", lateral_arc )

    cr_biv = Bivalent(cr[pos_cr], cr[cr.move_forward(pos_cr)]) if cr.inQ(pos_cr) else Bivalent(cr[cr.move_forward(pos_cr)], cr[pos_cr])
    end_biv = Bivalent(lateral_arc, cr[cr.move_forward(lateral_arc_pos)]) if cr.inQ(lateral_arc_pos) else Bivalent(cr[cr.move_forward(lateral_arc_pos)], lateral_arc)

    K.append_nodes([cr_biv, end_biv])
    K.remove_node(cr)
    K.remove_bivalent_nodes()

"""
def R4_poke(K, arc):
    """ poke through vertex, move needed to clear crossings at a bond"""
    if REIDEMEISTER_PRINT: print("  R4 poke on arc", arc, K)

    """
     |  /         |/
    -|-<  ->  ---<|
     |  \         |\
    """

    # get nodes involved
    (node0, pos0), (node1, pos1) = K.D(arc)
    if not (VQ(node0) ^ VQ(node1)): raise ValueError("Incorrect node types for poke.")

    # classify the nodes
    (v, pos_v, x, pos_x) = (node0, pos0, node1, pos1) if VQ(node0) else (node1, pos1, node0, pos0)

    pos_a, pos_b, pos_x_adj, pos_x_a_adj, pos_x_b_adj = (pos_v+1) % len(v), (pos_v+2) % len(v), (pos_x + 2) % len(x), (pos_x + 3) % len(x), (pos_x + 1) % len(x)
    arc_a, arc_b, arc_adj, arc_a_adj, arc_b_adj = v[pos_a], v[pos_b], x[pos_x_adj], x[pos_x_a_adj], x[pos_x_b_adj]
    arc_x_adj = x[pos_x_adj]
    new_arc_a, new_arc_b = max(K.arcs())+1, max(K.arcs())+2


    over_strand = x.underQ(pos_x)

    #print("Vertex:", v, "pos", pos_v, pos_a, pos_b)
    #print("Crossing:", x, "pos", pos_x, pos_x_a_adj, pos_x_b_adj)
    #print("arcs:", arc, arc_a, arc_b, arc_a_adj, arc_b_adj, new_arc_a, new_arc_b)
    #print("over:", over_strand)

    if x.inQ(pos_x_a_adj) and v.inQ(pos_a):
        new_crossing_a = Crossing([arc_a, arc, new_arc_a, arc_a_adj], +1)
    if x.inQ(pos_x_a_adj) and not v.inQ(pos_a):
        new_crossing_a = Crossing([new_arc_a, arc_a_adj, arc_a, arc], -1)
    if not x.inQ(pos_x_a_adj) and v.inQ(pos_a):
        new_crossing_a = Crossing([arc_a, arc, new_arc_a, arc_a_adj], -1)
    if not x.inQ(pos_x_a_adj) and not v.inQ(pos_a):
        new_crossing_a = Crossing([new_arc_a, arc_a_adj, arc_a, arc], +1)

    if x.inQ(pos_x_b_adj) and v.inQ(pos_b):
        new_crossing_b = Crossing([arc_b, arc_b_adj, new_arc_b, arc], -1)
    if x.inQ(pos_x_b_adj) and not v.inQ(pos_b):
        new_crossing_b = Crossing([new_arc_b, arc, arc_b, arc_b_adj], +1)
    if not x.inQ(pos_x_b_adj) and v.inQ(pos_b):
        new_crossing_b = Crossing([arc_b, arc_b_adj, new_arc_b, arc], +1)
    if not x.inQ(pos_x_b_adj) and not v.inQ(pos_b):
        new_crossing_b = Crossing([new_arc_b, arc, arc_b, arc_b_adj], -1)

    #print("NEW", new_crossing_a, new_crossing_b)
    if not over_strand:
        new_crossing_a.mirror()
        new_crossing_b.mirror()


    v[pos_v], v[pos_a], v[pos_b] = arc_x_adj, new_arc_a, new_arc_b


    #print("NEW", new_crossing_a, new_crossing_b)

    K.remove_node(x)
    K.append_nodes([new_crossing_a, new_crossing_b])


"""
def R4_unpoke_alt(K, area):
    pass

def OLD_R4_poke(K, arc):

    (cr0, pos0), (vx1, pos1) = K.D(arc) # get the two adjacent crossings, assume that the end one is a vertex
    if not XQ(cr0) or not VQ(vx1): raise ValueError("Incorrect node types for poke.")

    # get adjacent arcs
    pos_a, pos_b = vx1.CW(pos1), vx1.CCW(pos1)
    pos_c, pos_d, pos_e = cr0.CCW(pos0), cr0.CW(pos0), cr0.move_forward(pos0)
    arc_a, arc_b, arc_c, arc_d, arc_e = vx1[pos_a], vx1[pos_b], cr0[pos_c], cr0[pos_d], cr0[pos_e]

    arc_aa = max(K.arcs())+1
    arc_bb = arc_aa+1
    arc_f = vx1[pos1]

    #print(cr0, pos0, vx1, pos1)
    #print(pos_a, pos_b, pos_c, pos_d, pos_e)
    #print(arc_a, arc_b, arc_c, arc_d, arc_e)

    if cr0.overQ(pos0):
        if cr0.outQ(pos_c) and vx1.outQ(pos_a):
            cr_a = Crossing([arc_f, arc_a, arc_c, arc_aa], 1)
            cr_b = Crossing([arc_d, arc_b, arc_f, arc_bb], -1)
        if cr0.inQ(pos_c) and vx1.outQ(pos_a):
            cr_a = Crossing([arc_c, arc_aa, arc_f, arc_a], -1)
            cr_b = Crossing([arc_f, arc_bb, arc_d, arc_b], 1)
        if cr0.outQ(pos_c) and vx1.inQ(pos_a):
            cr_a = Crossing([arc_f, arc_a, arc_c, arc_aa], -1)
            cr_b = Crossing([arc_d, arc_b, arc_f, arc_bb], 1)
        if cr0.inQ(pos_c) and vx1.inQ(pos_a):
            cr_a = Crossing([arc_c, arc_aa, arc_f, arc_a], 1)
            cr_b = Crossing([arc_f, arc_bb, arc_d, arc_b], -1)
    else:
        if cr0.outQ(pos_c) and vx1.outQ(pos_a):
            cr_a = Crossing([arc_aa, arc_f, arc_a, arc_c], -1)
            cr_b = Crossing([arc_b, arc_f, arc_bb, arc_d], 1)
        if cr0.inQ(pos_c) and vx1.outQ(pos_a):
            cr_a = Crossing([arc_aa, arc_f, arc_a, arc_c], 1)
            cr_b = Crossing([arc_b, arc_f, arc_bb, arc_d], -1)
        if cr0.outQ(pos_c) and vx1.inQ(pos_a):
            cr_a = Crossing([arc_a, arc_c, arc_aa, arc_f], 1)
            cr_b = Crossing([arc_bb, arc_d, arc_b, arc_f], -1)
        if cr0.inQ(pos_c) and vx1.inQ(pos_a):
            cr_a = Crossing([arc_a, arc_c, arc_aa, arc_f], -1)
            cr_b = Crossing([arc_bb, arc_d, arc_b, arc_f], 1)


    #print(cr_a, cr_b)

    vx1[pos_a] = arc_aa
    vx1[pos_b] = arc_bb
    vx1[pos1] = cr0[pos_e] # replace middle arc of vertex



    del K.nodes[K.nodes.index(cr0)]
    K.nodes.append(cr_a)
    K.nodes.append(cr_b)
    pass
"""

def R4_unpoke(K, area):
    if REIDEMEISTER_PRINT: print("  R4 unpoke on area", area, K)

    # classify the arcs
    for i, (a,s) in enumerate(area):
        if K.middleQ(a):
            (arc_m, side_m), arc_a, arc_b = (a, s), area[(i+1)%3][0], area[(i+2)%3][0]
            break
    nodes = area_nodes(K, area)
    nodes_m = [node for node in nodes if VQ(node)]
    if len(nodes_m) != 1: raise ValueError("There should be only one middle vertex node in R4 move.")
    node_m = nodes_m[0]
    # adjacent to middle
    arc_m_adj_singleton = node_m.arc_set() - {arc_a, arc_b}
    if len(arc_m_adj_singleton) != 1: raise ValueError("There should be only one adjacent middle arc in R4 move.")
    arc_m_adj = arc_m_adj_singleton.pop()
    # adjacent to side arcs
    (node_b, pos_m_b), (node_a, pos_m_a) = K.D(arc_m) if side_m else K.D(arc_m)[::-1]

    if DEBUG_REIDEMEISTER: print("R4 unpoke", K, "\n",node_a, node_b, arc_a, arc_b)

    pos_m_a_adj, pos_m_b_adj = (pos_m_a+2)%4, (pos_m_b+2)%4
    arc_m_a_adj, arc_m_b_adj= node_a[pos_m_a_adj], node_b[pos_m_b_adj]
    pos_a, pos_b = node_a.arcs.index(arc_a), node_b.arcs.index(arc_b),
    pos_a_adj, pos_b_adj = (pos_a+2)%4, (pos_b+2)%4
    arc_a_adj, arc_b_adj = node_a[pos_a_adj], node_b[pos_b_adj]
    pos_v_a, pos_v_b, pos_v_adj = node_m.index(arc_a), node_m.index(arc_b), node_m.index(arc_m_adj)
    if DEBUG_REIDEMEISTER: print("R4 unpoke.", "Arcs:", arc_m, arc_a, arc_b ,"Nodes:",node_m, node_a, node_b, "adjacent", arc_m_adj, arc_a_adj, arc_b_adj, arc_m_a_adj, arc_m_b_adj)
    if DEBUG_REIDEMEISTER: print("Vertex positions:", pos_v_adj, pos_v_a, pos_v_b)

    if node_a.overQ(pos_m_a) != node_b.overQ(pos_m_b): raise ValueError("Middle arc must be and over or under strand in R4 poke.")
    arc_m_is_over = node_a.overQ(pos_m_a)

    arc_new = arc_m
    b_adj_in = node_m.inQ(pos_v_adj)
    if b_adj_in:
        new_crossing = Crossing([arc_m_adj,arc_m_b_adj,arc_new,arc_m_a_adj],-1 if side_m else +1)
    else:
        new_crossing = Crossing([arc_new, arc_m_a_adj, arc_m_adj, arc_m_b_adj], +1 if side_m else -1)

    if not arc_m_is_over:
        new_crossing.mirror()

    node_m[pos_v_adj], node_m[pos_v_a], node_m[pos_v_b] = arc_new, arc_a_adj, arc_b_adj

    K.remove_nodes([node_a, node_b])
    K.append_node(new_crossing)




# REIDEMEISTER MOVE 5

def R5_twist(K, arc, arc_side = None, sign = None):
    """
    :param K:
    :param arc:
    :param arc_side: either 0 or 1
    :param sign: +1 or -1
    :return:
    """


    (node0, pos0), (node1, pos1) = K.D(arc)

    if arc_side is None:
        arc_side = choice([i for i in (0, 1) if VQ([node0, node1][i])])
    if sign is None:
        sign = choice([+1, -1])


    if REIDEMEISTER_PRINT: print("  R5 twist on arc", arc, "side", arc_side, "sign", sign, K)

    (node, pos) = [(node0, pos0), (node1, pos1)][arc_side]  # choose the node/pos

    pos_a, pos_b = (pos + 1) % len(node), (pos + 2) % len(node)
    arc_a, arc_b = node[pos_a], node[pos_b]
    new_arc_a, new_arc_b = max(K.arcs())+1, max(K.arcs())+2

    # create new crossing
    if node.inQ(pos_a) and node.inQ(pos_b):     new_crossing = Crossing([arc_b, new_arc_a, new_arc_b, arc_a], 1)
    if node.inQ(pos_a) and not node.inQ(pos_b): new_crossing = Crossing([arc_a, arc_b, new_arc_a, new_arc_b], 1)
    if not node.inQ(pos_a) and node.inQ(pos_b): new_crossing = Crossing([new_arc_a, new_arc_b, arc_a, arc_b], 1)
    if not node.inQ(pos_a) and not node.inQ(pos_b): new_crossing = Crossing([new_arc_b, arc_a, arc_b, new_arc_a], 1)

    if sign < 0:
        new_crossing.mirror()

    # reattach old crossing
    node[pos_a], node[pos_b] = new_arc_b, new_arc_a
    node.color[pos_a], node.color[pos_b] = node.color[pos_b], node.color[pos_a] # exchange colors
    node.ingoingB[pos_a], node.ingoingB[pos_b] = node.ingoingB[pos_b], node.ingoingB[pos_a] # exchange directions

    K.append_node(new_crossing)

def R5_untwist(K, area):
    """ Only workd for 4-valent nodes"""


    if REIDEMEISTER_PRINT: print("  R5 untwist on area", area, K)


    arc_a, arc_b = area[0][0], area[1][0]

    (cr_a_0, pos_a_0), (cr_a_1, pos_a_1) = K.D(arc_a)
    (cr_b_0, pos_b_0), (cr_b_1, pos_b_1) = K.D(arc_b)
    (v_a, pos_v_a, x_a, pos_x_a) = (cr_a_0, pos_a_0, cr_a_1, pos_a_1) if VQ(cr_a_0) else (cr_a_1, pos_a_1, cr_a_0, pos_a_0)
    (v_b, pos_v_b, x_b, pos_x_b) = (cr_b_0, pos_b_0, cr_b_1, pos_b_1) if VQ(cr_b_0) else (cr_b_1, pos_b_1, cr_b_0, pos_b_0)
    if v_a != v_b or x_a != x_b: raise ValueError("Nodes are not the same in unwind.")

    arc_a_adj, arc_b_adj = x_a[(pos_x_a+2) % 4], x_b[(pos_x_b+2) % 4]
    v_a[pos_v_a], v_b[pos_v_b] = arc_b_adj, arc_a_adj  # change arc from vertex
    v_a[pos_v_a], v_b[pos_v_b] = arc_b_adj, arc_a_adj  # change color from vertex
    v_a.color[pos_v_a], v_b.color[pos_v_b] = v_b.color[pos_v_b], v_a.color[pos_v_a]  # exchange colors
    v_a.ingoingB[pos_v_a], v_b.ingoingB[pos_v_b] = v_b.ingoingB[pos_v_b], v_a.ingoingB[pos_v_a]  # exchange colors

    K.remove_node(x_a)



"""
g = Knotted([
    Vertex([0], ins=[]),
    Vertex([1], colors=[0], ins=[]),
    Vertex([2], colors=[0], ins=[]),
    Vertex([0,1,2],colors=[0,0,0],ins=[0,1,2])
])
"""








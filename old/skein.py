from crossing import *
from knotted import *

def skein_sign(knot, node):
    """ skein operation making a crossing change"""
    node_index = knot.nodes.index(node)
    K = knot.copy()
    K.nodes[node_index].mirror()
    return K

def skein_0(knot, node):
    """ split the crossing, coherently oriented"""
    node_index = knot.nodes.index(node)
    K = knot.copy()
    new_node = K.nodes[node_index]
    if new_node.sign == 1:
        biv_a, biv_b = Bivalent(new_node[0], new_node[1]), Bivalent(new_node[3], new_node[2])
    else:
        biv_a, biv_b = Bivalent(new_node[0], new_node[3]), Bivalent(new_node[1], new_node[2])

    del K.nodes[node_index]
    K.nodes += [biv_a, biv_b]
    K.remove_bivalent_nodes()
    return K


def skein_remove_bond(knot, arc):
    # removes the bond arc

    #print("REMOVE BOND", knot, arc)

    K = knot.copy()

    (cr0, pos0), (cr1, pos1) = K.D(arc)
    if cr0[pos0] != cr1[pos1]:
        raise ValueError("Cannot remove bond with crossings.")
    if cr0.color[pos0] == 0 or cr1.color[pos1] == 0:
        raise ValueError("Cannot remove uncolored bond.")

    # create singletons
    in0 = cr0.in_arc_set() - {arc}
    out0 = cr0.out_arc_set() - {arc}
    in1 = cr1.in_arc_set() - {arc}
    out1 = cr1.out_arc_set() - {arc}

    #print(in0,out0,in1, out1)

    if len(in0) != 1 or len(out0) != 1 or len(in1) != 1 or len(out1) != 1:
        raise ValueError("In/out sets should be singletons.")

    biv0 = Bivalent(in_arc=in0.pop(), out_arc=out0.pop())
    biv1 = Bivalent(in_arc=in1.pop(), out_arc=out1.pop())

    #print("removing", cr0, cr1,"adding",biv0, biv1, "to",knot)

    K.remove_node(cr0)
    K.remove_node(cr1)
    K.nodes.append(biv0)
    K.nodes.append(biv1)

    K.remove_bivalent_nodes()


    #print("RESULT", K)
    return K


def skein_reconnect_at_bond(knot, arc):
    # removes the bond arc and reconfigure the arcs

    K = knot.copy()
    (cr0, pos0), (cr1, pos1) = K.D(arc)

    # is the bond parallel or anti-parallel?
    parallel = K.parallel_bond_arcQ(arc)



    K.remove_node(cr0)
    K.remove_node(cr1)

    #print("parallel" if parallel else "antiparallel")

    if parallel:
        # parallel bond

        ccw0_pos, cw0_pos = cr0.CCW(pos0), cr0.CW(pos0)
        ccw1_pos, cw1_pos = cr1.CCW(pos1), cr0.CW(pos1)

        if cr0.inQ(ccw0_pos) and cr0.outQ(cw0_pos) and cr1.outQ(ccw1_pos) and cr1.inQ(cw1_pos):
            K.nodes.append(Crossing([cr1[cw1_pos], cr0[ccw0_pos], cr0[cw0_pos], cr1[ccw1_pos]], -1))
        elif cr0.outQ(ccw0_pos) and cr0.inQ(cw0_pos) and cr1.inQ(ccw1_pos) and cr1.outQ(cw1_pos):
            K.nodes.append(Crossing([cr0[cw0_pos], cr1[ccw1_pos], cr1[cw1_pos], cr0[ccw0_pos]], -1))
        else:
            raise ValueError("Crossing configuration wrong at parallel bond.")


    else:

        in0 = cr0.in_arc_set() - {arc}
        out0 = cr0.out_arc_set() - {arc}
        in1 = cr1.in_arc_set() - {arc}
        out1 = cr1.out_arc_set() - {arc}

        if len(in0) != 1 or len(out0) != 1 or len(in1) != 1 or len(out1) != 1:
            raise ValueError("In/out sets should be singletons.")

        in0, out0, in1, out1 = in0.pop(), out0.pop(), in1.pop(), out1.pop()  # get the arcs


        # anti-parallel bond
        K.nodes.append(Bivalent(in_arc=in0, out_arc=out1))
        K.nodes.append(Bivalent(in_arc=in1, out_arc=out0))
        K.remove_bivalent_nodes()


    return K

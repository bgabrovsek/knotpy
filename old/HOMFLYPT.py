from knotted import *
from module import *
from reidemeister_moves import *
import reidemeister_walk
from random import choice
from skein import *
from drawknot import *

from sympy import symbols
from sympy import simplify as sy_simplify
#from sympy.abc import v, z #l, m
from sympy.abc import l, m

# HOMFLYPT generators
#gen_H, gen_H_bar, gen_Theta, gen_Theta_bar = symbols('H h Θ ϑ')
#gen_H, gen_H_bar, gen_Theta, gen_Theta_bar = symbols('H H Θ Θ')

gen_Theta, gen_Theta_bar, gen_H, gen_H_bar = symbols('Θ ϑ H h')
gen_Theta_list = symbols("Θ0 Θ1 Θ2 Θ3 Θ4 Θ5")

DEBUG_HOMFLYPT = False

def choose_overpath_skein_node(K):
    """
    choose a node s.t. it is good to perform a skein
    """
    components = K.components()
    min_len = min([len(c) for c in components])
    component = choice([c for c in components if len(c) == min_len])  # choose a component with minimal length

    # list of tuples (crossing, position) for the component
    #print(K, "\n","COMP",component)
    cp_list = [K.D(arc)[0] for arc in component]
    #print(cp_list)
    cp_non_self_list = [(c, p) for c, p in cp_list if c[c.CCW(p)] not in component]  # select non-self intersection nodes

    over_crossings = [c for c, p in cp_non_self_list if c.overQ(p)]
    under_crossings = [c for c, p in cp_non_self_list if c.underQ(p)]

    if len(over_crossings) < len(under_crossings):
        return choice(over_crossings)
    elif len(over_crossings) > len(under_crossings):
        return choice(under_crossings)
    return choice(under_crossings + over_crossings)


def HOMFLYPT_polynomial(knot, depth = 0):
    """ Computes the HOMFLYPT polynomial in variables l and m
        following the relation l * L+ + (1/l) * L- + m * L0  = 0
                        or (1/v) * L+ - v * L- = z * L0
    """

    # make a copy of the knot
    knot_copy = knot.copy()
    # simplify and split components
    components = reidemeister_walk.simplify_and_split(knot_copy)

    # simplify each component
    for K in components:
        reidemeister_walk.decreasing_simplify(K, make_canonical=False)

    if DEBUG_HOMFLYPT:
        print("· "*depth, components,"#COMPONENTS =", len(components))

    if len(components) == 1:
        # if knot is not split (disjoint sum)
        K = components[0]  # take the compoennt
        if unknotQ(K): return 1  # unknot has value 1

        # select 2-region and make a crossing change
        areas = reidemeister_walk.find_areas(K, 2, alternating=True)

        if not len(areas):
            # there are no 2-areas
            if len(K.components()) == 1:
                # if we have a 1-component knot and no 3-areas, we cannot perform a skein reduction to simplify
                if depth > 30:
                    raise ValueError("Knot has no 2-region to perform a skein reduction.","\n",K,K.bondedQ(),"\n")
                # try performing a R3 move to obtain some 2-areas
                if not reidemeister_walk.random_R3_move(K):
                    raise ValueError("Cannot perform R3,",K)
                return HOMFLYPT_polynomial(K, depth+1)

            # make overpasses and reduce number of components

            # TODO: choose node s.t. least number of skeins necessary

            node = choose_overpath_skein_node(K)
        else:
            # there are 2-areas
            area = choice(areas)  # choose a 2-area
            nodes = area_nodes(K, area)
            node = nodes[choice((0, 1))]  # choose a crossing in the 2-area

        #if depth == 0:
        #    print(node)
        #    print("THE KNOT:", K)
        # make the crossing change
        if node.sign > 0:

            # POSITIVE
            K_minus = skein_sign(K, node)
            K_0 = skein_0(K, node)

            #if depth == 0:
            #    print("KNOT", K)
            #    print("KNOT MINUS", K_minus)

            polynomial_minus = HOMFLYPT_polynomial(K_minus, depth+1)

            #if depth == 0:
            #    print("POLY MINUS", polynomial_minus)
            #    print("KNOT ZERO", K_0)

            polynomial_0 = HOMFLYPT_polynomial(K_0, depth+1)

            #if depth == 0:
            #    print("POLY ZERO", polynomial_0)

            if DEBUG_HOMFLYPT: print("· "*depth, "[+ skein] on",node,": v^2",K_minus,"+","vz", K_0)

            #polynomial = (v*v) * polynomial_minus + (v*z) * polynomial_0
            polynomial = (-l**(-2)) * polynomial_minus - (m/l) * polynomial_0




        else:
            # NEGATIVE

            K_plus = skein_sign(K, node)
            K_0 = skein_0(K, node)

            #if depth == 0:
            #    print(depth, "KNOT", K)
            #    print(depth, "KNOT PLUS", K_plus)

            polynomial_plus = HOMFLYPT_polynomial(K_plus, depth + 1)

            #if depth == 0:
            #    print(depth, "POLY PLUS", polynomial_plus)
            #    print(depth, "KNOT ZERO", K_0)


            polynomial_0 = HOMFLYPT_polynomial(K_0, depth + 1)

            #if depth == 0:
            #    print(depth, "POLY ZERO", polynomial_0)


            if DEBUG_HOMFLYPT: print("· "*depth, "[- skein] on",node,": v^-2",K_plus,"-","z/v", K_0)

            #polynomial = (1/v * 1/v) * polynomial_plus - (z/v) * polynomial_0
            polynomial = (-l*l) * polynomial_plus - (l*m) * polynomial_0

    else:
        polynomial = ((-l-l**(-1)) / m)**(len(components)-1)
        poly_components = [HOMFLYPT_polynomial(K, depth+1) for K in components]
        if DEBUG_HOMFLYPT: print("· " * depth, "[disjoint sum] :", "(v^-1-v)/z","+".join([str(p) for p in poly_components]))
        for p in poly_components:
            polynomial *= p


    polyn = sy_simplify(polynomial)

    return polyn


def HSM(knot, refined=False, rigid=False, colored=None, depth=0):
    """
    :param knot:
    :param refined: should we cancel terms at the end (this makes poly longer, but no divisions)
    :param depth: # internal parameter
    :param rigid: # compute the rigid version
    :return:
    """

    """
    Computes the HOMFLYPT skein module of a bonded knot.
    :param K: bonded knot
    :return: the HOMFLYPT skein module
    """

    if colored is None:
        # autodetect if knot is colored (has more than one color)
        colored = bool(knot.colors()) and max(knot.colors()) >= 2


    if not knot.bondedQ():
        return HOMFLYPT_polynomial(knot, depth)

    knot_simpl = knot.copy()
    reidemeister_walk.decreasing_simplify(knot_simpl, make_canonical=False, rigid=rigid)
    K = reidemeister_walk.isolate_bonds(knot_simpl)  # isolate the bonds, so they do not contain crossings

    hsm = 1

    # get a bond
    arc, bond_color = K.pop_bond_arc()

    if arc is None:
        # knot is w/o bonds

        L = K.copy()
        reidemeister_walk.decreasing_simplify(L, make_canonical=False, rigid=rigid)
        h = HOMFLYPT_polynomial(K)
        return h
    else:
        K_wo = skein_remove_bond(K, arc)
        K_reconf = skein_reconnect_at_bond(K, arc)
        K_reconf.name += "cb"
        K_wo.name += "wo"

        HSM_wo = HSM(K_wo, refined=refined, depth=depth + 1, colored=colored, rigid=rigid)
        HSM_reconf = HSM(K_reconf, refined=refined, depth=depth + 1,colored=colored, rigid=rigid)

        #if depth == 0:
        #    print("H WO", HSM_wo)
        #    print("H RE", HSM_reconf)

        if rigid and colored:
            raise ValueError("Not yet implemented.")
        elif rigid and not colored:
            GEN_H_TYPE = gen_H_bar if K.parallel_bond_arcQ(arc) else gen_H
            GEN_THETA_TYPE = gen_Theta_bar if K.parallel_bond_arcQ(arc) else gen_Theta
        elif not rigid and colored:
            Theta_color = gen_Theta_list[bond_color]
            GEN_H_TYPE = (-1 - l * l) / (l * m) * Theta_color
            GEN_THETA_TYPE = Theta_color


        else:
            GEN_H_TYPE = (-1 - l * l) / (l * m) * gen_Theta
            GEN_THETA_TYPE = gen_Theta

        #GEN_H_TYPE = gen_H_bar if K.parallel_bond_arcQ(arc) else gen_H
        #GEN_THETA_TYPE = gen_Theta_bar if K.parallel_bond_arcQ(arc) else gen_Theta


        hsm = ((l ** 2 * m ** 2) * GEN_H_TYPE + (l ** 3 * m ** 3) / (1 + l ** 2) * GEN_THETA_TYPE) * HSM_wo + \
              ((l ** 2 * m ** 2) * GEN_THETA_TYPE + (l ** 3 * m ** 3) / (1 + l ** 2) * GEN_H_TYPE) * HSM_reconf

        hsm /= (l ** 4 + 2 * (l ** 2) + 1 - l ** 2 * m ** 2)

        if refined and rigid:
            if depth > 0:
                hsm *= (l ** 4 + 2 * (l ** 2) + 1 - l ** 2 * m ** 2)
            hsm *= (1+l**2) / (l**2 * m**2)

        if refined and not rigid:
            if depth > 0:
                hsm *= -(1+l**2) / (l * m)


        if depth == 0:
            hsm *= -(l+l**-1)/m # since there is an additional unknot, that does not form the generating set


        return sy_simplify(hsm)


def test_HOMFLYPT_skein_relation(knot):

    colored_arcs = knot.color_arc_set(1) # get colored arcs

    for node in knot.filter_nodes(XQ):
        if set(node.arcs) & colored_arcs: continue

        if node.sign > 0 :

            knot_plus = knot.copy()
            knot_minus = skein_sign(knot, node)
            knot_0 = skein_0(knot, node)


            expression = l * HSM(knot_plus) + l**-1 * HSM(knot_minus) + m*HSM(knot_0)
            if sy_simplify(expression) != 0:
                print("=K+ :", knot_plus)
                print(" K- :", knot_minus)
                print(" K0 :", knot_0)
                print("=P+ :", HSM(knot_plus))
                print(" P- :", HSM(knot_minus))
                print(" P0 :", HSM(knot_0))
                print("  ", sy_simplify(expression), "= 0\n")
                return False
                print("\nSKEIN DOES NOT HOLD\n", knot, node,"\n",knot_plus,"\n",knot_minus, "\n",knot_0)
                return False

        else:
            knot_minus = knot.copy()
            knot_plus = skein_sign(knot, node)
            knot_0 = skein_0(knot, node)

            expression = l * HSM(knot_plus) + l**-1 * HSM(knot_minus) + m * HSM(knot_0)
            if sy_simplify(expression) != 0:
                print(" K+ :", knot_plus)
                print("=K- :", knot_minus)
                print(" K0 :", knot_0)
                print(" P+ :", HSM(knot_plus))
                print("=P- :", HSM(knot_minus))
                print(" P0 :", HSM(knot_0))
                print("  ", sy_simplify(expression),"= 0\n")
                return False
                print("\nSKEIN DOES NOT HOLD\n", knot, node, "\n", knot_plus, "\n", knot_minus, "\n", knot_0,"\nResult:",expression)
                return False
    return True

def equal(poly_a, poly_b):
    return sy_simplify(poly_a - poly_b) == 0


def print_hsm(h):
    s = str(h)
    for a,b in [("**","^"), ("ϑ","T"), ("Θ","T"), ("h","H")]:
        s = s.replace(a,b)
    print(s)

# TREFOIL 1
"""
if True:


    k_cn = Knotted(nodes = [
        Cm(6,0,7,1), Cp(8,4,9,3), Cm(11,5,0,6),
        V([1,2,12],12,[1]), V([9,10,12],12,[9,12]),
        V([2,13,3],13,[2]), V([7,8,13],13,[7,13]),
        V([4,5,14],14,[4]), V([10,14,11],14,[10,14])
    ])

    k_ad = Knotted(nodes = [
        Cm(3,11,4,12), Cm(4,9,5,10),
        V([0,8,1],8,[0]), V([5,8,6],8,[5,8]),
        V([1,9,2],9,[1]), V([6,7,10],10,[6,10]),
        V([2,11,3],11,[2]), V([0,12,7], 12, [7,12])
    ])

    #plot_knot(k_cn, "CN.pdf")

    #plot_knot(k_ad, "AD.pdf")

    ha = HSM(k_cn, refined=True)

    print()
    hb = HSM(k_ad, refined=True)


    print_hsm(ha)
    print(str(ha).count("/"), len(str(ha)))
    print_hsm(hb)
    print(str(hb).count("/"), len(str(hb)))

    print("\n\n")


    T1 = Knotted(nodes=[
        Crossing([0,4,1,6],+1), Crossing([4,2,5,1],+1), Crossing([2,7,3,5],+1),
        Vertex([0,8,7], colors=[0,0,1], ingoingB=[False, True, True]), Vertex([3,8,6], colors=[0,0,1], ingoingB=[True, False, False]),
    ])

    T2 = Knotted(nodes=[
        Crossing([0,4,1,6],+1), Crossing([4,2,5,1],+1), Crossing([2,7,3,5],+1),
        Vertex([0,8,7], colors=[1,0,0], ingoingB=[False, False, True]), Vertex([3,8,6], colors=[1,0,0], ingoingB=[True, True, False]),
    ])



    tref_2 = Knotted(nodes=[
        Crossing([0,6,1,5],+1), Crossing([6,2,7,1],+1), Crossing([2,8,3,7],+1),
        Vertex([0,4,8], colors=[0,0,1], ingoingB=[False, True, True]), Vertex([3,4,5], colors=[0,0,1], ingoingB=[True, False, False]),
    ])


    tref_2B = Knotted(nodes=[
        Crossing([0,6,1,5],-1), Crossing([7,1,6,2],-1), Crossing([2,8,3,7],-1),
        Vertex([0,4,8], colors=[0,0,1], ingoingB=[False, True, False]), Vertex([3,4,5], colors=[0,0,1], ingoingB=[True, False, True]),
    ])

    tref_3 = Knotted(nodes=[
        Crossing([5,2,6,1],+1), Crossing([2,7,3,6],+1), Crossing([7,4,8,3],+1),
        Vertex([0,1,8], colors=[0,0,1], ingoingB=[True, False, True]), Vertex([0,4,5], colors=[0,0,1], ingoingB=[False, True, False]),
    ])



    tref_1 = Knotted(nodes=[
        Crossing([0,5,1,4],+1), Crossing([5,2,6,1],+1), Crossing([2,7,3,6],+1),
        Vertex([7,0,8], colors=[0,0,1], ingoingB=[True, False, False]), Vertex([4,3,8], colors=[0,0,1], ingoingB=[False, True, True]),
    ])



    tref_2 = Knotted(nodes=[
        Crossing([0,6,1,5],+1), Crossing([6,2,7,1],+1), Crossing([2,8,3,7],+1),
        Vertex([0,4,8], colors=[0,0,1], ingoingB=[False, True, True]), Vertex([3,4,5], colors=[0,0,1], ingoingB=[True, False, False]),
    ])



    print("[TREF 1]")
    h1 = HSM(tref_1, refined=True)
    print_hsm(h1)
    print("\n")
    print("[TREF 2]")
    h1 = HSM(tref_2, refined=True)
    print_hsm(h1)


    exit()

    print(str(HSM(T1)).replace("**","^"))
    print(str(HSM(T2)).replace("**","^"))

    print()

    print(str(HSM(tref_1)).replace("**","^"))
    print(str(HSM(tref_2)).replace("**","^"))
    print(str(HSM(tref_2B)).replace("**","^"))
    print(str(HSM(tref_3)).replace("**","^"))

    print()

    print(str(HSM(tref_1, refined=True)).replace("**","^"))
    print(str(HSM(tref_2, refined=True)).replace("**","^"))
    print(str(HSM(tref_2B, refined=True)).replace("**","^"))
    print(str(HSM(tref_3, refined=True)).replace("**","^"))

"""
from copy import deepcopy
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.region_algorithms import choose_kink, choose_poke
from knotpy.manipulation.reidemeister import remove_kink, remove_poke




def __bracket_polynomial(k, reduce=False):

    from sympy import Expr, expand, Integer, symbols
    from collections import deque
    from knotpy.utils.decorators import single_variable_invariant
    from knotpy.algorithms.skein import smoothing_type_A, smoothing_type_B

    _debug = False

    A = symbols("A")

    if k.is_oriented():
        raise NotImplemented("Oriented case not yet implemented")  # TODO: convert to unoriented version

    kauff_term = (-A**2 - 1 / A**2)
    framing_term = (-A**(3))
    polynomial = Integer(0)
    stack = deque()
    stack.append((Integer(1), k))

    #print("ok")

    while stack:
        #print("pop")
        poly, k = stack.pop()

        if reduce:
            simplify(k, in_place=True)

        #print("k", k)
        if k.crossings:
            crossing = next(iter(k.crossings))
            #print("SKEIN")
            kA = smoothing_type_A(k, crossing)
            kB = smoothing_type_B(k, crossing)

            #print("A", kA)
            #print("B", kB)
            stack.append((poly * A, kA))
            stack.append((poly / A, kB))

        else:
            polynomial += poly * (kauff_term ** (k.number_of_nodes - 1)) * (framing_term ** k.framing)

    return expand(polynomial)



def simplify(k: PlanarDiagram, in_place=True):

    _debug = False



    if not in_place:
        k = deepcopy(k)

    changes_made = True

    while changes_made:

        changes_made = False

        while kink := choose_kink(k):

            if _debug:
                kc = deepcopy(k)
                poly_1 = __bracket_polynomial(kc)
            remove_kink(k, kink)

            if _debug:
                poly_2 = __bracket_polynomial(k)
                if poly_1 != poly_2:
                    print("Wrong unkink:")
                    print("before removal", kc)
                    print(" after removal", k)
                    print("poly before removal", poly_1)
                    print(" poly after removal", poly_2)

            changes_made = True
        while poke := choose_poke(k):

            if _debug:
                kc = deepcopy(k)
                poly_1 = __bracket_polynomial(kc)


            remove_poke(k, poke)

            if _debug:
                poly_2 = __bracket_polynomial(k)
                if poly_1 != poly_2:
                    print("Wrong unkink:")
                    print("mod", k)
                    print("ori", kc)
                    print("poke", poke)
                    print("p1",poly_1)
                    print("p2",poly_2)

            changes_made = True

    return k



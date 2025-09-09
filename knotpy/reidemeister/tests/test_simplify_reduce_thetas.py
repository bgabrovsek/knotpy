import knotpy as kp
from knotpy import canonical
from knotpy.algorithms.sanity import sanity_check


def test_simplify_thetas():
    # Take a minimal diagram, make random Reidemeister moves and simplify it to the original

    theta = kp.PlanarDiagram("t3_1")

    for i in range(5):
        # make the diagram more complicated
        #print(kp.canonical(theta))
        theta_mod = kp.randomize_diagram(theta, number_of_moves=1)

        # print(theta_mod)

        # the Yamadas should be the same
        assert kp.yamada(theta) == kp.yamada(theta_mod)

        # simplify the modified theta curve

        theta_simplified = kp.simplify(theta_mod, depth=1)  # probably depth 0 is enough (no increasing moves)

        # the canonical forms should be the same
        #kp.export_pdf([theta, theta_mod, theta_simplified], f"test_simplify_thetas {i}.pdf", with_labels=True)

        # print(kp.canonical(theta_simplified))

        # print()
        # print("##1")
        # print(canonical(theta))
        # print("##2")
        # print(canonical(theta_simplified))
        # kp.export_pdf([theta, theta_simplified], f"test_simplify_theta.pdf", with_labels=True)

        assert kp.canonical(theta) == kp.canonical(theta_simplified)


def test_reduce_thetas():

    theta1 = kp.PlanarDiagram("t3_1")
    theta2 = kp.PlanarDiagram("t4_1")

    # 4 different diagrams of two theta curves
    list_of_thetas = [
        theta1,
        kp.randomize_diagram(theta1, 1),
        kp.randomize_diagram(theta1, 1),
        kp.randomize_diagram(theta1, 1),
        theta2,
        kp.randomize_diagram(theta2, 1),
        kp.randomize_diagram(theta2, 1),
        kp.randomize_diagram(theta2, 1),
    ]

    # reduce the list
    # reduce_equivalent_diagrams returns a dictionary, the key is the reduced knot (diagram) and the values are diagrams that are reduced to the key
    reduced = kp.reduce_equivalent_diagrams(list_of_thetas, depth=1)  # probably depth 0 is enough (no increasing moves)

    for key in reduced:
        # print("The following diagrams are equivalent to", key)
        for value in reduced[key]:
            # print("   ", value)
            # the yamada polynomials for each group is the same
            assert kp.yamada(value) == kp.yamada(key)

    # we expect the list to reduce to two different thetas
    assert len(reduced) == 2

def test_wanda():
    groups = {}
    groups["Unknown"] = ['V[0,1,2],V[3,4,5],V[6,5,7],V[1,8,9],X[0,3,6,8],X[4,2,9,7]',
                         'V[0,1,2],V[0,3,4],V[3,5,6],V[2,7,5],X[4,8,9,1],X[8,6,7,9]']
    groups['h2_1.1#_3h2_1.2'] = ['V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,2,8,9],X[1,5,10,8],X[9,10,4,7]',
                                 'V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,2,8,7],X[9,10,4,8],X[1,5,10,9]',
                                 'V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,8,4,7],X[9,10,8,2],X[1,5,10,9]']


    for t, G in groups.items():
        list_of_bonded = [kp.from_pd_notation(pd) for pd in G]
        # print(list_of_bonded)
        for k in list_of_bonded:
            assert sanity_check(k)
        # reduced = kp.reduce_equivalent_diagrams(list_of_bonded, depth=2)

        # for key, value in reduced.items():
            # print(key)
            # print("    ", value)
            # for v in value:
            #     print("   ", v)
        # print(t, len(G), len(reduced), [len(v) for k, v in reduced.items()])
        # print(reduced)
        # print("**")


def test_reduce_groups_bonded():
    groups = {}
    groups["Unknown"] = ['V[0,1,2],V[3,4,5],V[6,5,7],V[1,8,9],X[0,3,6,8],X[4,2,9,7]',
                         'V[0,1,2],V[0,3,4],V[3,5,6],V[2,7,5],X[4,8,9,1],X[8,6,7,9]']
    groups['h2_1.1#_3h2_1.2'] = ['V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,2,8,9],X[1,5,10,8],X[9,10,4,7]',
                                 'V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,2,8,7],X[9,10,4,8],X[1,5,10,9]',
                                 'V[0,1,2],V[3,4,5],X[0,6,7,3],X[6,8,4,7],X[9,10,8,2],X[1,5,10,9]']

    # 2 2 0 0
    # 3 1 2
    for t, G in groups.items():
        list_of_bonded = [kp.from_pd_notation(pd) for pd in G]
        reduced = kp.reduce_equivalent_diagrams(list_of_bonded, depth=1)
        #print(t, len(G), len(reduced), [len(v) for k, v in reduced.items()])
        #print(reduced)
        #print("**")

def test_theta_r4():
    pass
    # from knotpy.reidemeister.reidemeister import r4_generator
    #
    #
    # theta = kp.PlanarDiagram("+t3_1")
    # theta.name = None
    # print(theta)
    # print("")
    #
    # h = kp.from_knotpy_notation("a → V(h1 i1 e0), b → V(h3 h2 e3), c → X(i3 e2 e1 i0), e → X(a2 c2 c1 b2), h → X(i2 a0 b1 b0), i → X(c3 a1 h0 c0)")
    # for m in kp.crossing_non_increasing_space(h, greediness=1, assume_canonical=False):
    #     print(m)
    #
    # exit()
    # print(theta)
    # print()
    # for t in r4_generator(theta):
    #
    #     print(t)
    #     print(tt :=kp.canonical(kp.simplify_smart(t, depth=1)))
    #     print(theta == tt, theta < tt)
    #     print()

if __name__ == '__main__':
    test_reduce_groups_bonded()
    test_simplify_thetas()

    # a = kp.from_knotpy_notation("a → V(b0 c0 d3), b → V(a0 d2 e3), c → X(a1 e2 e1 d0), d → X(c3 e0 b1 a2), e → X(d1 c2 c1 b2)")
    # b = kp.from_knotpy_notation("a → V(b0 c0 d3), b → X(a0 e0 e3 c1), c → V(a1 b3 d0), d → X(c2 e2 e1 a2), e → X(b1 d2 d1 b2)")
    #
    # kp.export_pdf([a,b],"ab.pdf")
    test_theta_r4()
    #
    test_simplify_thetas()
    test_reduce_thetas()
    test_wanda()

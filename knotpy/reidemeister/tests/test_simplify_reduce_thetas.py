import knotpy as kp
from sandbox.classification_knotoids.knotpy.drawing import export_pdf
from sandbox.classification_knotoids.knotpy.notation import from_knotpy_notation


def test_simplify_thetas():
    # Take a minimal diagram, make random Reidemeister moves and simplify it to the original

    theta = kp.PlanarDiagram("+t3_1")

    for i in range(10):
        # make the diagram more complicated
        theta_mod = kp.randomize_diagram(theta, crossing_increasing_moves=1)

        # the Yamadas should be the same
        assert kp.yamada_polynomial(theta) == kp.yamada_polynomial(theta_mod)

        # simplify the modified theta curve
        theta_simplified = kp.simplify_smart(theta_mod, depth=1)

        # the canonical forms should be the same
        assert kp.canonical(theta) == kp.canonical(theta_simplified)


def test_reduce_thetas():

    theta1 = kp.PlanarDiagram("+t3_1")
    theta2 = kp.PlanarDiagram("t4_1.1")

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
    reduced = kp.reduce_equivalent_diagrams(list_of_thetas, depth=1)

    for key in reduced:
        print("The following diagrams are equivalent to", key)
        for value in reduced[key]:
            print("   ", value)
            # the yamada polynomials for each group is the same
            assert kp.yamada_polynomial(value) == kp.yamada_polynomial(key)

    # we expect the list to reduce to two different thetas
    assert len(reduced) == 2

if __name__ == '__main__':


    test_reduce_thetas()
    test_simplify_thetas()
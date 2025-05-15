from knotpy import yamada_polynomial, sanity_check
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.invariants.jones_polynomial import jones_polynomial
from knotpy.reidemeister.reidemeister import randomize_diagram
from knotpy.invariants._naive_yamada import _naive_yamada_polynomial


from knotpy import settings

def test_randomize_knot():
    """ Make random Reidemeister moves on a knot and check the Jones polynomial."""
    dump = settings.dump()
    settings.allowed_moves = "r1,r2,r3"

    k = PlanarDiagram("3_1")
    j = jones_polynomial(k)

    for i in range(10):
        k_ = randomize_diagram(k, crossing_increasing_moves=2)
        assert k != k_  # unlikely they are the same
        assert jones_polynomial(k_) == j

    settings.load(dump)

def test_randomize_theta():
    """ Make random Reidemeister moves on a theta curve and check the Yamada polynomial."""
    dump = settings.dump()
    settings.allowed_moves = "r1,r2,r3,r4,r5"
    thetas = [PlanarDiagram("t0_1"), PlanarDiagram("+t3_1"), PlanarDiagram("t4_1.1"), PlanarDiagram("h0_1"), PlanarDiagram("h2_1.1")]

    for theta in thetas:
        y = yamada_polynomial(theta)
        for i in range(20):
            theta_ = randomize_diagram(theta, crossing_increasing_moves=1)
            assert sanity_check(theta_)
            y_ = yamada_polynomial(theta_)
            n_ = _naive_yamada_polynomial(theta_)
            assert y_ == y == n_
    settings.load(dump)

def test_randomize_theta_direct():
    from knotpy.reidemeister import choose_reidemeister_1_add_kink, choose_reidemeister_1_remove_kink
    from knotpy.reidemeister import choose_reidemeister_2_unpoke, choose_reidemeister_2_poke
    from knotpy.reidemeister import choose_reidemeister_3_triangle, choose_reidemeister_4_slide, choose_reidemeister_5_twist, choose_reidemeister_5_untwist
    from knotpy.reidemeister import reidemeister_3, reidemeister_1_add_kink, reidemeister_2_poke, reidemeister_4_slide, reidemeister_5_twist, reidemeister_5_untwist, reidemeister_1_remove_kink, reidemeister_2_unpoke

    dump = settings.dump()
    settings.allowed_moves = "r1,r2,r3,r4,r5"

    thetas = [PlanarDiagram("t0_1"), PlanarDiagram("+t3_1"), PlanarDiagram("t4_1.1"), PlanarDiagram("h0_1"), PlanarDiagram("h2_1.1")]

    f = [(choose_reidemeister_3_triangle, reidemeister_3, "R3"),
         (choose_reidemeister_2_unpoke, reidemeister_2_unpoke, "R2 unpoke"),
         (choose_reidemeister_2_poke, reidemeister_2_poke, "R2 poke"),
         (choose_reidemeister_1_add_kink, reidemeister_1_add_kink, "R1 add"),
         (choose_reidemeister_1_remove_kink, reidemeister_1_remove_kink, "R1 remove"),
         (choose_reidemeister_5_untwist, reidemeister_5_untwist, "R5 untwist"),
         (choose_reidemeister_5_twist, reidemeister_5_twist, "R5 twist"),
         (choose_reidemeister_4_slide, reidemeister_4_slide, "R4 slide")
         ]

    for theta in thetas:
        y = yamada_polynomial(theta)
        k = theta.copy()
        for i in range(24):
            for c, r, name in f:
                if (location := c(k, random=True)) is not None:
                    q = r(k, location, inplace=False)
                    nyq = _naive_yamada_polynomial(q)
                    yq = yamada_polynomial(q)
                    assert nyq == yq, f"G\n{k}\n{name}{location}\n{q}\n{yq}\n{nyq}"
                    assert y == yq, f"\n{k}\n{name}{location}\n{q}\n{y}\n{yq}"

    settings.load(dump)

def test_randomize_theta_3_1_direct():
    from knotpy.reidemeister import choose_reidemeister_1_add_kink, choose_reidemeister_1_remove_kink
    from knotpy.reidemeister import choose_reidemeister_2_unpoke, choose_reidemeister_2_poke
    from knotpy.reidemeister import choose_reidemeister_3_triangle, choose_reidemeister_4_slide, choose_reidemeister_5_twist, choose_reidemeister_5_untwist
    from knotpy.reidemeister import reidemeister_3, reidemeister_1_add_kink, reidemeister_2_poke, reidemeister_4_slide, reidemeister_5_twist, reidemeister_5_untwist, reidemeister_1_remove_kink, reidemeister_2_unpoke

    f = [(choose_reidemeister_3_triangle, reidemeister_3, "R3"),
         (choose_reidemeister_2_unpoke, reidemeister_2_unpoke, "R2 unpoke"),
         (choose_reidemeister_2_poke, reidemeister_2_poke, "R2 poke"),
         (choose_reidemeister_1_add_kink, reidemeister_1_add_kink, "R1 add"),
         (choose_reidemeister_1_remove_kink, reidemeister_1_remove_kink, "R1 remove"),
         (choose_reidemeister_5_untwist, reidemeister_5_untwist, "R5 untwist"),
         (choose_reidemeister_5_twist, reidemeister_5_twist, "R5 twist"),
         (choose_reidemeister_4_slide, reidemeister_4_slide, "R4 slide")
         ]
    dump = settings.dump()
    settings.allowed_moves = "r1,r2,r3,r4,r5"

    theta = PlanarDiagram("+t3_1")
    y = yamada_polynomial(theta)
    assert sanity_check(theta)


    for i in range(3):
        for c, r, name in f:
            if (location := c(theta, random=True)) is not None:
                q = r(theta, location, inplace=False)
                assert sanity_check(q)
                yq = yamada_polynomial(q)
                nyq = _naive_yamada_polynomial(q)
                assert nyq == yq == y, f"G\n{theta}\n{name}{location}\n{q}\n{yq}\n{nyq}\n{y}"
    settings.load(dump)

if __name__ == '__main__':
    test_randomize_knot()
    test_randomize_theta()
    test_randomize_theta_direct()
    test_randomize_theta_3_1_direct()
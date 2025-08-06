import knotpy as kp
from knotpy import sanity_check
from knotpy.reidemeister.space import crossing_preserving_space

def test_r1():

    for knot in ["3_1", "4_1", "5_2"]:
        k = kp.orient(kp.PlanarDiagram(knot))
        assert kp.sanity_check(k)

        # make one r-move
        k_r1 = [kp.reidemeister_1_add_kink(k, loc) for loc in kp.find_reidemeister_1_add_kink(k)]
        assert all(kp.sanity_check(_) for _ in k_r1)
        # make two r-moves
        k_r1r1 = [kp.reidemeister_1_add_kink(_, loc) for _ in k_r1 for loc in kp.find_reidemeister_1_add_kink(_)]
        assert all(kp.sanity_check(_) for _ in k_r1r1)

        # undo the moves
        k_ = [kp.reidemeister_1_remove_kink(_, loc) for _ in k_r1 + k_r1r1 for loc in kp.find_reidemeister_1_remove_kink(_)]
        assert all(kp.sanity_check(_) for _ in k_)


def test_r2():

    for knot in ["3_1",  "5_2"]:
        k = kp.orient(kp.PlanarDiagram(knot))
        assert kp.sanity_check(k)

        # make one r-move
        k_r1 = [kp.reidemeister_2_poke(k, loc) for loc in kp.find_reidemeister_2_poke(k)]
        assert all(kp.sanity_check(_) for _ in k_r1)
        # make two r-moves
        k_r1r1 = [kp.reidemeister_2_poke(_, loc) for _ in k_r1 for loc in kp.find_reidemeister_2_poke(_)]
        assert all(kp.sanity_check(_) for _ in k_r1r1)

        # undo the moves
        k_ = [kp.reidemeister_2_unpoke(_, loc) for _ in k_r1 + k_r1r1 for loc in kp.find_reidemeister_2_unpoke(_)]
        assert all(kp.sanity_check(_) for _ in k_)

def test_r3():
    from knotpy.utils.set_utils import powerset
    from knotpy import mirror


    for knot in kp.knots((4,5)):#kp.knot_invariants((4, 5)):


        k = kp.orient(kp.PlanarDiagram(knot))
        assert kp.sanity_check(k)

        # crossings on 3-faces
        c3f = [face for face in k.faces if len(face) == 3]
        c3f = set(ep.node for f in c3f for ep in f)

        for csings in powerset(c3f):
            if len(csings) == len(c3f):
                continue
            k_ = mirror(k, csings, inplace=False)

            # make one r-move
            for location in kp.find_reidemeister_3_triangle(k_):
                #print(" IN:", k_)
                assert sanity_check(k_)
                #print(location)
                k_r3 = kp.reidemeister_3(k_, location)
                #print("OUT:", k_r3)
                assert sanity_check(k_r3)
            k_r3 = crossing_preserving_space(k_)
            if len(k_r3) > 1:
                print("*", len(k_r3), knot, csings)
                assert kp.sanity_check(k_r3)

if __name__ == "__main__":
    # test_r1()
    # test_r2()
    test_r3()
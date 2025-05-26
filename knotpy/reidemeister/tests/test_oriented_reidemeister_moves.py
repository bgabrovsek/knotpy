import knotpy as kp


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

    for knot in ["3_1", "4_1", "5_2"]:
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

    for knot in ["3_1", "4_1", "5_2"]:
        k = kp.orient(kp.PlanarDiagram(knot))
        assert kp.sanity_check(k)

        # make one r-move
        k_r3 = kp.reidemeister_3_space(k)
        assert kp.sanity_check(k_r3)

if __name__ == "__main__":
    test_r1()
    test_r2()
    test_r3()
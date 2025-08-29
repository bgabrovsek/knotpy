import knotpy as kp


def test_bracket():
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    for k in kp.knots((3,7)):
        p = kp.bracket(k)
        print(k.name)
        for kk in kp.all_reidemeister_moves(k, depth=1):
            pp = kp.bracket(kk)
            assert p == pp, f"{k.name} {p} {pp}"

def test_bracket_vs_homflypt():
    from knotpy.invariants.bracket import bracket_from_homflypt


    for k in kp.knots(range(0, 8), mirror=True, oriented=True):
        h = kp.homflypt(k, variables="xyz")
        b = kp.bracket(k)
        assert h is not None
        jb = bracket_from_homflypt(h)
        assert b == jb


def test_bracket_precomputed():


    for k in kp.knots(range(0, 8), mirror=True, oriented=False):
        kp.settings.use_precomputed_invariants = False
        h = kp.bracket(k)
        kp.settings.use_precomputed_invariants = True
        hp = kp.bracket(k)
        assert h == hp

    for k in kp.knots(range(0, 8), mirror=True, oriented=False):
        kp.settings.use_precomputed_invariants = False
        h = kp.bracket(k, normalize=False)
        kp.settings.use_precomputed_invariants = True
        hp = kp.bracket(k, normalize=False)
        assert h == hp


    for k in kp.knots(range(0, 8), mirror=True, oriented=True):
        kp.settings.use_precomputed_invariants = False
        k.framing = 7
        h = kp.bracket(k, normalize=False)
        kp.settings.use_precomputed_invariants = True
        hp = kp.bracket(k, normalize=False)
        assert h == hp


if __name__ == "__main__":
    #test_bracket()
    #test_bracket_vs_homflypt()
    test_bracket_precomputed()

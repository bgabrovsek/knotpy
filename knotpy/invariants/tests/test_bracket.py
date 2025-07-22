import knotpy as kp


def test_bracket():
    kp.settings.allowed_moves = "r1,r2,r3,flype"
    for k in kp.knots((3,7)):
        p = kp.bracket_polynomial(k)
        print(k.name)
        for kk in kp.all_reidemeister_moves(k, depth=1):
            pp = kp.bracket_polynomial(kk)
            assert p == pp, f"{k.name} {p} {pp}"


if __name__ == "__main__":
    test_bracket()
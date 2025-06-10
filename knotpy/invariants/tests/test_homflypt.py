import knotpy as kp
from knotpy import export_png, from_knotpy_notation


def test_homflypt():

    # problem: 13a_3436
    for knot, real_h in kp.knot_invariants(crossings=9,invariant="homflypt"):
        h = kp.homflypt_polynomial(knot)
        h_ = kp.homflypt_polynomial(kp.mirror(knot))

        if real_h == h or real_h == h_:
            #print(knot.name)
            pass
        else:
            print(knot.name, real_h, "     ", h, "     ", h_)
        assert real_h == h or real_h == h_, f"{knot.name} \n{real_h}\n{h}\n{h_}"


        #assert real_h == h

    pass

if __name__ == '__main__':
    import knotpy as kp
    test_homflypt()

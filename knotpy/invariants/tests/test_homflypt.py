import knotpy as kp
from knotpy import from_knotpy_notation
from time import time

def DO_NOT_test_homflypt():

    # problem: 13a_3436
    for knot, real_h in kp.knot_invariants(crossings=9,invariant="homflypt"):
        h = kp.homflypt(knot)
        h_ = kp.homflypt(kp.mirror(knot))

        if real_h == h or real_h == h_:
            print(knot.name)
            pass
        else:
            print(knot.name, real_h, "     ", h, "     ", h_)
        assert real_h == h or real_h == h_, f"{knot.name} \n{real_h}\n{h}\n{h_}"


        #assert real_h == h

    pass

def test_cache():

    k = kp.knot("8_4")

    t1 = time()

    h1 = kp.homflypt(k)

    t2 = time()

    h2 = kp.homflypt(k, variables="lm")

    t3 = time()

    h3 = kp.homflypt(k)

    t4 = time()

    print(t2 - t1, t3 - t2, t4 - t3)

    # assert (t2 - t1)  > (t3 - t2)
    # assert (t2 - t1)  > (t4 - t3)
    # assert h1 == h3



if __name__ == '__main__':
    import knotpy as kp
    #test_homflypt()

    test_cache()

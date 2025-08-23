from collections import OrderedDict

import knotpy as kp
def test():
    k = kp.knot("8_9")
    p = kp.homflypt(k.copy())
    for i in range(1000):
        kk = k.copy()
        p_ = kp.homflypt(kk)
        assert p == p_



if __name__ == "__main__":
    from time import time

    t =time()
    test()
    print(time() - t)

    # cache: 0.1963362693786621
    # no cache: 4.060028076171875

    #test_ordered_dict_simple()
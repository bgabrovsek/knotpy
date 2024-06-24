from pathlib import Path
from itertools import combinations, chain
from time import time
import knotpy as kp
from random import choice, randint



t = time()
DATA_FOLDER = Path("data")
path_knots_6 = DATA_FOLDER / "knots_pdcodes-2-6.gz"
path_knots_7 = DATA_FOLDER / "knots_pdcodes-7.gz"
path_knots_8 = DATA_FOLDER / "knots_pdcodes-8.gz"
path_knots_9 = DATA_FOLDER / "knots_pdcodes-9.gz"
path_knots_10 = DATA_FOLDER / "knots_pdcodes-10.gz"

knots = kp.load_collection(path_knots_6)
canonical_knots = [kp.canonical(k) for k in knots]

def make_random_reidemeister_move(k, r=None):

    f_choice = [
        kp.choose_reidemeister_1_kink,
        kp.choose_reidemeister_1_unkink,
        kp.choose_reidemeister_2_poke,
        kp.choose_reidemeister_2_unpoke,
        kp.choose_reidemeister_3_nonalternating_triangle
    ]

    f_make = [
        lambda k, eps: kp.reidemeister_1_add_kink(k, *eps),
        lambda k, ep: kp.reidemeister_1_remove_kink(k, ep),
        lambda k, eps: kp.reidemeister_2_poke(k, *eps),
        lambda k, face: kp.reidemeister_2_unpoke(k, face),
        lambda k, face: kp.reidemeister_3(k, face)
    ]

    s = ["R1 add kink", "R1 remove kink", "R2 poke", "R2 unpoke", "R3"]

    #print(k)
    if r is None:
        r = randint(0,4)
    #r=2
    result = f_choice[r](k, random=True)
    if result is not None:
        #print(s[r])
        f_make[r](k, result)
        #print("result", k)
        kp.sanity_check(k)


s = set(canonical_knots)
print(len(canonical_knots), len(s))
exit()

s = set()
for k in canonical_knots[:1000]:

    a = k.copy()
    b = k.copy()

    print(hash(k), hash(a), hash(b), k == a, k==b, a==b)

    continue

print(len(s))
exit()
    #
    # print(k)
    # minimal = kp.simplify(k, 6, "auto")
    # if minimal < k:
    #     print("Minimal: ", k)
    #
    # print()

count = 0
t = time()
for k in canonical_knots[:150]:

    print("hash", hash(k))
    continue

    count += 1


    poly = kp.kauffman_bracket_skein_module(k)[0]
    k_ = k.copy()

    print("reidemeister #", count, "(", k, ")")
    for i in range(8):
        make_random_reidemeister_move(k)
        poly2 = kp.kauffman_bracket_skein_module(k)[0]

        if poly != poly2:
            print("Knot 1:", k_)
            print("Knot 2:", k)
            print("Poly 1:", poly)
            print("Poly 2:", poly2)

            raise ValueError("Polies different", poly, "vs", poly2)

    #print(k)
    #print("reducing")
    kp.simplify_diagram_crossing_reducing(k)
    #print(k)
    poly3 = kp.kauffman_bracket_skein_module(k)[0]

    if poly != poly3:
        raise ValueError("polies...!!!", poly, poly3)

    print()

print()
print("Finished in time", time()-t)

"""
48
22
7
15

0.6
0.6
0.6


"""

# for k in canonical_knots[:10]:
#
#     print(k)
#     print("R1 kinks", list(kp.find_reidemeister_1_kinks(k)))
#     print("R1 unkinks", list(kp.find_reidemeister_1_unkinks(k)))
#     print("faces", list(k.faces))
#     print("R2 pokes", list(kp.find_reidemeister_2_pokes(k)))
#     print("R2 unpokes", list(kp.find_reidemeister_2_unpokes(k)))
#     print("R2 faces", list(kp.find_reidemeister_3_nonalternating_triangles(k)))
#     print()
#     continue


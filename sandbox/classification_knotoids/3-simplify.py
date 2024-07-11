from pathlib import Path
from tqdm import tqdm
from time import time
import os
import sympy
import matplotlib.pyplot as plt

import knotpy as kp

POLY_FOLDER = Path("polys")
FILTER_POLY_FOLDER = Path("filt-1")

def str2poly(s):
    """Convert a file name string into a polynomial."""
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(y, x)
    return sympy.sympify(s)

def poly2str(poly):
    """Convert polynomial into a filename-type string"""
    s = str(poly)
    for x, y in ["/d", "*x", "+p", "-m", " _", "(o", ")z"]:
        s = s.replace(x, y)
    return s

# print("Start")
#
# a = kp.from_pd_notation("X[0,1,2,3],X[4,5,6,7],X[1,0,4,8],X[2,8,7,6],V[3],V[5]")
# aa = kp.from_pd_notation("X[5,1,6,0],X[1,5,2,4],X[6,4,7,3],X[2,8,3,7],V[0],V[8]")
# b = kp.from_pd_notation("V[0],X[3,1,4,0],X[1,5,2,4],X[5,3,6,2],V[6]")
#
# print(a)
# print(aa)
# print(b)
#
#
# print(hash(a))
# print(hash(aa))
# print(hash(b))
# exit()
#
# pa, ga = kp.kauffman_bracket_skein_module(a)[0]
# paa, gaa = kp.kauffman_bracket_skein_module(aa)[0]
# pb, gb = kp.kauffman_bracket_skein_module(b)[0]
#
# print(pa, ga)
# print(paa, gaa)
# print(pb, gb)
#
# print()
# print()
# exit()

count_knotoids = 0
count_filtered_knotoids = 0

outer_counter = 0
for filename in os.listdir(POLY_FOLDER):  # load all knots with same polynomial

    if not filename.endswith(".gz"):
        continue

    outer_counter += 1

    # load the knotoids with same polynomial
    polynomial = str2poly(filename[:-3][filename.find("_")+1:])
    knots = kp.load_collection(POLY_FOLDER / filename)


    # put them into an equivalence relation
    er = kp.EquivalenceRelation([kp.canonical(k) for k in knots])
    original_number_of_classes = er.number_of_classes()
    count_knotoids += len(er)
    print()
    print("Poly:", polynomial)
    print("   Classes:", er.number_of_classes(), f"({len(knots)})","crossings from", min(len(k) for k in er), "to", max(len(k) for k in er))

    # for i, k in enumerate(er):
    #     print(f"*{i}", k)
    #     print(kp.to_pd_notation(k))
    #     print(kp.kauffman_bracket_skein_module(k))
    #     print(polynomial)
    # found = False
    # for i, k in enumerate(er):
    #     r3 = list(kp.find_reidemeister_3_triangles(k))
    #
    #     if len(r3) > 0:
    #
    #         print(r3[0])
    #         k_ = kp.reidemeister_3(k, r3[0], inplace=False)
    #         kp.algorithms.canonical_unoriented_details_temp(k_)
    #         k_ = kp.canonical(k_)
    #         print(f"-({i})", k_)
    #         print(kp.kauffman_bracket_skein_module(k_))
    #         found = True
    #
    # print()
    # continue



    counter = 0
    for counter, k in enumerate(er):

        k.name = f"Diagram {outer_counter}.{counter}"
        #print("  ", kp.canonical(k))




    for depth in [2, 5, 8, 11, 14]:

        if er.number_of_classes() == 1:
            continue

        for k in list(er):
            k_simplified = kp.simplify(k, depth=depth, method="nonincreasing")
            k_simplified = kp.canonical(k_simplified)
            #print("  *", k)
            # print("->", k_simplified)
            k_simplified.framing = 0

            er[k] = k_simplified



        #print("depth", depth, "number of classes", er.number_of_classes())
    #

    for depth in [1, 2, 5, 8]:

        if er.number_of_classes() == 1:
            continue

        for k in list(er):
            k_simplified = kp.simplify(k, depth=depth)
            k_simplified = kp.canonical(k_simplified)
            # print("  *", k)
            # print("->", k_simplified)
            k_simplified.framing = 0

            #print("****", k,"->", k_simplified)
            er[k] = k_simplified
    # print("..........."*3)
    # from itertools import combinations
    # repr = list(er.representatives())
    # for a, b in combinations(repr, 2):
    #     print(a==b, "   ", "\n",a, "\n",b)
    #     print(hash(a))
    #     print(hash(b))
    #     exit()


    count_filtered_knotoids += er.number_of_classes()

    print("Simplified:", er.number_of_classes(),"crossings from", min(len(k) for k in er.representatives()), "to",
          max(len(k) for k in er.representatives()))

    for k in er.representatives():
        print("  *", k)

        try:
            plt.close()
            kp.draw(k, with_title=True)
            plt.savefig("figures/" + k.name + ".png")
            plt.close()
        except:
            pass

    filename = poly2str(polynomial) + ".gz"  # convert the polynomial to a filename type string (no characters "*", "/", ...)
    filename = FILTER_POLY_FOLDER / filename
    kp.save_collection(filename, list(er.representatives()))

print("Simplified from ", count_knotoids,"to", count_filtered_knotoids)
    #exit()
    #print()


"""

      PlanarDiagram with 8 nodes, 13 arcs, and adjacencies a → V(b3), b → X(c0 d0 d3 a0), c → X(b0 e0 e3 f0), d → X(b1 g0 g3 b2), e → X(c1 h0 h3 c2), f → V(c3), g → X(d1 h2 h1 d2), h → X(e1 g2 g1 e2) with framing 0
      X[0,1,2,3],X[0,4,5,6],X[1,7,8,2],X[4,9,10,5],X[7,11,12,8],X[9,12,11,10],V[3],V[6]
      PlanarDiagram with 8 nodes, 13 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 d3), c → X(b1 e0 e3 b2), d → X(f0 g0 g3 b3), e → X(c1 h0 h3 c2), f → V(d0), g → X(d1 h2 h1 d2), h → X(e1 g2 g1 e2) with framing 0
      X[0,1,2,3],X[4,5,6,3],X[1,7,8,2],X[5,9,10,6],X[7,11,12,8],X[11,10,9,12],V[0],V[4]
      """

exit()
#
#
# if LOAD_KBSM_FROM_CSV:
#     t = time()
#     knots_kbsm = kp.load_invariant_collection(path_kauffman)
#     print(f"Loaded {len(knots_kbsm)} kbsm's in {round(time()-t, 2)}s" )
# else:
#     knots = kp.load_collection(DATA_FOLDER / filename_knots[6])
#     canonical_knots = [kp.canonical(k) for k in knots]
#
#     s = set(canonical_knots)
#     print(f"There are {len(s)} unique diagrams out of {len(canonical_knots)} diagrams.")
#
#     print("computing KBSM...")
#     knots_kbsm = dict()
#     for k in tqdm(canonical_knots):
#         knots_kbsm[k] = {"kbsm": str(kp.kauffman_bracket_skein_module(k)[0][0])}
#
#     kp.save_invariant_collection(path_kauffman, knots_kbsm)


print("Number of diagrams", len(knots_kbsm))
# splitting knots into groups
groups = kp.inverse_nested_dict(knots_kbsm)


print(f"There are {len(groups)} unique KBSM's and {sum([len(groups[inv]) == 1 for inv in groups])} unique (classified) diagrams.")

# equivalence classes
for g in groups:
    groups[g] = kp.EquivalenceRelation(groups[g])  # transform set into equivalence classes

for depth_step in range(3):
    depth = (depth_step + 1) * 3 - 1

    print()
    print(f"Simplification #{depth_step} at depth {depth}")
    number_classes = sum(groups[poly].number_of_classes() for poly in groups)
    number_elements = sum(len(groups[poly]) for poly in groups)
    number_of_polynomials = len(groups)
    print("Classes:", number_classes, "elements:", number_elements, "polys:", number_of_polynomials)

    # fist few groups
    few = [len(list(groups[poly].representatives())) for index, poly in enumerate(groups) if index < 20]
    print(few)

    for index, poly in enumerate(groups):
        ec = groups[poly]  # equivalence class
        diagrams = list(ec.representatives())
        #print(f"Group {index} of {len(groups)} with {len(diagrams)} diagrams and KBSM", poly)

        if len(diagrams) > 1:
            for k in diagrams:
                k_simplified = kp.simplify(k, depth=depth)
                k_simplified = kp.canonical(k_simplified)
                ec[k_simplified] = k

    number_classes = sum(groups[poly].number_of_classes() for poly in groups)
    number_elements = sum(len(groups[poly]) for poly in groups)
    number_of_polynomials = len(groups)
    print("Classes:", number_classes, "elements:", number_elements, "polys:", number_of_polynomials)

    # fist few groups
    few = [len(list(groups[poly].representatives())) for index, poly in enumerate(groups) if index < 20]
    print(few)


    #
    #
    #
    # for index, group in enumerate(groups):
    #     diagrams = groups[group]
    #
    #
    #     if len(diagrams) > 1:
    #         for k in diagrams:
    #             print("   ", k)
    #             #print(kp.to_pd_notation(k))
    #             k_s = kp.canonical(kp.simplify(k, depth=5))
    #             if k_s == k: text = "same"
    #             if k_s < k: text = "smaller"
    #             if k_s > k: text = "larger"
    #             print("-> ", text, k_s)
    #
    #
    #     count += 1
    #     if count >= 1:
    #         break

                #k_simpl = kp.simplify(k, 6)
                #print(k_simpl)
        # if len(diagrams) > 1:
        #     groups[group] = set(
        #         kp.simplify(k, 6, "auto") for k in groups[group]
        #     )


exit()

"""
PlanarDiagram with 2 nodes, 1 arcs, and adjacencies a → V(b0), b → V(a0) with framing 0 {' kbsm': 1}
PlanarDiagram with 4 nodes, 5 arcs, and adjacencies a → V(b1), b → X(c2 a0 c1 c0), c → X(b3 b2 b0 d0), d → V(c3) with framing 0 {' kbsm': -1/A**2 + A**(-6) + A**(-8)}
PlanarDiagram with 4 nodes, 5 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 c1), c → X(b1 b3 d0 b2), d → V(c2) with framing 0 {' kbsm': A**8 + A**6 - A**2}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 e0 d3 d2), d → X(b3 b2 c3 c2), e → V(c1) with framing 0 {' kbsm': -1/A**2 + A**(-6) + A**(-14)}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {' kbsm': A**14 + A**6 - A**2}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 d3 e0 d2), d → X(b3 b2 c3 c1), e → V(c2) with framing 0 {' kbsm': A**8 + A**6 - A**4 - A**2 + A**(-2)}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c1 d1 d0), c → X(d2 b1 d3 e0), d → X(b3 b2 c0 c2), e → V(c3) with framing 0 {' kbsm': A**14 + A**12 - A**8}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c3 d0 c0), c → X(b3 d2 d1 b1), d → X(b2 c2 c1 e0), e → V(d3) with framing 0 {' kbsm': -1/A**8 + A**(-12) + A**(-14)}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b1), b → X(c0 a0 c3 d0), c → X(b0 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {' kbsm': A**2 - 1/A**2 - 1/A**4 + A**(-6) + A**(-8)}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 e0 d3 d2), d → X(b3 b2 c3 c2), e → V(c1) with framing 0 {' kbsm': -1/A**2 + A**(-6) + A**(-14)}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {' kbsm': A**14 + A**6 - A**2}



PlanarDiagram with 2 nodes, 1 arcs, and adjacencies a → V(b0), b → V(a0) with framing 0 {'kbsm': '1'}
PlanarDiagram with 4 nodes, 5 arcs, and adjacencies a → V(b1), b → X(c2 a0 c1 c0), c → X(b3 b2 b0 d0), d → V(c3) with framing 0 {'kbsm': '-1/A**2 + A**(-6) + A**(-8)'}
PlanarDiagram with 4 nodes, 5 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 c1), c → X(b1 b3 d0 b2), d → V(c2) with framing 0 {'kbsm': 'A**8 + A**6 - A**2'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 e0 d3 d2), d → X(b3 b2 c3 c2), e → V(c1) with framing 0 {'kbsm': '-1/A**2 + A**(-6) + A**(-14)'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {'kbsm': 'A**14 + A**6 - A**2'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 d3 e0 d2), d → X(b3 b2 c3 c1), e → V(c2) with framing 0 {'kbsm': 'A**8 + A**6 - A**4 - A**2 + A**(-2)'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c1 d1 d0), c → X(d2 b1 d3 e0), d → X(b3 b2 c0 c2), e → V(c3) with framing 0 {'kbsm': 'A**14 + A**12 - A**8'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c3 d0 c0), c → X(b3 d2 d1 b1), d → X(b2 c2 c1 e0), e → V(d3) with framing 0 {'kbsm': '-1/A**8 + A**(-12) + A**(-14)'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b1), b → X(c0 a0 c3 d0), c → X(b0 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {'kbsm': 'A**2 - 1/A**2 - 1/A**4 + A**(-6) + A**(-8)'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 d1 d0), c → X(b1 e0 d3 d2), d → X(b3 b2 c3 c2), e → V(c1) with framing 0 {'kbsm': '-1/A**2 + A**(-6) + A**(-14)'}
PlanarDiagram with 5 nodes, 7 arcs, and adjacencies a → V(b0), b → X(a0 c0 c3 d0), c → X(b1 d2 d1 b2), d → X(b3 c2 c1 e0), e → V(d3) with framing 0 {'kbsm': 'A**14 + A**6 - A**2'}
"""

# kbsm_k = {
#     k: {"KBSM": poly_to_tuple(kp.kauffman_bracket_skein_module(k)[0][0], sympy.symbols('A'))}
#     for k in canonical_knots
# }


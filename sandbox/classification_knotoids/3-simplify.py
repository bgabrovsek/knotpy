from pathlib import Path
from tqdm import tqdm
from time import time
import os
import sympy

import knotpy as kp

POLY_FOLDER = Path("polynomials")


print("X[0,1,2,3],X[4,5,6,7],X[1,8,9,2],X[10,11,12,4],X[13,6,5,14],X[15,9,8,11],X[15,10,16,0],X[16,13,14,12],V[3],V[7]")
print("X[0,1,2,3],X[4,5,6,7],X[1,8,9,2],X[10,11,4,12],X[12,6,5,13],X[14,10,13,15],X[16,9,8,15],X[16,11,14,0],V[3],V[7]")


k1 = kp.from_pd_notation("X[0,1,2,3],X[4,5,6,7],X[1,8,9,2],X[10,11,12,4],X[13,6,5,14],X[15,9,8,11],X[15,10,16,0],X[16,13,14,12],V[3],V[7]")
k2 = kp.from_pd_notation("X[0,1,2,3],X[4,5,6,7],X[1,8,9,2],X[10,11,4,12],X[12,6,5,13],X[14,10,13,15],X[16,9,8,15],X[16,11,14,0],V[3],V[7]")
print(k1)
print(k2)




c1 = kp.canonical(k1)
c2 = kp.canonical(k2)

print(k1 < k2, k2 < k1)


print(c1)
print(c2)

print("---")
kp.simplify(c2, 1, "non-increasing",)

exit()
def str2poly(s):
    d = ["/d", "*x", "+p", "-m", " s", "(o", ")z"]
    for x, y in d:
        s = s.replace(y, x)
    return sympy.sympify(s)

for filename in os.listdir(POLY_FOLDER):
    if not filename.endswith(".gz"): continue

    #if not filename.startswith("7_"): continue
    #print(filename)
    polynomial = str2poly(filename[:-3][filename.find("_")+1:])

    knots = kp.load_collection(POLY_FOLDER / filename)
    print("Polynomial", polynomial, f"({len(knots)} knots)")

    er = kp.EquivalenceRelation(knots)

    print("Classes:", er.number_of_classes(), end=" ", flush=True)

    for depth in [2]:#[2, 5, 8, 11, 17]:

        new_dict = dict()

        for k in er:
            #print(k)
            k_simplified = kp.simplify(k, depth=depth, method="nonincreasing")
            k_simplified = kp.canonical(k_simplified)
            #print("simpl", k_simplified)
            new_dict[k_simplified] = k

        for a, b in new_dict.items():
            er[a] = b

        noc = er.number_of_classes()
        print(noc, end=" ", flush=True)
    print()



    break


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


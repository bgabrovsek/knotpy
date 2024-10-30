"""Load knotoids from files and split them by their invariant (normalized Kauffman bracket).
For each polynomial, store the knotoids into a file (with the name of that polynomial)
"""
from pathlib import Path

import sympy
from tqdm import tqdm
from time import time
from collections import defaultdict

import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
#from classification import loop_diagrams_file, print_invariant_dict_stats, line_count, ClassificationFile

DATA_FOLDER = Path("data")
input_knotoids = DATA_FOLDER / "knotoids_pd_codes.txt"  # save PD codes of knotoids
output = DATA_FOLDER / "knotoids-filter-0.txt"  # save PD codes of knotoids


def is_mirror(poly):
    # return True if poly is the smaller of the two mirror polynomials
    def zlp(poly):
        # zip laurent poly
        return tuple(zip(*[(e, c) for c, e in kp.laurent_polynomial_to_tuples(poly, "A")]))
    return zlp(poly) < zlp(kp.reciprocal(poly, "A"))


def print_invariant_dict_stats(data):
    from collections import defaultdict
    print("There are", len(data), "polynomials with", sum(len(val) for val in data.values()), "diagrams - ", end="")
    poly_group_sizes = defaultdict(int)
    for p in data:
        poly_group_sizes[len(data[p])] += 1
    print("Group sizes (count):", ", ".join(f"{l}({poly_group_sizes[l]})" for l in sorted(poly_group_sizes)))



if __name__ == "__main__":

    comment = f"Knotoids up to 6 crossings without mirrors // 7.8.2024"

    invariant_names = ("Kauffman bracket", "Affine index polynomial", "Arrow polynomial", "Mock Alexander polynomial")
    invariant_functions = (lambda q: kp.kauffman_bracket_skein_module(q, normalize=True)[0][0],
                           kp.affine_index_polynomial,
                           kp.arrow_polynomial,
                           kp.mock_alexander_polynomial)

    knotoids = defaultdict(set)  # store invariants (Kauffman bracket polynomials)
    no_ignored = 0

    for k in kp.Bar(kp.load_collection_iterator(input_knotoids), total=kp.count_lines(input_knotoids), comment="invariants"):

        k_invariants = tuple(f(k) for f in invariant_functions)

        # ignore knotoid if Kauffman says it is a mirror
        if is_mirror(k_invariants[0]):
            no_ignored += 1
            continue

        k = kp.canonical(k)
        knotoids[k_invariants].add(k)

    print_invariant_dict_stats(knotoids)

    kp.save_collection_with_invariants(output, knotoids, invariant_names=invariant_names, comment=comment)

    print(f"Ignored {no_ignored} knotoids")


    print("Verifying output")
    count = 10
    for q in kp.load_collection_with_invariants_iterator(output):
        diagrams, invariants = q
        print("Diagrams:")
        for d in diagrams:
            print("  ", d)
        print("Invariants:")
        for key, value in invariants.items():
            print("  ", key, value)

        count -= 1
        if count <= 0:
            break

        print()
    #
    # cf = ClassificationFile(output, comment, invariants=invariant_names, notation_function=kp.to_condensed_pd_notation)
    # cf.write_dict(knotoids)
    # print("Wrote", line_count(output), "lines to", output)

exit()

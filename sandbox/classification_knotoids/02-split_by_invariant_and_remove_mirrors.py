"""Load knotoids from files and split them by their invariant (normalized Kauffman bracket).
For each polynomial, store the knotoids into a file (with the name of that polynomial)
"""
from pathlib import Path

import knotpy as kp

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "knotoids_pd_codes.txt"  # save PD codes of knotoids
output = DATA_FOLDER / "knotoids-0-split-no-mirrors.txt"  # save PD codes of knotoids
output_classified = DATA_FOLDER / "knotoids-0-classified.txt"  # save PD codes of knotoids


def is_mirror(poly):
    # return True if poly is the smaller of the two mirror polynomials
    def zlp(poly):
        # zip laurent poly
        return tuple(zip(*[(e, c) for c, e in kp.laurent_polynomial_to_tuples(poly, "A")]))
    return zlp(poly) < zlp(kp.reciprocal(poly, "A"))

if __name__ == "__main__":

    comment = f"Knotoids up to 7 crossings without mirrors"

    invariants = {
        "Kauffman bracket": lambda q: kp.kauffman_bracket_skein_module(q, normalize=True)[0][0],
        "Affine index polynomial": kp.affine_index_polynomial,
        "Arrow polynomial": kp.arrow_polynomial,
        "Mock Alexander polynomial": kp.mock_alexander_polynomial
    }

    knotoids = kp.load_diagrams(input)
    inv_dict = kp.InvariantDict(invariants)

    count_removed_mirror = 0
    count_removed_disjoint = 0
    for k in kp.Bar(knotoids, comment="Computing invariants"):
        if is_mirror(kp.kauffman_bracket_skein_module(k, normalize=True)[0][0]):
            count_removed_mirror += 1
            continue
        if kp.is_disjoint_sum(k):
            count_removed_mirror += 1
            continue

        inv_dict.append(k)



    knotoids_unique = []
    knotoids_non_unique = []

    for knotoid_group in inv_dict.values():
        if len(knotoid_group) == 1:
            knotoids_unique.append(knotoid_group.pop())
        else:
            knotoids_non_unique.append(knotoid_group)

    kp.save_diagram_sets(output, knotoids_non_unique)
    kp.save_diagrams(output_classified, knotoids_unique)

    kp.charts.print_bar_chart(inv_dict.stats())

    print("Removed", count_removed_mirror, "diagrams (mirrors)")
    print("Removed", count_removed_disjoint, "diagrams (disjoint sums)")


exit()

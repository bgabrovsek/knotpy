"""
Convert PD codes of graphs to PD and native KP/EM codes of knotoids.
Remove knotoids that allow an unpoke R2 move.
Remove knotoids with more than 1 component (linkoids)
Put knotoids into canonical form and save them into gzipped files.
"""
from datetime import datetime
from pathlib import Path

import sys

import knotpy as kp

DATA_FOLDER = Path("data")
input = DATA_FOLDER / "graphs_pdcodes.txt"  # get PD codes of planar graphs
output = DATA_FOLDER / "knotoids_pd_codes.txt"  # save PD codes of knotoids
comment = "Knotoids up to 7 crossings from graphs with all possible crossing combinations"

MAX_NUMBER_OF_CROSSINGS = 6

def is_mirror(poly):
    # return True if poly is the smaller of the two mirror polynomials
    def zlp(poly):
        # zip laurent poly
        return tuple(zip(*[(e, c) for c, e in kp.laurent_polynomial_to_tuples(poly, "A")]))
    return zlp(poly) < zlp(kp.reciprocal(poly, "A"))



if __name__ == "__main__":


    graphs = kp.load_diagrams(input, "pd")

    print(f"Loaded {len(graphs)} graphs having {min(len(g) for g in graphs)-2} to {max(len(g) for g in graphs)-2} crossings")

    file_comment = f"All knotoids up to {MAX_NUMBER_OF_CROSSINGS} crossings // 4.3.2025"

    graphs = [g for g in graphs if len(g) - 2 <= MAX_NUMBER_OF_CROSSINGS]
    kp.charts.print_bar_chart({i:len([g for g in graphs if len(g)-2 == i]) for i in range(9)})

    print(f"Up to 8 crossings: {len(graphs)}")

    canonical_graphs = {kp.canonical(g) for g in graphs}
    canonical_graphs = sorted(canonical_graphs)
    print(f"Canonical graphs:  {len(graphs)}")

    count_knotoids = 0


    with kp.DiagramWriter(output, notation="cem", comment=f"{comment} - {datetime.now().isoformat()}") as writer:
        for g in kp.Bar(canonical_graphs, comment="Graphs to knots"):

            # get all possible knotoids by changing signs
            knotoids = kp.vertices_to_crossings(g, all_crossing_signs=True)

            # remove obvious non-minimal diagrams
            knotoids = [k for k in knotoids if kp.choose_reidemeister_2_unpoke(k) is None]  # keep if no unpoke
            knotoids = {kp.canonical(k) for k in knotoids}

            writer.write_diagrams(knotoids)

            count_knotoids += len(knotoids)

print(f"Wrote {count_knotoids} knotoids to {output}")
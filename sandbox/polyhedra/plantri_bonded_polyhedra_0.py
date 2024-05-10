"""
Reads all polyhedra (>= 4 nodes) obtained by the Plantri (called by "plantri -m3c2 -a ???)",
and splits the polyhedra into classes (good polyhedra, connected sum, and 3rd order connected sum).
"""
from pathlib import Path
from collections import Counter, defaultdict

import sys

sys.path.append('../..')  # Add the directory to the search path

import knotpy as kp

data_dir = Path("./data")
fig_dir = Path("./figs")

for n in range(3, 13):
    print("=================================")
    print(f"Processing graphs with {n} nodes.")

    poly, poly_sum, poly_third, poly_other = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)

    # load the data iteratively
    for count, g in enumerate(kp.loadtxt_iterator(data_dir / "0-plantri" / f"plantri-{n}.txt",
                                                  notation="plantri",
                                                  ccw=False)):

        if count % 100000 == 0: print(count, end=" ", flush=True)
        c = Counter(ds := kp.degree_sequence(g))
        if set(c) == {3, 4} and c[3] % 2 == 0:
            b = c[3] // 2  # number of bonds
            if kp.is_connected_sum(g):
                poly_sum[b].append(g)
            elif kp.is_connected_sum_third_order(g):
                poly_third[b].append(g)
            else:
                poly[b].append(g)
        else:
            if n <= 8:
                poly_other[ds].append(g)

    print("\nWriting...")
    # write
    for knots, filename, description in [
        (poly, "poly", "polyhedral graph(s)"),
        (poly_sum, "sum", "polyhedral graph(s) that are connected sums"),
        (poly_third, "third", "polyhedral graph(s) that are 3rd-degree sums"),
        (poly_other, "other", "other polyhedral graph(s)")
    ]:
        print("  saving", filename, "...", end=" ", flush=True)
        for i, b in enumerate(sorted(knots)):
            if i < 6:
                print(b, end=" ", flush=True)
            comment = (f"# {len(knots)} {description} with {n} nodes ({n - 2 * b} vertices) and {b} bond(s)" ) \
                if isinstance(b, int) else str(b)
            sb = str(b).replace(", ","")
            kp.savetxt_multiple_obsolete(knots[b],
                                         data_dir / ("1-" + filename) / f"{filename}-{n}-{sb}.txt",
                                         notation="plantri",
                                         ccw=False,
                                         separator=",",
                                         comment=comment)
        print("\n  exporting", filename,end=" ... ", flush=True)
        for i, b in enumerate(sorted(knots)):
            all_graphs = knots[b][:80]
            if i < 6:
               print(b,end=" ", flush=True)
            for i, g in enumerate(all_graphs):
                c4 = sum(1 for v in g.nodes if len(g.nodes[v]) == 4)
                c3 = sum(1 for v in g.nodes if len(g.nodes[v]) == 3)
                g.name = f"{c4} crossings + {c3} nodes (#{i})"
                for v in g.nodes:
                    if g.nodes[v].degree == 3:
                        g.nodes[v]["color"] = "brown"

            #kp.export_pdf(all_graphs, fig_dir / f"{filename}-{n}-{b}.pdf")
        print()
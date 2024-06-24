
import knotpy as kp
from knotpy import is_connected_sum, is_connected_sum_third_order, export_pdf
from pathlib import Path


data_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/sandbox/polyhedra/data")
fig_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/sandbox/polyhedra/figs")

for name in ["poly"]:#, "sum", "third"]:
    for B, N, nm in [([0, 1, 2, 3, 4, 5, 6], [4, 5, 6, 7, 8, 9], "9"),
                  ([0, 1, 2, 3, 4, 5, 6], [10], "10"),
                ([0, 1, 2, 3, 4, 5, 6], [11], "11"),
                 ([0, 1, 2, 3, 4, 5, 6], [12], "12")
            ]:
        for b in B:
            graphs = []
            print(name, "bonds", b, "nodes", N)
            for n in N:
                graphs += kp.loadtxt_multiple(data_dir / (name + f"-{n}-{b}.txt"), notation="plantri", prepended_node_count=False)


            canon = {kp.canonical_unoriented(g) for g in graphs}
            print("  count =", len(graphs), "=", len(canon))


            for i, g in enumerate(graphs):
                g.name = f"Graph {i} ({len(g)} nodes)"
                for v in g.nodes:
                    if g.degree(v) == 3:
                        g.nodes[v]["color"] = "brown"

            if len(graphs) > 0:
                print("exporting", len(graphs), "graphs")
                export_pdf(graphs, fig_dir / f"{name}-{nm}-{b}.pdf")


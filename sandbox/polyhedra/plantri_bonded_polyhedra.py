import knotpy as kp
from pathlib import Path

data_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/sandbox/polyhedra/data")

N = 12  # max nodes

for n in range(4, N+1):
    print(n, "nodes", end=" ", flush=True)
    graphs = kp.loadtxt(data_dir / f"plantri-{n}.txt", notation="pl", prepended_node_count=True, ccw=False)

    if not isinstance(graphs, list):
        graphs = [graphs]

    print(f"({len(graphs)} polyhedra)")

    for bonds in range(0, n//2 + 1):
        deg_seq = [3] * (2 * bonds) + [4] * (n - 2 * bonds)
        bonded_knots = [g for g in graphs if g.degree_sequence() == deg_seq]
        print("   ", len(bonded_knots), "polyhedra with", bonds, "bonds")

        kp.savetxt(bonded_knots,
                   data_dir / f"polyhedra-{n}-{bonds}.txt",
                   notation="plantri",
                   ccw=False,
                   separator=",",
                   prepended_node_count=True,
                   comment=f"# {len(bonded_knots)} " + ("graph" if len(bonded_knots) == 1 else "graphs")
                   )


    print("---")


"""
Obtains all polyhedra (>= 4 nodes) obtained by the plantri application, called by "plantri -m3c2 -a ???".
"""
import sys
sys.path.append('../..')

import knotpy as kp
from knotpy import is_connected_sum, is_connected_sum_third_order, export_pdf
from pathlib import Path

data_dir = Path("/Users/bostjan/Dropbox/Code/knotpy/sandbox/polyhedra/data")

N = 12  # max nodes

for n in range(4, N+1):

    print(f"Number of nodes = {n}")


    # generate lists and degree sequences

    poly, poly2, poly3, deg_seq = dict(), dict(), dict(), dict()  # polyhedra, connected sums, connected sums 3rd order
    for b in range(0, n // 2 + 1):
        poly[b], poly2[b], poly3[b] = [], [], []
        deg_seq[b] = [3] * (2 * b) + [4] * (n - 2 * b)

    # load the data iteratively

    for g in kp.loadtxt_iterator(data_dir / f"plantri-{n}.txt", notation="pl", prepended_node_count=True, ccw=False):
        for b in deg_seq:
            if kp.degree_sequence(g) == deg_seq[b]:
                if is_connected_sum(g):
                    poly2[b].append(g)
                elif is_connected_sum_third_order(g):
                    poly3[b].append(g)
                else:
                    poly[b].append(g)

    # write
    for b in deg_seq:
        for o, fn, com in [
            (poly[b], "poly", "polyhedral graph(s)"),
            (poly2[b], "sum", "polyhedral graph(s) that are connected sums"),
            (poly3[b], "third", "polyhedral graph(s) that are 3rd-degree sums")]:
            kp.savetxt_multiple(o,
                                data_dir / f"{fn}-{n}-{b}.txt",
                                notation="plantri", ccw=False, separator=",", prepended_node_count=False,
                                comment=f"# {len(o)} {com} with {n} nodes ({n - 2 * b} vertices) and {b} bond(s)")




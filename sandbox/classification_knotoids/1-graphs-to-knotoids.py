"""
Convert PD codes of graphs to PD and native KP/EM codes of knotoids.
Remove knotoids that allow an unpoke R2 move.
Remove knotoids with more than 1 component (linkoids)
Put knotoids into canonical form and save them into gzipped files.
"""

from pathlib import Path
from itertools import combinations, chain
from tqdm import tqdm

import knotpy as kp

DATA_FOLDER = Path("data")
path_graphs = DATA_FOLDER / "graphs_pdcodes.txt"
path_knotoids_pd = DATA_FOLDER / "knotoids_pd_codes.gz"
path_knotoids_kp = DATA_FOLDER / "knotoids_native_codes.gz"

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def all_crossing_sign_combinations(k):
    list_of_knots = []
    for crossings in powerset(k.crossings):
        new_k = k.copy()
        kp.mirror(new_k, crossings=crossings)
        list_of_knots.append(new_k)
    return list_of_knots

def _fai(filename: str, n:int):
    """ File Append Integer: convert example.txt to example-n.txt"""
    return filename[:filename.rfind(".")] + f"-{n}" + filename[filename.rfind("."):]

graphs = {n: list() for n in range(11)}  # graphs with n crossings and 2 terminals

# load all graphs from pd codes
with open(path_graphs) as file:
    for line in file:
        g = kp.from_pd_notation(line.rstrip())
        graphs[g.number_of_nodes - 2].append(g)


# print number of graphs for a given number of crossings
print("Number of graphs:", {n: len(graphs[n]) for n in graphs})

# convert graphs to knotoids by changing all possible crossing signs
knotoids_pd = list()  # PD codes of knotoids
knotoids_kp = list()  # KnotPy codes of knotoids
count_all_knotoids = 0  # count theoretical number of knotoids

for n in range(0, 11):  # number of crossings

    #print(f"Mirroring crossings of knots with {n} crossings ({len(graphs[n])})")

    print()
    for g in tqdm(graphs[n], desc=f"{n} crossings"):

        # ignore if we have a linkoid
        if kp.number_of_link_components(g) > 1:
            count_all_knotoids += n ** 2  # add to theoretical counter
            continue

        new_knotoids = all_crossing_sign_combinations(g)  # all candidates single crossing "mutations"
        count_all_knotoids += len(new_knotoids)

        # keep only knots with no R2 unpoke move
        new_knotoids = [k for k in new_knotoids if kp.choose_reidemeister_2_unpoke(k) is None]

        # put the knots into canonical form
        new_knotoids = [kp.canonical(k) for k in new_knotoids]

        # store only the codes to save memory (codes take up less memory than the actual instance)
        knotoids_kp.extend([kp.to_knotpy_notation(k) for k in new_knotoids])  # convert to pd so save memory
        knotoids_pd.extend([kp.to_pd_notation(k) for k in new_knotoids])  # convert to pd so save memory

    print(f"{len(graphs[n])} graphs converted to {count_all_knotoids} knots with {len(knotoids_pd)} good ones.")

    # save the knotoids (group knotoids with 6 or fewer crossings into one file)
    if n >= 6:

        kp.save_collection(_fai(str(path_knotoids_pd), n), iterable=knotoids_pd, notation="pd")
        print(f"{len(knotoids_pd)} knots saved to files {_fai(str(path_knotoids_pd), n)}", end=" and ")

        kp.save_collection(_fai(str(path_knotoids_kp), n), iterable=knotoids_kp, notation="knotpy")
        print(f"{_fai(str(path_knotoids_kp), n)}.")

        # clear tables, since they are now saved
        knotoids_pd = []
        knotoids_kp = []
        count_all_knotoids = 0

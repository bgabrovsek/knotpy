"""
Convert PD codes of graphs to PD and native KP/EM codes of knotoids.
Remove knotoids that allow an unpoke R2 move.
Remove knotoids with more than 1 component (linkoids)
Put knotoids into canonical form and save them into gzipped files.
"""
import multiprocessing
from pathlib import Path
from itertools import combinations, chain
from tqdm import tqdm

import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp


DATA_FOLDER = Path("data")
input_graphs = DATA_FOLDER / "graphs_pdcodes.txt"  # get PD codes of planar graphs
output_knotoids = DATA_FOLDER / "knotoids_pd_codes.txt"  # save PD codes of knotoids

MAX_NUMBER_OF_CROSSINGS = 8

def powerset(iterable):
    """Return the powerset of an iterable, e.g., for [1,2,3], obtain () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def all_crossing_sign_combinations(k):
    """For a given knotoid, generate all knotoids with all possible signs for crossings, +++, ++-, ...
    :param k:
    :return:
    """
    list_of_knots = []
    for crossings in powerset(k.crossings):
        new_k = k.copy()
        kp.mirror(new_k, crossings=crossings, inplace=True)
        list_of_knots.append(new_k)
    return list_of_knots




if __name__ == "__main__":

    comment = f"All knotoids up to {MAX_NUMBER_OF_CROSSINGS} crossings // 7.8.2024"

    # load all graphs from pd codes
    graphs = kp.load_headerless_collection(input_graphs, "pd")
    print(f"Loaded {len(graphs)} graphs from {min(len(g) for g in graphs)-2} to {max(len(g) for g in graphs)-2} crossings")
    print(graphs[0], "...")

    count_all_knotoids = 0  # count theoretical number of knotoids
    count_output_knotoids = 0  # count theoretical number of knotoids
    knotoids_pd = []

    # create new collection
    kp.init_collection(output_knotoids, comment=comment)

    all_graphs = len(graphs)
    canonical_graphs = set()
    number_of_potential_graphs = 0
    for g in kp.Bar(graphs, comment="canonical"):
        no_crossings = len(g) - 2  # nuber of crossings

        # ignore if we have too many crossings
        if no_crossings > MAX_NUMBER_OF_CROSSINGS:
            continue

        g = kp.canonical(g)
        number_of_potential_graphs += 1
        canonical_graphs.add(g)

    print(f"Using {len(canonical_graphs)} out of {number_of_potential_graphs} ({len(graphs)}) graphs.")

    for g in kp.Bar(canonical_graphs, comment="graphs"):



        count_all_knotoids += no_crossings ** 2

        # ignore if we have a linkoid
        if kp.number_of_link_components(g) > 1:
            continue

        new_knotoids = all_crossing_sign_combinations(g)  # all candidates single crossing "mutations"
        new_knotoids = [k for k in new_knotoids if kp.choose_reidemeister_2_unpoke(k) is None] # keep if no unpoke
        new_knotoids = {kp.canonical(k) for k in new_knotoids}  # keep only knots with no R2 unpoke move

        kp.extend_collection(output_knotoids, new_knotoids)

        count_output_knotoids += len(new_knotoids)


    print(f"Written {count_output_knotoids} out of {count_all_knotoids} knotoids.")
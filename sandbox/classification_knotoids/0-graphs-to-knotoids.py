from pathlib import Path
from itertools import combinations, chain

import knotpy as kp

DATA_FOLDER = Path("data")
path_graphs = DATA_FOLDER / "graphs_pdcodes.txt"
path_knots = DATA_FOLDER / "knots_pdcodes.gz"

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



graphs = {n: list() for n in range(11)}  # graphs with n crossings and 2 terminals

# load all graphs from pd codes
with open(path_graphs) as file:
    for line in file:
        line = line.rstrip()
        print("Line", line)
        g = kp.from_pd_notation(line)
        graphs[g.number_of_nodes - 2].append(g)


# print number of graphs for a given number of crossings
print("Number of graphs:", {n: len(graphs[n]) for n in graphs})

# convert graphs to knots by changing all possible crossing signs
knots = {n: list() for n in range(0, 11)}
count_all_knots = {n: 0 for n in range(0, 11)}
for n in range(0, 11):
    print(f"Mirroring crossings of knots with {n} crossings ({len(graphs[n])})", end="")
    for g in graphs[n]:
        if kp.number_of_link_components(g) > 1:
            count_all_knots[n] += n**2
            continue

        candidates = all_crossing_sign_combinations(g)  # all candidates single crossing "mutations"
        count_all_knots[n] += len(candidates)  # count all
        good_candidates = [k for k in candidates if kp.choose_reidemeister_2_unpoke(k) is None]  # select knots with no unpoke
        knots[n].extend([kp.to_pd_notation(k) for k in good_candidates])  # convert to pd so save memory

    print(f" ({len(graphs[n])} graphs converted to {count_all_knots[n]} knots with {len(knots[n])} good ones).")

    if n >= 6:
        filename = str(path_knots)
        # replace extension with "-{number of crossings}.extension"
        if n == 6:
            filename = filename[:filename.rfind(".")] + "-2-6" + filename[filename.rfind("."):]
            #new_path = str(path_knots).replace(".txt", "-3-8.txt")
        else:
            filename = filename[:filename.rfind(".")] + f"-{n}" + filename[filename.rfind("."):]

        kp.save_collection(filename, iterable=chain(*knots.values()), notation="pd")
        print(f"{sum(len(v) for v in knots.values())} knots saved to file {filename}.")
        knots = {n: list() for n in range(2, 11)}

#print("Number of knots:", {n: len(knots[n]) for n in knots})

# L = kp.load_collection(path_knots)
# print(len(L))

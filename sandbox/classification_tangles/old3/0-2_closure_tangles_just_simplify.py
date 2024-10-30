import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
import multiprocessing
from knotpy.utils.multiprogressbar import Bar
import math
import zipfile
from time import time
import os
import string


def safe_delete_file(s):
    if os.path.exists(s):
        os.remove(s)
        print("File", s, "has been deleted")

#global_diagrams = list()

def knot2str(k):
    if any(len(k._nodes[x]._inc) != 4 for x in sorted(k._nodes)):
        return "?"
    #turn a knot into
    return "".join(k._nodes[x][0].node + str(k._nodes[x][0].position) +
                   k._nodes[x][1].node + str(k._nodes[x][1].position) +
                   k._nodes[x][2].node + str(k._nodes[x][2].position) +
                   k._nodes[x][3].node + str(k._nodes[x][3].position) for x in sorted(k._nodes))


def knot2str_advanced(k:kp.PlanarDiagram):

    k = kp.canonical(k)

    if len(k) == 1 and all(k.degree(node) == 2 for node in k.nodes):
        return "unknot"


    if kp.is_disjoint_sum(k):
        components = kp.disjoint_components(k)
        return " U ".join([knot2str_advanced(c) for c in components])

    if kp.is_connected_sum(k):
        components = kp.to_connected_sum(k)
        return " # ".join([knot2str_advanced(c) for c in components])


    if any(len(k._nodes[x]._inc) != 4 for x in sorted(k._nodes)):
        raise ValueError("!", k)


    #turn a knot into
    return "".join(k._nodes[x][0].node + str(k._nodes[x][0].position) +
                   k._nodes[x][1].node + str(k._nodes[x][1].position) +
                   k._nodes[x][2].node + str(k._nodes[x][2].position) +
                   k._nodes[x][3].node + str(k._nodes[x][3].position) for x in sorted(k._nodes))


def innner_classify(k):

    if len(k) == 1:
        return "unknot"

    code = knot2str(k)

    if code in known:
        return known[code] #shared_diagrams[shared_diagrams.index(k)].name

    if kp.is_disjoint_sum(k):
        components = kp.disjoint_components(k)
        return " U ".join([classify(c)[0] for c in components])

    if kp.is_connected_sum(k):
        components = kp.to_connected_sum(k)
        return " # ".join([classify(c)[0] for c in components])

    if len(k) > 11 and kp.number_of_link_components(k) > 1:
        return "link"

    return "unknown"


def describe_unknown(k):
    if kp.is_disjoint_sum(k):
        return "unknown composite"
    if kp.is_connected_sum(k):
        return "unknown connected sum"
    if (nlk := kp.number_of_link_components(k)) > 1:
        return f"unknown {len(k)} crossing link with {nlk} components"
    else:
        return f"unknown {len(k)} crossing knot"

def make_simple(k):
    kk = kp.simplify_smart(k, depth=0)
    #return knot2str_advanced(kp.canonical(kp.simplify_crossing_reducing(k)))
    return knot2str_advanced(kk)


def classify(k):
    """ try to classify unsimplified knot k"""
    depth = 0

    # just simplify
    k = kp.canonical(kp.simplify_crossing_reducing(k))

    if (knot_name := innner_classify(k)) != "unknown":
        return knot_name, k

    k = kp.simplify_non_increasing(k)

    if (knot_name := innner_classify(k)) != "unknown":
        return knot_name, k

    k = kp.simplify_smart(k, depth=1, progress_bar=False)

    if (knot_name := innner_classify(k)) != "unknown":
        return knot_name, k

    # if depth == 0:
    #     print(k)
    #     k = kp.simplify_smart(k, 0, progress_bar=False)
    #     return classify(k)

    #kp.export_png(k, f"pics/{k.name}.png")

    return ("unknown", k)


def read_file_in_chunks(filename, chunk_size):
    """Generator function that reads a file and yields chunks of lines."""
    with open(filename, 'r') as file:
        while True:
            chunk = [file.readline().strip() for _ in range(chunk_size)]
            if not chunk or all(line == '' for line in chunk):
                break
            yield [c for c in chunk if c and "name" not in c]

if __name__ == "__main__":

    filename_simplified = "../data/old/tangles-simplified-0.txt"
    safe_delete_file(filename_simplified)

    CHUNK_SIZE = 512

    print(f"Starting with chunk size {CHUNK_SIZE}")

    lengths = set()

    for lines in Bar(read_file_in_chunks("../data/pds_tangles.txt", CHUNK_SIZE), total=math.ceil(1902581 / CHUNK_SIZE)):
        knots = []
        for line in lines:
            name, nc, dc, npd, dpd, inv = line.strip().split("\t")
            knots.append(kp.from_pd_notation(npd, name=f"N({name})"))
            knots.append(kp.from_pd_notation(npd, name=f"D({name})"))
            lengths.add(len(knots[-1]))


        with multiprocessing.Pool() as pool:
            # Map the process_element function to each element of the list in parallel
            #results = pool.starmap(classify, [(k, shared_diagrams) for k in knots])
            results = pool.map(make_simple, knots)

            with open(filename_simplified, "at") as f:
                for k, s in zip(knots, results):
                    f.write(k.name + ":" + s + "\n")

            #results = [classify(k) for k in knots]

    #         for (name, simplified), k in zip(results, knots):
    #             count_tangles += 1
    #
    #             #code = knot2str(simplified)
    #
    #             if name == "unknown":
    #                 # completely unclassified
    #                 count_unclassified += 1
    #                 with open(tangles_filename_unknown, "at") as f:
    #                     f.write(f"{k.name}; {describe_unknown(k)}; {kp.to_condensed_pd_notation(simplified)}\n")
    #
    #             elif "unknown" in name:
    #                 # partially unclassified
    #                 count_partially_classified += 1
    #                 with open(tangles_filename_partial, "at") as f:
    #                     f.write(f"{k.name}; {name}; {kp.to_condensed_pd_notation(simplified)}\n")
    #
    #             else:
    #                 # completely classified
    #                 count_classified += 1
    #                 with open(tangles_filename_classified, "at") as f:
    #                     f.write(f"{k.name}; {name}; {kp.to_condensed_pd_notation(simplified)}\n")
    #
    #             Bar.set_comment(f"{100 * (count_classified + count_partially_classified) / count_tangles:.1f}%")
    #
    # print(lengths)
    #
    # # LOAD LINKS
    # t = time()
    # with open("data/linkinfo_data_filt.csv") as file:
    #     lines = [line.strip() for line in file.readlines()][1:]
    #
    #     #lines = lines if limit is None else lines[:limit]
    #     lines = [(
    #         line[1:line[1:].find('}')+2],
    #         line[line.find("PD[") + 3:line.find("]]") + 1],
    #         int(line[line.find("]]") + 4:])
    #     ) for line in lines]
    # print(f"Loaded {len(lines)} links ({time() - t:.1f}s)")
    # # convert links
    # t = time()
    # # links = dict()
    # links = list()
    # for name, pd, _ in Bar(lines, comment="converting links"):
    #     # links[name] = kp.from_pd_notation(pd, name=name)
    #     links.append(kp.from_pd_notation(pd, name=name))
    # #print(f"Converted {len(lines)} links ({time() - t:.1f}s)\n")
    #
    #
    # # SIMPLIFY
    # canonical_link_diagrams = []
    # canonical_link_diagrams_min = []
    #
    # print("Simplifying")
    # num_all_knots = 0
    # num_knots = 0
    #
    # for k in Bar(links):
    #     # minimal crossing representations
    #     k_min = kp.all_minimal_crossings_simplifications(k, depth=0)
    #
    #     # minimal crossing representations of the mirror
    #     k_min_mirror = kp.all_minimal_crossings_simplifications(kp.mirror(k).copy(name=k.name+"m"), depth=0)
    #
    #     if k_min.isdisjoint(k_min_mirror):  # ignore mirror, if it is amphichiral
    #         table = [min(k_min), min(k_min_mirror)]
    #         table_all = list(k_min) + list(k_min_mirror)
    #     else:
    #         table = [min(k_min)]
    #         table_all = list(k_min)
    #
    #     num_all_knots += len(table_all)
    #     num_knots += len(table)
    #     kp.append_to_collection(save_links_filename, table, notation="cpd")
    #     kp.append_to_collection(save_links_filename_all, table_all, notation="cpd")
    #
    # print("Total links:", num_all_knots, "minimal", num_knots)

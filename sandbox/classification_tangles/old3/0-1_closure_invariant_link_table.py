import sys

sys.path.append('/home/bostjan/remote_code/knotpy')


import knotpy as kp
import multiprocessing
from knotpy.utils.multiprogressbar import Bar
import zipfile
from time import time
import os

import csv
import math
def safe_delete_file(s):
    if os.path.exists(s):
        os.remove(s)
        print("File", s, "has been deleted")

def knot2str(k):
    #turn a knot into
    return "".join(k._nodes[x][0].node + str(k._nodes[x][0].position) +
                   k._nodes[x][1].node + str(k._nodes[x][1].position) +
                   k._nodes[x][2].node + str(k._nodes[x][2].position) +
                   k._nodes[x][3].node + str(k._nodes[x][3].position) for x in sorted(k._nodes))

def append2file(filename, knots):
    with open(filename, "at") as f:
        for k in knots:
            f.write(f"{k.name}:{knot2str(k)}\n")

# def read_file_in_chunks(filename, chunk_size):
#     """Generator function that reads a file and yields chunks of lines."""
#
#     with open("data/linkinfo_data_filt.csv") as file:
#         sv_reader = csv.reader(file, delimiter=',', )
#         next(sv_reader, None) # skip header
#         rows = list(sv_reader)
#         rows = [[s.strip().replace("PD[", "").replace("]]", "]") for s in row] for row in rows]
#
#
#
#     with open(filename, 'r') as file:
#         while True:
#             chunk = [file.readline().strip() for _ in range(chunk_size)]
#             if not chunk or all(line == '' for line in chunk):
#                 break
#             yield [c for c in chunk if c and "name" not in c]


def make_diagrams(k):

    k_diagrams = kp.all_minimal_crossings_simplifications(k, depth=1, max_difference=1)

    m = kp.mirror(k.copy())
    m.name = k.name + "m"

    m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=0)
    if m_diagrams.isdisjoint(k_diagrams):
        m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=2, max_difference=1)

        if not m_diagrams.isdisjoint(k_diagrams):
            m_diagrams = set()
    else:
        m_diagrams = set()

    min_crossings_k = min(len(_) for _ in k_diagrams)
    min_crossings_m = min(len(_) for _ in m_diagrams) if m_diagrams else 0

    diagrams = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams] +
                [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams])
    diagrams_min = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams if len(k) == min_crossings_k] +
                    [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams if len(m) == min_crossings_m])

    return diagrams, diagrams_min

def chunkify(input_list, chunk_size=64):
    # Split the input list into sublists of size 'chunk_size'
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]


if __name__ == "__main__":

    save_links_filename = "data/canonical-links-2.txt"
    save_links_filename_min = "data/canonical-links-min-2.txt"

    # with open(save_links_filename_min, "rt") as f:
    #     lines = f.readlines()
    #     existing_diagrams = set([l.split(":")[0] for l in lines if "m:" not in l])
    #     lines.clear()

    safe_delete_file(save_links_filename_min)
    safe_delete_file(save_links_filename)

    with open("../data/linkinfo_data_filt.csv") as file:
        sv_reader = csv.reader(file, delimiter=',', )
        next(sv_reader, None) # skip header
        rows = list(sv_reader)
        rows = [[s.strip().replace("PD[", "").replace("]]", "]") for s in row] for row in rows]

    total_links = 0
    total_links_min = 0


    print("Simplifying links")

    # LOAD
    CHUNK_SIZE = 32
    for rws in Bar(chunkify(rows, 64), total=len(rows)//64):
        links = [kp.from_pd_notation(pd, name=name) for name, pd, _ in rws]
        #lines = [l for l in lines if l[0] not in existing_diagrams]


        with multiprocessing.Pool(processes=8) as pool:
            results = pool.map(make_diagrams, links)

        f = open(save_links_filename, "at")
        f_min = open(save_links_filename_min, "at")

        for diagrams, diagrams_min in results:
            for line in diagrams:
                f.write(line)
                total_links += 1
            for line in diagrams_min:
                f_min.write(line)
                total_links_min += 1

        f.close()
        f_min.close()

    exit()
    # t = time()
    # with open("data/PD_3-16.txt") as file:
    #     lines = [line.strip() for line in file.readlines() if "K16" not in line and "K15" not in line]
    #     lines = [(s[s.find("'") + 1:s.find("'", s.find("'") + 1)], s[s.find("'", s.find("'") + 3) + 3:-2]) for s in lines]
    #     knots = []
    #     for name, pd in Bar(lines):
    #         k = kp.from_pd_notation(pd, name=name)
    #         knots.append(kp.from_pd_notation(pd, name=name))
    #     lines.clear()
    #
    #     with multiprocessing.Pool() as pool:
    #         results = pool.map(make_diagrams, knots)
    #
    #
    # exit()
    #
    # # CONVERT
    #
    # t = time()
    # knots = list()
    # for name, pd in Bar(lines):
    #     k = kp.from_pd_notation(pd, name=name)
    #     knots.append(kp.from_pd_notation(pd, name=name))
    # #print(f"Converted {len(lines)} knots ({time() - t:.1f}s)\n")
    #
    #
    #
    # # SIMPLIFY
    # canonical_knot_diagrams = []
    # canonical_knot_diagrams_min = []
    #
    # print("Simplifying")
    # num_all_knots = 0
    # num_knots = 0
    #
    # for k in Bar(knots):
    #     # minimal crossing representations
    #     k_min = kp.all_minimal_crossings_simplifications(k, depth=1)
    #
    #     # minimal crossing representations of the mirror
    #     k_min_mirror = kp.all_minimal_crossings_simplifications(kp.mirror(k).copy(name=k.name+"m"), depth=1)
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
    #     append2file(save_knots_filename_all, table_all)
    #     #kp.append_to_collection(save_knots_filename, table, notation="cpd")
    #     #kp.append_to_collection(save_knots_filename_all, table_all, notation="cpd")
    #
    # print("Total knots:", num_all_knots, "minimal", num_knots)

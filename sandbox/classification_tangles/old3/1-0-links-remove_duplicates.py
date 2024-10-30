import sys
sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
from knotpy import Bar
import multiprocessing
from itertools import  chain
from read_input import safe_delete_file

input_links = "data/links-em.txt"
num_knots, num_links, num_tangles = 59937, 4188, 3805162

output_links = "data/canonical_links3a.txt"


def make_diagrams(k):

    k_diagrams = kp.all_minimal_crossings_simplifications(k, depth=1, max_difference=0)

    m = kp.mirror(k.copy())
    m.name = k.name + "m"

    m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=0)
    if m_diagrams.isdisjoint(k_diagrams):
        m_diagrams = kp.all_minimal_crossings_simplifications(m, depth=1, max_difference=0)

        if not m_diagrams.isdisjoint(k_diagrams):
            m_diagrams = set()
    else:
        m_diagrams = set()

    # min_crossings_k = min(len(_) for _ in k_diagrams)
    # min_crossings_m = min(len(_) for _ in m_diagrams) if m_diagrams else 0

    # diagrams = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams] +
    #             [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams])
    # diagrams_min = ([f"{k.name}:{knot2str(k)}\n" for k in k_diagrams if len(k) == min_crossings_k] +
    #                 [f"{m.name}:{knot2str(m)}\n" for m in m_diagrams if len(m) == min_crossings_m])

    return k_diagrams | m_diagrams


def get_keys_from_file(file_path):
    keys = set()

    # Open the file and read lines
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line by the colon to separate key and value
            if ':' in line:
                key, value = line.split(':', 1)  # Split at the first colon only
                keys.add(key.strip())  # Strip whitespace and add the key to the set

    return keys

if __name__ == "__main__":

    #safe_delete_file(output_knots)
    #safe_delete_file(output_links)
    #safe_delete_file(output_tangles)

    chunk_size = 24

    new_links = list()

    for link in Bar(kp.load_collection_iterator(input_links), total=num_links):

        if link not in new_links:
            new_links.append(link)


    kp.save_collection("data/old3/canonical_links3a-2.txt", new_links, notation="cem")

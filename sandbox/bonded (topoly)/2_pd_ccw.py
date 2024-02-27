"""
Load PD codes from a CSV file and exports them as a .knots file.
"""

print("loly")

import csv
# from itertools import chain, combinations
# from copy import deepcopy
#
# from knotpy import from_pd_notation, to_pd_notation
from knotpy import SpatialGraph
# import knotpy as kp

_DEBUG = True

with open('data/theta-pd-non-ccw.csv', 'r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    data = list(csv_reader)
    if _DEBUG:
        print("Loaded", len(data), "thetas.")



# just print the codes that are ok.
for count, (name, pd) in enumerate(data):
    k = from_pd_notation(pd, str, SpatialGraph)

    if _DEBUG:
        print("Converted", pd, "to", k)

    #print("PD", pd, "->", k)
    if kp.check_region_sanity(k) or len(k) <= 2:
        #print(count) #, name+",\""+pd+"\"")
        print(name+",\""+pd+"\"")
        pass
    else:
        #print("Non-realizable:", k)

        # loop through all subsets of degree 3 nodes of length > 0
        has_sane_candidate = False
        nodes3 = k.nodes(degree=3)
        L = None
        for nodes in chain(*(combinations(nodes3, i) for i in range(1, len(nodes3) + 1))):
            L = deepcopy(k)
            for node in nodes:
                kp.permute_node(L, node, list(range(len(L.nodes[node])-1, -1, -1)))

            if kp.check_region_sanity(L):
                has_sane_candidate = True
                pd_code = to_pd_notation(L)
                break

        if has_sane_candidate:
            print(name+",\""+to_pd_notation(L)+"\"")
        else:
            print("!!!"+name+",\""+to_pd_notation(L)+"\"")


        # for reverse_nodes in

        # node = "a"
        # kp.permute_node(k, node, list(range(len(k.nodes[node])-1, -1, -1)))
        # print("               ", k)

exit()

for name, pd in data:



    k = from_pd_notation(pd, int, SpatialGraph)
    nodes3 = [node for node in k.nodes if k.nodes[node].degree() == 3]
    #print(k, nodes3)

    good = False
    for reverse_nodes in [[], [nodes3[0]], [nodes3[1]], [nodes3[0], nodes3[1]]]:
        k = from_pd_notation(pd, int, SpatialGraph)
        k.name = name

        #print("   ", k)
        for n in reverse_nodes:
            k._nodes[n].reverse()
        #print("  r", k, reverse_nodes)

        sane = kp.check_region_sanity(k)
        if sane:
            #print("ok", k)
            print(kp.to_pd_notation(k))
            good = True
            break
        print("!")

    if not good:
        print("not good.")
        exit(9)


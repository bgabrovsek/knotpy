from pathlib import Path
import os
import sympy
import matplotlib.pyplot as plt
import multiprocessing
from collections import Counter

import sys


import knotpy.algorithms.topology

sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp

DATA_FOLDER = Path("../data")
input = DATA_FOLDER / "knotoids-filter-1.txt"
output = DATA_FOLDER / "knotoids-filter-1-nosums.txt"

def remove_obvious_sums(knots):
    at_lest_one_sum = False
    all_are_sums = True

    knots_that_are_not_sums = []

    for k in knots:
        is_sum = len(knotpy.algorithms.topology.bridges(k)) > 2 or kp.is_connected_sum(k)  # has three bridges (two leafs and the other one or is sum)
        at_lest_one_sum |= is_sum
        all_are_sums &= is_sum
        if not is_sum:
            knots_that_are_not_sums.append(k)
    # if all_are_sums:
    #     return "*"
    # if at_lest_one_sum:
    #     return "-"
    # return " "
    return knots_that_are_not_sums

def print_stats(filename):
    group_sizes = kp.invariant_collection_group_sizes(filename, "pdc")
    number_of_groups = sum(val for val in group_sizes.values())
    number_of_diagrams = sum(key * val for key, val in group_sizes.items())
    print(f"In {filename} there are:")
    print(f"  {number_of_groups} groups containing {number_of_diagrams} diagrams")
    print(f"  Group sizes:", " ".join([f"{x}:{y}" for x,y in sorted(group_sizes.items())]))

kp.init_collection(output,multiple_diagrams_per_line=True)

for diagrams in kp.Bar(kp.load_collection(input)):
    good_diagrams = []
    cs = False
    ds = False
    for d in diagrams:
        cs_ = kp.is_connected_sum(d)
        ds_ = kp.number_of_disjoint_components(d) > 1

        cs |= cs_
        ds |= ds_

        if not cs and not ds:
            good_diagrams.append(d)

    if good_diagrams:

        name = " ".join(["sum" if cs else "", "dis" if ds else ""])
        if not name.strip():
            name = None
        else:
            for d in good_diagrams:
                d.name = name

        kp.append_to_collection(output, good_diagrams)

    kp.append_comment(output,"done.")


        # print(s, end= "")

    # print()

exit()


exit()
print("Input:", input)

print_stats(input)

comment = "Knotoids up to 6 crossings without mirrors simplified once in parallel without sums // 9.8.2024"

header = kp.load_invariant_collection_header(input)
# save an empty file containing only comments and headers
kp.save_invariant_collection(filename=output, data=[], invariant_names=header, notation="cpd", comment=comment)

counter = 0

for diagrams, invariant in kp.load_invariant_collection_iterator(input, "cpd"):

    counter += 1
    new_diagrams = remove_obvious_sums(diagrams)

    if len(new_diagrams) == 0:
        print("#", end="" if counter % 100 else "\n")
    elif len(new_diagrams) < len(diagrams):
        print("?", end="" if counter % 100 else "\n")
    else:
        print(" ", end="" if counter % 100 else "\n")

    if new_diagrams:
        kp.append_invariant_collection(output, new_diagrams, invariant, "cpd")

print()
print_stats(output)

print("Output:", output)


"""



        #    ?                    ?               ?                ERROR PlanarDiagram with 8 nodes, 13 arcs, and adjacencies a → X(g2 g0 g3 f0), b → X(e0 c3 c1 c0), c → X(b3 b2 d0 b1), d → X(c2 h3 h1 h0), e → V(b0), f → V(a3), g → X(a1 h2 a0 a2), h → X(d3 d2 g1 d1) with framing 0
ERROR X[0,1,2,3],X[4,5,6,7],X[7,6,8,5],X[8,9,10,11],V[4],V[3],X[1,12,0,2],X[11,10,12,9]
ERROR [{'f', 'a', 'g'}, {'e', 'b', 'c'}, {'d', 'h'}]
/home/bostjan/remote_code/knotpy/knotpy/algorithms/connected_sum.py:56: UserWarning: The cut-set (frozenset({c1, d3}), frozenset({g2, h1})) contains three components.
  warnings.warn(f"The cut-set {cut_set} contains three components.")
ERROR PlanarDiagram with 8 nodes, 13 arcs, and adjacencies a → X(f0 g0 g3 g1), b → X(c3 c2 c0 e0), c → X(b2 d3 b1 b0), d → X(h3 h2 h0 c1), e → V(b3), f → V(a0), g → X(a1 a3 h1 a2), h → X(d2 g2 d1 d0) with framing 0
ERROR X[0,1,2,3],X[4,5,6,7],X[6,8,5,4],X[9,10,11,8],V[7],V[0],X[1,3,12,2],X[11,12,10,9]
ERROR [{'f', 'a', 'g'}, {'e', 'b', 'c'}, {'d', 'h'}]
#                #   # #  # # ?  
        ##    #   #      #         #      # ## #                                          #     #   
   #                                                                                #        ?      
                   ##                                          ?                                    
                                                                                                    
                                                                                                    
                                        #                                                     #     
                   #        #                # #                                                    
                                                                                                    
                                                     ?##                                            
             ?                                 ?                                                    
        ?    # #                                                                                    
/home/bostjan/remote_code/knotpy/knotpy/algorithms/connected_sum.py:56: UserWarning: The cut-set (frozenset({b3, d1}), frozenset({h2, g1})) contains three components.
  warnings.warn(f"The cut-set {cut_set} contains three components.")
                                    #   #                 ERROR PlanarDiagram with 8 nodes, 13 arcs, and adjacencies a → X(d3 d2 d0 f0), b → X(g2 g0 g3 d1), c → X(e0 h3 h1 h0), d → X(a2 b3 a1 a0), e → V(c0), f → V(a3), g → X(b1 h2 b0 b2), h → X(c3 c2 g1 c1) with framing 0
ERROR X[0,1,2,3],X[4,5,6,7],X[8,9,10,11],X[2,7,1,0],V[8],V[3],X[5,12,4,6],X[11,10,12,9]
ERROR [{'f', 'd', 'a'}, {'b', 'g'}, {'e', 'c', 'h'}]
#          #              ?               
                            #  ?                        #  #         ?                     ?  #     
             #                  #                                                  ###       
             
             
             """
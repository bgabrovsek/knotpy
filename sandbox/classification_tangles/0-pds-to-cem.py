"""
bartosz pds to cem format
name	numerator_components	denominator_components	pdcode_numerator	pdcode_denominator	invariants
1	1	1	X[2,2,1,1]	X[2,1,1,2]	X0:30727:+1/1:((0,0,-1),(0,0,0,0,-1))
!
"""
import sys
sys.path.append('/home/bostjan/Dropbox/Code/knotpy/')

import knotpy as kp

input = "data/pds_tangles.txt"
output = "data/0-tangles-canonical.csv"

num_tangles = kp.count_lines(input) - 1

kp.init_collection(output, comment="All Tangles from Bartosz, reduced, canonical")

with open(input, "rt") as f:
    header = f.readline()
    print("Header:", header)
    counter = 0
    for line in kp.Bar(f, total=num_tangles):
        line = [c.strip() for c in line.strip().split("\t")]
        dk = kp.from_pd_notation(line[3], name=f"N({line[0]})")
        nk = kp.from_pd_notation(line[4], name=f"D({line[0]})")
        #print(type(dk), type(nk))
        #dk = kp.simplify_crossing_reducing(dk)
        #nk = kp.simplify_crossing_reducing(nk)
        #print(type(dk), type(nk))
        dk = kp.canonical(dk)
        nk = kp.canonical(nk)
        #print(type(dk), type(nk), "can", nk, dk)
        #print()
        counter += 1

        kp.extend_collection(output, [dk, nk])

kp.append_comment(output,"done.")
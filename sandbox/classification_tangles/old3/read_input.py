import sys

sys.path.append('/home/bostjan/remote_code/knotpy')

import knotpy as kp
import csv
import os

def safe_delete_file(s):
    if os.path.exists(s):
        os.remove(s)
        print("File", s, "has been deleted")

def nicer_knots():

    knot_out = "data/knots-em.txt"

    result = []
    r = []

    with open("data/PD_3-16.txt") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if "K16" not in line and "K15" not in line]
        lines = [(s[s.find("'") + 1:s.find("'", s.find("'") + 1)], s[s.find("'", s.find("'") + 3) + 3:-2]) for s in
                 lines]
        for name, code in kp.Bar(lines):
            #print(code)
            k = kp.from_pd_notation(code)
            em = kp.to_condensed_em_notation(k)
            k_em = kp.from_condensed_em_notation(em)

            k_can = kp.canonical(k)
            k_can.name = name
            r.append(k_can)
            em_can = kp.to_condensed_em_notation(k_can)
            k_can_em = kp.from_condensed_em_notation(em_can)
            k_can_em_can = kp.canonical(k_can_em)

            if k != k_em:
                print(k)
                print(k_em)
                raise ValueError("EM difference")

            if k_can != k_can_em or k_can != k_can_em_can or k_can_em != k_can_em_can:
                print(k_can)
                print(k_can_em)
                print(k_can_em_can)
                raise ValueError("CAN difference")

            result.append(name+": "+em_can)

    kp.save_collection(knot_out,r,  notation="cem")



def nicer_links():

    knot_out = "data/links-em.txt"

    result = []
    r = []



    with open("data/linkinfo_data_filt.csv") as file:
        sv_reader = csv.reader(file, delimiter=',', )
        next(sv_reader, None) # skip header
        rows = list(sv_reader)
        rows = [[s.strip().replace("PD[", "").replace("]]", "]") for s in row] for row in rows]

        for name, code, _ in kp.Bar(rows):
            #print(code)
            k = kp.from_pd_notation(code)
            em = kp.to_condensed_em_notation(k)
            k_em = kp.from_condensed_em_notation(em)

            k_can = kp.canonical(k)
            k_can.name = name
            r.append(k_can)
            em_can = kp.to_condensed_em_notation(k_can)
            k_can_em = kp.from_condensed_em_notation(em_can)
            k_can_em_can = kp.canonical(k_can_em)

            if k != k_em:
                print(k)
                print(k_em)
                raise ValueError("EM difference")

            if k_can != k_can_em or k_can != k_can_em_can or k_can_em != k_can_em_can:
                print(k_can)
                print(k_can_em)
                print(k_can_em_can)
                raise ValueError("CAN difference")

            result.append(name+": "+em_can)

    kp.save_collection(knot_out,r,  notation="cem")

def nicer_tangles():
    knot_out = "data/tangles-em.txt"

    result = []
    r = []

    with open("../data/pds_tangles.txt") as f:
        lines = f.readlines()
        print(lines[0])

        lines = [line.strip().split("\t") for line in lines[1:]]

    for name, nc, dc, npd, dpd, inv in kp.Bar(lines):
        for name, code in [(f"N({name})", npd), (f"D({name})", dpd)]:
            k = kp.from_pd_notation(code)
            k_can = kp.canonical(k)
            k_can.name = name
            r.append(k_can)

    kp.save_collection(knot_out, r,  notation="cem")


if __name__ == "__main__":

    # nicer_knots()
    # nicer_links()

    nicer_tangles()
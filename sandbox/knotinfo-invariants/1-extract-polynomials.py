import csv
import gzip
import sympy
import knotpy as kp

columns = [
"Name", # 0
"PD Notation", # 1
"Unknotting Number", # 2
"Alexander", # 3
"Jones", # 4
"Conway", # 5
"Kauffman", # 6
"Symmetry Type", # 7
"Full Symmetry Group", # 8
"HOMFLY", # 9
]

header = {
}

number_of_lines = kp.count_lines("data/knotinfo_13.csv")

header = [
"Alexander polynomial",
"Jones polynomial",
"Conway polynomial",
"Kauffman polynomial",
"HOMFLYPT polynomial",
"Unknotting number",
"Symmetry",
"Symmetry group"]

output = "data/knot_invariants_up_to_13_crossings.csv"

kp.init_collection_with_invariants(output, False, "CEM",invariant_names=header,
                                   comment="Knot invariants up to 13 crossings from knotinfo")

def syp(text:str):
    # try:
    text = text.strip()
    if text:
        return sympy.sympify(text).expand()
    else:
        return None
    # except:
    #     print("\n EX")
    #     print(text)
    #     print()
    #     raise ValueError()

counter = {i:0 for i in range(14)}

with open("data/knotinfo_13.csv", 'rt') as f:
    reader = csv.reader(f)



    first_line = next(reader, None)

    for row in kp.Bar(reader, total=number_of_lines):
        try:
            pd_code = row[1].replace(";", ",")[1:-1]
            name = row[0]
            invariants = {
                "Unknotting number": row[2].replace(";",",") if ";" in row[2] else int(row[2]),
                "Alexander polynomial": syp(row[3]),
                "Jones polynomial": syp(row[4]),
                "Conway polynomial": syp(row[5]),
                "Kauffman polynomial": syp(row[6]),
                "HOMFLYPT polynomial": syp(row[9]),
                "Symmetry": row[7].strip(),
                "Symmetry group": row[8].strip(),
            }

            k = kp.from_pd_notation(pd_code, name=name)
            k = kp.canonical(k)
            counter[len(k)] += 1

            kp.append_to_collection_with_invariants(output, k, invariants)

        except:
            print("\nExcept")
            for item in row:
                print(item)

"""
{0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 3, 7: 7, 8: 21, 9: 49, 10: 165, 11: 552, 12: 2176, 13: 9988}

"""

print(counter)
"""
(""
 "['13n_4931', "
 "'[[5; 1; 6; 26]; [1; 9; 2; 8]; [11; 3; 12; 2]; [3; 19; 4; 18]; [21; 5; 22; 4]; [6; 15; 7; 16]; [14; 7; 15; 8]; [9; 21; 10; 20];
  [19; 11; 20; 10]; [23; 13; 24; 12]; [13; 25; 14; 24]; [25; 17; 26; 16]; [17; 23; 18; 22]]', 
  
  '[2;3]', 
  
  '-3+20*t-47*t^2+61*t^3-47*t^4+20*t^5-3*t^6', 
  
  '2*t^2 - 7*t^3 + 16*t^4 - 23*t^5 + 30*t^6 - 33*t^7 + 31*t^8 - 26*t^9 + 18*t^10 - 10*t^11 + 4*t^12 - t^13', 
  '-3*z^6 + 2*z^4 + 6*z^2 + 1', '', 'chiral', '0', '(5*v^6-6*v^8+3*v^10-v^12)+(2*v^4+8*v^6-8*v^8+5*v^10-v^12)*z^2+(2*v^4+2*v^6-5*v^8+3*v^10)*z^4+(-v^6-2*v^8)*z^6']

")

"""
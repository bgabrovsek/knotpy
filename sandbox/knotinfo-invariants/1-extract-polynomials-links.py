import csv
import gzip
import sympy
import knotpy as kp

"""
0 name -> L5a1{0}
22 pd_notation_math -> PD[X[6, 1, 7, 2], X[10, 7, 5, 8], X[4, 5, 1, 6], X[2, 10, 3, 9], X[8, 4, 9, 3]]
34 multivariable_alexander -> 1-t1-t2 +t1*t2
36 conway_polynomial -> z^3
38 jones_polynomial -> x^(-7)-2/x^5 + x^(-3)-2/x + x-x^3
42 homflypt_polynomial -> 1/(v*z)-v/z-z/v^3 + (2*z)/v-v*z + z^3/v
46 kauffman_polynomial -> -1 + 1/(a*z) + a/z-(2*z)/a-4*a*z-2*a^3*z-z^2 + a^4*z^2 + z^3/a + 3*a*z^3 + 2*a^3*z^3 + z^4 + a^2*z^4
50 khovanov_polynomial -> 2 + 2/q^2 + 1/(q^8*t^3) + 1/(q^6*t^2) + 1/(q^4*t^2) + 1/(q^2*t) + t + q^4*t^2
64 components -> 2
76 splitting_number -> 2
84 unlinking_number -> 1
"""

columns = [
    "Name",  # 0
    "PD Notation",  # 1
    "Multivariable Alexander",  # 2
    "Conway",  # 3
    "Jones",  # 4
    "HOMFLYPT",  # 5
    "Kauffman",  # 6
    "Khovanov",
    "Components",
    "Splitting number",
    "Unlinking number"
]

output = "data/link_invariants_up_to_11_crossings.csv"
number_of_lines = kp.count_lines("data/linkinfo_data_complete.csv")

header = [
    "Alexander",
    "Jones",
    "Conway",
    "Kauffman",
    "HOMFLYPT",
]

header = [
"Alexander",
"Jones",
"Conway",
"Kauffman",
"HOMFLYPT",
"Khovanov",
"Components",
"Splitting number",
"Unlinking number"]




kp.init_collection_with_invariants(output, False, "CEM", invariant_names=header,
                                   comment="Link invariants up to 11 crossings from knotinfo")


def syp(text: str):
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


counter = {i: 0 for i in range(14)}

def to_int(i):
    try:
        return int(i)
    except:
        return None

with open("data/linkinfo_data_complete.csv", 'rt') as f:
    reader = csv.reader(f, delimiter=";")

    first_line = next(reader, None)

    for row in kp.Bar(reader, total=number_of_lines):
        #try:
        if True:
            pd_code = row[22].replace(";", ",").replace("]]", "]").replace("PD[","").replace("X[","[")
            name = row[0]
            invariants = {
                "Alexander": syp(row[34]),
                "Jones": syp(row[38]),
                "Conway": syp(row[36]),
                "Kauffman": syp(row[46]),
                "HOMFLYPT": syp(row[42]),
                "Khovanov": syp(row[50]),
                "Components": to_int(row[64]),
                "Splitting number": to_int(row[76]),
                "Unlinking number": to_int(84)
            }
            try:
                k = kp.from_pd_notation(pd_code, name=name)
            except:
                print(name)
                print(pd_code)
                exit()
            k = kp.canonical(k)
            counter[len(k)] += 1

            kp.append_to_collection_with_invariants(output, k, invariants)

        # except:
        #     print("\nExcept")
        #     for item in row:
        #         print(item)
        #
        #     for key, item in invariants.items():
        #         print(key, "->", item)
        #
        #     print(name)
        #     print(pd_code)

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
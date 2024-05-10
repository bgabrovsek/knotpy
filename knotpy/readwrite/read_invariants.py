import csv
from sympy import symbols, sympify

from knotpy.notation.pd import from_pd_notation


def _string_to_polynomial(s):
    #chars = [char for char in s if s.isupper() or s.islower]
    #sy = symbols(" ".join(chars))  # sympy symbols
    poly = sympify(s)
    return poly

def read_invariants_from_csv(filename):
    # read data
    with open('knotinfo.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Name,PD Notation,Alexander,Jones,Conway,Kauffman,HOMFLY
        rows = [row for row in csv_reader]

    name_index = header.index("Name")

    data = {
        row[0]: {key: value for key, value in zip(header, row) if key != "Name"}
        for row in rows
    }

    # convert data to knot
    if "PD Notation" in header:
        for name, value in data.items():
            k = from_pd_notation(value["PD Notation"])
            k.name = name

            del value["PD Notation"]
            value["diagram"] = k

            for poly_name in ["Jones", "Conway", "HOMFLPY", "kauffman", "Alexander"]:
                if poly_name in header:

                    # poly to
                    poly_str = value[poly_name]
                    value[poly_name] = _string_to_polynomial(poly_str)




    return data

if __name__ == "__main__":
    data = read_invariants_from_csv("knotinfo.csv")
    for x in data:
        print(x, data[x])
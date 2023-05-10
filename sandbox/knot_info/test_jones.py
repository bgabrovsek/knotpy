import pandas
from knotpy import Knot, from_pd_notation, bracket_polynomial

df = pandas.read_excel("knotinfo_data_complete.xls")
extract = ["name", "pd_notation", "jones_polynomial"]
df = df[extract][2:]

for index, row in df.iterrows():
    name, pd_notation, jones = row

    k = from_pd_notation(pd_notation, notation_format="knotinfo")
    k.name = name

    print(name, pd_notation)
    print(k)
    b = bracket_polynomial(k)

    print()
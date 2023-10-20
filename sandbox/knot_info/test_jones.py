import pandas
from knotpy import Knot, from_pd_notation, bracket_polynomial
from time import time

df = pandas.read_excel("knotinfo_data_complete.xls")
extract = ["name", "pd_notation", "jones_polynomial"]
df = df[extract][2:]

knots = []
for index, row in df.iterrows():
    name, pd_notation, jones = row
    k = from_pd_notation(pd_notation, notation_format="knotinfo")
    k.name = name
    knots.append(k)
    if len(knots) > 140:
        break

#    if k.name[0] == "9": break

t = time()
for k in knots:
    #print("-----")
    #print(k)
    b = bracket_polynomial(k, reduce=False)
    q = bracket_polynomial(k, reduce=True)
    #print(b)
    #print(q)

    from knotpy.sanity import check

    check(k)

    assert b == q

print(time()-t)

# 0.288787841796875r
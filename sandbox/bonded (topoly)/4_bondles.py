import csv
import knotpy as kp

with open('data/theta-pd-non-ccw.csv', 'r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    data = list(csv_reader)

for count, (name, pd) in enumerate(data):
    k = kp.from_pd_notation(pd, str, kp.SpatialGraph)
    k.name = name
    print(k)




import csv
from knotpy import from_pd_notation
import knotpy as kp



with open('good-theta-pd-non-ccw.csv', 'r', newline='') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    data = list(csv_reader)

# Convert PD codes to text

knots = []
for name, pd_text in data:
    k = from_pd_notation(pd_text)
    k.name = name
    knots.append(k)

print(f"Loaded {len(knots)} knots.")
for k in knots:
    print(k)

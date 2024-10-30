import knotpy as kp
from collections import defaultdict
from knotpy import Bar
#for k in kp.load_collection_iterator("data/canonical_tangles.txt", notation="cem"):

count = 0
d = defaultdict(list)
with open("../data/old/canonical_tangles.txt", "rt") as f:
    lines = f.readlines()
    for line in Bar(lines):
        name, code = [l.strip() for l in line.split(": ")]
        d[code].append(name)

with open("../data/old/canonical_tangles_grouped.txt", "wt") as f:
    for code, names in Bar(d.items(), total=len(d)):
        f.write(f"{','.join(names)}: {code}\n")

print("All:", len(lines))
print("Unique:", len(d), f"{100*len(d)/len(lines):0.2f}%")
exit()
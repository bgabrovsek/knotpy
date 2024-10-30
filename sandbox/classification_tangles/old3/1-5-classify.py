import knotpy as kp
from collections import defaultdict
from knotpy import Bar
#for k in kp.load_collection_iterator("data/canonical_tangles.txt", notation="cem"):

count = 0

# names = set()
# with open("data/tangles-em.txt", "rt") as f:
#     for line in f:
#         if ":" in line:
#             name, code = line.strip().split(": ")
#             if name in names:
#                 print(name)
#             else:
#                 names.add(name)
#
# exit()

count = 0
not_good = 0
with open("../data/pds_tangles.txt") as f:
    for line in f:
        if "name" in line:
            continue
        count += 2
        m = line.strip().split("\t")
        if m[3].count(";") + 1 > 11:
            if int(m[2]) != 1:
                not_good +=1
            if int(m[1]) != 1:
                not_good += 1

print(not_good, count)

exit()

            # load links
links = dict()
with open("data/old3/canonical_links3a.txt", "rt") as f:
    lines = f.readlines()
    print("Loading links")
    for line in Bar(lines):
        name, code = [l.strip() for l in line.split(": ")]
        if code not in links:
            #raise ValueError(f"Duplicate code {code} with names {links[code]} and {name}")
            links[code] = name

with open("data/old3/canonical_links3b-copy.txt", "rt") as f:
    lines = f.readlines()
    print("Loading links #2")
    for line in Bar(lines):
        name, code = [l.strip() for l in line.split(": ")]
        if code in links:
            continue
        links[code] = name


# load tangles
tangles = dict()
with open("../data/old/canonical_tangles_grouped.txt", "rt") as f:
    lines = f.readlines()
    print("Loading tangles")
    for line in Bar(lines):
        name, code = [l.strip() for l in line.split(": ")]
        tangles[name] = code


# load knots
knots = dict()
with open("data/old3/canonical_knots.txt", "rt") as f:
    lines = f.readlines()
    print("Loading knots")
    for line in Bar(lines):
        name, code = [l.strip() for l in line.split(": ")]
        if code in knots:
            raise ValueError("Duplicate code")
        knots[code] = name



print("Loaded", len(tangles), "groups of tangles of", sum(s.count(",")+1 for s in tangles))
print("Loaded", len(knots), "codes of knots of", len(set(knots.values())))
print("Loaded", len(links), "codes of links of", len(set(links.values())))

replacements = 0
new_tangles = dict()
new_tangles_unknown = dict()

known = 0
unknown = 0

for names, code in tangles.items():
    if code in knots:
        new_tangles[names] = knots[code]
        known += names.count(",") + 1
    elif code in links:
        new_tangles[names] = links[code]
        known += names.count(",") + 1
    else:
        new_tangles_unknown[names] = code
        unknown += names.count(",") + 1

tangles_classification = dict()

for names, code in new_tangles.items():
    names = names.replace(",N", ";N").replace(",D",";D")
    for name in names.split(";"):
        if name not in tangles_classification:
            tangles_classification[name] = code

known2 = len(tangles_classification)

for names, code in new_tangles_unknown.items():
    names = names.replace(",N", ";N").replace(",D",";D")
    for name in names.split(";"):
        if name not in tangles_classification:
            tangles_classification[name] = code

unknown2 = len(tangles_classification) - known2

print("Known:", known2, f"{100*known2/(known2+unknown2):0.2f}%")
print("Unknown:", unknown2, f"{100*unknown2/(known2+unknown2):0.2f}%")

# with open("data/results.txt", "wt") as f:
#     pass


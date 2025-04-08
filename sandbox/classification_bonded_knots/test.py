"""
* Load diagrams from plantri,
* remove diagrams that have vertices of degree 5 or more,
* remove non-isomorphic diagrams,
* export images of diagrams to pdf
* save diagrams to a file.
"""

import knotpy as kp

diagrams = kp.load_diagrams("data/plantri-8.txt", notation="plantri")

print(f"Loaded {len(diagrams)} diagrams")

# remove graphs that have vertices with degree larger than 4
diagrams = [k for k in diagrams if max(k.degree(v) for v in k.vertices) <= 4]

print(f"Reduced to {len(diagrams)} good diagrams")

# put diagrams in canonical form and remove duplicates
unique_diagrams = set(kp.canonical(k) for k in diagrams)

print("Number of unique diagrams:", len(unique_diagrams))“
print(f"Number of diagrams that are *not* planar or are invalid:", sum(not kp.sanity_check(k) for k in unique_diagrams))

# name the diagrams, so that in the pdf, the titles correspond to the plantri notation
for k in unique_diagrams:
    k.name = kp.to_plantri_notation(k)

kp.export_pdf(unique_diagrams, "graphs.pdf", with_title=True)

print(f"Saving {len(unique_diagrams)} diagrams")

kp.save_diagrams("data/plantri-8-canonical.txt", unique_diagrams, notation="plantri")


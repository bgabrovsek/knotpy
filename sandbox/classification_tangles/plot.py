import sys
sys.path.append('/home/bostjan/Dropbox/Code/knotpy/')

import knotpy as kp

A = []
i = 0

for k in kp.Bar(kp.load_collection_iterator("data/0-tangles-canonical.csv", max_diagrams=50000), total=50000):
    i += 1
    if i % 50 == 1:
        print(kp.to_condensed_em_notation(k))
        if len(k) > 6:
            A.append(k)
            A[-1].name = kp.to_condensed_pd_notation(A[-1])

kp.export_pdf(A, "closed-t.pdf", with_title=True)
import knotpy as kp
from pathlib import Path

print(Path.cwd())
for i in range(2, 12):
    if i == 3:
        continue
    links = kp.load_invariant_table(f"links_{i}.csv.gz")
    for k, v in links.items():
        v["diagram"] = kp.canonical(v["diagram"])
    kp.save_invariant_table(f"links_{i}_canonical.csv.gz", links)
    print(len(links))

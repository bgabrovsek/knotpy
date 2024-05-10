
from pathlib import Path
import knotpy as kp


data_folder = Path("data")
txt_input_file = data_folder / 'bonded.txt'



with open(txt_input_file, 'r', newline='') as file:
    lines = file.readlines()
bonded = [kp.from_knotpy_notation(s) for s in lines]

for k in bonded:
    print(k)
    print("unplugging....")
    val = kp.unplugging(k)

    for x in val:
        print("  ", x)
        for c in kp.algorithms.disjoint_components(x):
            kp.algorithms.remove_bivalent_vertices(c, match_attributes=True)
            print("     ", c)
        #print("   ", kp.to_knotpy_notation(x))
        #print("    ", kp.algorithms.components_link.link_components_endpoints(x))

    print(k)
    break
